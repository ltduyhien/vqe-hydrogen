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
