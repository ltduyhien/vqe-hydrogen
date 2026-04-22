# Builds the parameterized circuit VQE optimizes over.
# Called by vqe_runner.py; main.py picks the depth via recommended_reps().
#
# Ansatz = the family of trial states VQE is allowed to search.
# We use EfficientSU2 (hardware-efficient: RY/RZ + CNOT chain).
# Shallow circuits -> survives the noise sweep and stays fast on a laptop.

from __future__ import annotations

from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import EfficientSU2


def build_ansatz(
    num_qubits: int,
    reps: int = 2,
    entanglement: str = "linear",
) -> QuantumCircuit:
    # EfficientSU2 lays down: rotation block, entangler, rotation, entangler, ...
    # "linear" = CNOT chain 0-1, 1-2, ... Cheapest pattern, good enough here.
    ansatz = EfficientSU2(
        num_qubits=num_qubits,
        reps=reps,
        entanglement=entanglement,
        insert_barriers=False,
    )
    # decompose() so the result prints as plain RY/RZ/CX instead of a blueprint.
    return ansatz.decompose()


def recommended_reps(num_qubits: int) -> int:
    # Picked by trial: H2 needs barely anything, BeH2 wants a bit more depth.
    if num_qubits <= 2:
        return 1
    if num_qubits <= 4:
        return 2
    if num_qubits <= 6:
        return 3
    return 2
