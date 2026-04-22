# CLI entry point for QuantumH2.
# Runs VQE for a chosen molecule or sweeps noise, and writes plots to disk.
#
#   python main.py --molecule H2
#   python main.py --molecule LiH --optimizer COBYLA --maxiter 200
#   python main.py --molecule H2 --noise-sweep
#
# This is the only orchestrator. The other modules never import main and
# never import each other across unrelated seams.

from __future__ import annotations

import argparse
from pathlib import Path

from src.molecules import available_molecules, get_molecule
from src.hamiltonian import build_qubit_hamiltonian
from src.ansatz import build_ansatz, recommended_reps
from src.fci import compute_fci_reference
from src.vqe_runner import run_vqe
from src.plot import plot_convergence, plot_noise_sweep


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description=(
            "QuantumH2: ground-state VQE for small hydrogen-storage "
            "molecules (H2, LiH, BeH2) on the qiskit-aer simulator."
        ),
        epilog=(
            "Examples:\n"
            "  python main.py --molecule H2\n"
            "  python main.py --molecule LiH --optimizer COBYLA --maxiter 200\n"
            "  python main.py --molecule H2 --noise-sweep"
        ),
        # RawDescriptionHelpFormatter keeps the epilog newlines intact.
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--molecule",
        choices=available_molecules(),
        required=True,
        metavar="{H2,LiH,BeH2}",
        help="Target molecule. H2 is the fastest; BeH2 the slowest.",
    )
    # COBYLA is best on ideal, SPSA under noise.
    parser.add_argument(
        "--optimizer",
        choices=["COBYLA", "SPSA"],
        default="COBYLA",
        help="Classical optimizer driving the VQE loop.",
    )
    parser.add_argument(
        "--reps",
        type=int,
        default=None,
        help="Ansatz repetitions (default: auto from qubit count).",
    )
    parser.add_argument(
        "--maxiter",
        type=int,
        default=200,
        help="Maximum optimizer iterations.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for the initial parameter vector.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for output plots.",
    )
    # Flips to sweep mode. Always uses SPSA because COBYLA hates shot noise.
    parser.add_argument(
        "--noise-sweep",
        action="store_true",
        help="Sweep the two-qubit gate error rate and plot |VQE-FCI| vs noise.",
    )
    return parser.parse_args()


def run_single(args, ham, ansatz, fci) -> None:
    result = run_vqe(
        ham=ham,
        ansatz=ansatz,
        optimizer_name=args.optimizer,
        maxiter=args.maxiter,
        seed=args.seed,
    )

    # Chemical accuracy ~ 1.6e-3 Ha is the usual VQE pass/fail line.
    gap = result.energy - fci.energy
    pass_flag = "PASS (chemical accuracy)" if abs(gap) < 1.6e-3 else "above chemical accuracy"
    print(f"Molecule:        {args.molecule}")
    print(f"Optimizer:       {args.optimizer}")
    print(f"Iterations:      {result.num_iterations}")
    print(f"VQE energy:      {result.energy:.6f} Hartree")
    print(f"FCI energy:      {fci.energy:.6f} Hartree")
    print(f"VQE - FCI:       {gap:+.6f} Hartree   [{pass_flag}]")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = args.output_dir / f"convergence_{args.molecule}_{args.optimizer}.png"
    plot_convergence(
        trace=result.trace,
        energy_shift=ham.energy_shift,
        fci_energy=fci.energy,
        molecule_name=args.molecule,
        optimizer_name=args.optimizer,
        out_path=plot_path,
    )
    print(f"Plot saved to:   {plot_path}")


def run_noise_sweep(args, ham, ansatz, fci) -> None:
    # Local import: noise.py pulls qiskit_aer, only needed on this path.
    from src.noise import NoiseParameters, build_noisy_estimator

    # Log-spaced: ideal through NISQ-realistic through very noisy.
    noise_levels = [0.0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]
    errors = []

    for p in noise_levels:
        print(f"Running VQE at p2q={p}...")

        # p=0 -> ideal Estimator; anything else -> noisy AerEstimator.
        if p == 0.0:
            estimator = None
        else:
            estimator = build_noisy_estimator(NoiseParameters(p2q=p), shots=1024)

        result = run_vqe(
            ham=ham,
            ansatz=ansatz,
            optimizer_name="SPSA",
            maxiter=args.maxiter,
            seed=args.seed,
            estimator=estimator,
        )

        gap = abs(result.energy - fci.energy)
        errors.append(gap)
        print(f"  energy={result.energy:.6f} Ha, |VQE-FCI|={gap:.2e} Ha")

    # Log-x choke on 0.0; nudge to a tiny positive number for plotting.
    plot_levels = [max(p, 1e-5) for p in noise_levels]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = args.output_dir / f"noise_sweep_{args.molecule}.png"
    plot_noise_sweep(
        noise_levels=plot_levels,
        errors=errors,
        molecule_name=args.molecule,
        out_path=plot_path,
    )
    print(f"Noise sweep plot: {plot_path}")


def main() -> None:
    args = parse_args()

    # Shared setup: molecule -> hamiltonian -> ansatz -> FCI,
    # then dispatch to single or sweep.
    spec = get_molecule(args.molecule)
    ham = build_qubit_hamiltonian(spec)
    reps = args.reps if args.reps is not None else recommended_reps(ham.num_qubits)
    ansatz = build_ansatz(ham.num_qubits, reps=reps)
    fci = compute_fci_reference(ham)

    if args.noise_sweep:
        run_noise_sweep(args, ham, ansatz, fci)
    else:
        run_single(args, ham, ansatz, fci)


if __name__ == "__main__":
    main()
