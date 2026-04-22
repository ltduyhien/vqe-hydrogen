# The two figures from the brief:
#   (a) energy vs. iteration for one VQE run, with FCI as reference line,
#   (b) final VQE error vs. noise strength for the sweep.
#
# Energies in Hartree. If out_path is given we write to disk, otherwise show.
# CLI always writes, so runs stay reproducible and headless-safe.

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import matplotlib.pyplot as plt


def plot_convergence(
    trace: Sequence[float],     # per-iteration pre-shift energies
    energy_shift: float,        # add this to make them physical totals
    fci_energy: float,          # reference (already shifted)
    molecule_name: str,
    optimizer_name: str,
    out_path: Optional[Path] = None,
) -> None:
    # trace is <psi|qubit_op|psi>; shift it so the y-axis is physical energy.
    shifted = [x + energy_shift for x in trace]

    fig, ax = plt.subplots(figsize=(8, 5))

    # 1-indexed iterations read better than "iteration 0".
    iterations = range(1, len(shifted) + 1)

    ax.plot(
        iterations, shifted,
        marker="o", markersize=3, linewidth=1,
        label=f"VQE ({optimizer_name})",
    )
    ax.axhline(
        fci_energy, color="red", linestyle="--", linewidth=1.5,
        label=f"FCI = {fci_energy:.6f} Ha",
    )

    ax.set_xlabel("Optimizer iteration")
    ax.set_ylabel("Energy [Hartree]")
    ax.set_title(f"VQE convergence for {molecule_name}")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if out_path is None:
        plt.show()
    else:
        fig.savefig(out_path, dpi=150)
        plt.close(fig)


def plot_noise_sweep(
    noise_levels: Sequence[float],  # 2q error rates; use a small positive
                                    # floor (e.g. 1e-5) instead of 0 for the
                                    # ideal point, log axis wouldn't show it.
    errors: Sequence[float],        # matching |VQE - FCI|
    molecule_name: str,
    out_path: Optional[Path] = None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(noise_levels, errors, marker="o", linewidth=1.5)

    # Errors span several decades, log-log is the only readable scale.
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("Two-qubit gate error rate p2q")
    ax.set_ylabel("|VQE - FCI| [Hartree]")
    ax.set_title(f"VQE accuracy vs noise for {molecule_name}")

    # Chemical accuracy ~ 1.6e-3 Ha, the canonical "success" line.
    ax.axhline(
        1.6e-3, color="green", linestyle="--", linewidth=1,
        label="Chemical accuracy (1.6e-3 Ha)",
    )
    ax.legend()
    ax.grid(which="both", alpha=0.3)
    fig.tight_layout()

    if out_path is None:
        plt.show()
    else:
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
