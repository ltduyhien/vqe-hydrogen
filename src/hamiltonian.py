# MoleculeSpec -> qubit Hamiltonian.
# Runs PySCF for integrals, then maps fermions to Paulis (parity + 2-qubit reduction).
# Called once per run by main.py; consumed by fci.py and vqe_runner.py.
#
# Hamiltonian: operator whose lowest eigenvalue is the ground-state energy.
# VQE's whole job is finding that minimum for qubit_op below.

from __future__ import annotations

from dataclasses import dataclass

from qiskit.quantum_info import SparsePauliOp

from src.molecules import MoleculeSpec


@dataclass(frozen=True)
class QubitHamiltonian:
    qubit_op: SparsePauliOp
    num_qubits: int
    num_particles: tuple[int, int]   # (alpha, beta) in the active space
    energy_shift: float              # Hartree; add to any eigenvalue for total energy.
                                     # VQE itself never sees this (it only reads qubit_op),
                                     # keeping it separate avoids double-counting downstream.


def build_qubit_hamiltonian(spec: MoleculeSpec) -> QubitHamiltonian:
    # Lazy imports so `import hamiltonian` does not require PySCF installed.
    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.mappers import ParityMapper
    from qiskit_nature.second_q.transformers import (
        ActiveSpaceTransformer,
        FreezeCoreTransformer,
    )
    from qiskit_nature.units import DistanceUnit

    driver = PySCFDriver(
        atom=spec.geometry,
        basis=spec.basis,
        charge=spec.charge,
        spin=spec.spin,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()

    # Order matters: freeze core first, then cut to the active window.
    if spec.active_space is not None:
        if spec.active_space.freeze_core:
            problem = FreezeCoreTransformer().transform(problem)
        problem = ActiveSpaceTransformer(
            num_electrons=spec.active_space.num_electrons,
            num_spatial_orbitals=spec.active_space.num_spatial_orbitals,
        ).transform(problem)

    fermionic_op = problem.hamiltonian.second_q_op()

    # Passing num_particles triggers the 2-qubit reduction.
    mapper = ParityMapper(num_particles=problem.num_particles)
    qubit_op = mapper.map(fermionic_op)

    # constants already includes nuclear repulsion + transformer shifts.
    # Do not add nuclear_repulsion_energy separately, it would double-count.
    energy_shift = float(sum(problem.hamiltonian.constants.values()))

    # Guard against drift between molecules.py and the mapper.
    assert qubit_op.num_qubits == spec.expected_qubits, (
        f"Qubit-count mismatch for {spec.name}: "
        f"expected {spec.expected_qubits}, got {qubit_op.num_qubits}. "
        "Check the active-space config in src/molecules.py."
    )

    return QubitHamiltonian(
        qubit_op=qubit_op,
        num_qubits=qubit_op.num_qubits,
        num_particles=problem.num_particles,
        energy_shift=energy_shift,
    )
