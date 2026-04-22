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
from src.plot import plot_convergence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QuantumH2 - VQE for small hydrogen-storage molecules",
    )
    parser.add_argument(
        "--molecule",
        choices=available_molecules(),
        required=True,
        help="Target molecule: H2, LiH, or BeH2.",
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # molecule -> hamiltonian -> ansatz -> VQE
    spec = get_molecule(args.molecule)
    ham = build_qubit_hamiltonian(spec)

    reps = args.reps if args.reps is not None else recommended_reps(ham.num_qubits)
    ansatz = build_ansatz(ham.num_qubits, reps=reps)

    # FCI up front so we have the reference before VQE finishes.
    fci = compute_fci_reference(ham)

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


if __name__ == "__main__":
    main()
