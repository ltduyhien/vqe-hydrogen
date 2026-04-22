# Exact classical reference for the qubit Hamiltonian.
# Called by main.py before plotting, so we have a line to compare VQE against.
#
# FCI = Full Configuration Interaction. In our basis it is just diagonalizing
# the 2^n x 2^n Hamiltonian matrix. Fine up to ~12 qubits, impossible past that
# (that is the whole reason VQE exists).
#
# Not "exact physics" -- exact for the Hamiltonian we handed it (STO-3G +
# active space). VQE sees the same one, so the comparison is fair.

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class FCIResult:
    eigenvalue: float     # smallest eigenvalue of qubit_op, pre-shift
    energy_shift: float   # carried through from ham.energy_shift
    energy: float         # eigenvalue + shift, the number to compare


def compute_fci_reference(ham: QubitHamiltonian) -> FCIResult:
    # to_matrix() gives a dense 2^n x 2^n array. Tiny for n <= 6.
    matrix = ham.qubit_op.to_matrix()

    # eigvalsh: Hermitian input, real eigenvalues, sorted ascending.
    eigvals = np.linalg.eigvalsh(matrix)
    ground_eigenvalue = float(eigvals[0])

    total_energy = ground_eigenvalue + ham.energy_shift

    return FCIResult(
        eigenvalue=ground_eigenvalue,
        energy_shift=ham.energy_shift,
        energy=total_energy,
    )
