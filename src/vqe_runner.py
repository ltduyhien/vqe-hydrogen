# The VQE loop itself.
# Takes the Hamiltonian + ansatz, runs a classical optimizer, records the energy
# at every step so plot.py can draw the convergence curve.
#
# VQE = hybrid loop: optimizer proposes theta, estimator evaluates <psi(theta)|H|psi(theta)>,
# optimizer consumes the scalar, repeats. The two halves only meet at that number.
#
# `estimator` is a parameter on purpose: default is the ideal statevector
# Estimator, the noise sweep in main.py swaps in a noisy AerEstimator.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Estimator, BaseEstimator
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA, SPSA

from src.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class VQEResult:
    eigenvalue: float        # final <psi|H|psi>, pre-shift
    energy_shift: float      # carried through
    energy: float            # eigenvalue + shift, the headline number
    trace: list[float]       # per-callback energies, pre-shift
    optimal_params: list[float]
    num_iterations: int
    optimizer_name: str


def run_vqe(
    ham: QubitHamiltonian,
    ansatz: QuantumCircuit,
    optimizer_name: str = "COBYLA",
    maxiter: int = 200,
    estimator: Optional[BaseEstimator] = None,
    seed: int = 42,
) -> VQEResult:
    # Ansatz and Hamiltonian have to agree, otherwise you assembled for the wrong molecule.
    assert ansatz.num_qubits == ham.num_qubits, (
        f"Ansatz has {ansatz.num_qubits} qubits but Hamiltonian expects "
        f"{ham.num_qubits}. Check ansatz.build_ansatz(num_qubits=...)."
    )

    if estimator is None:
        estimator = Estimator()

    name = optimizer_name.upper()

    # COBYLA: fast on ideal, brittle under noise.
    # SPSA: slower on ideal, robust under noise. -> noise sweep uses SPSA.
    if name == "COBYLA":
        optimizer = COBYLA(maxiter=maxiter)
    elif name == "SPSA":
        optimizer = SPSA(maxiter=maxiter)
    else:
        raise ValueError(
            f"Unsupported optimizer '{optimizer_name}'. Expected one of: COBYLA, SPSA."
        )

    # Small random start around 0; breaks symmetry without leaving the near-identity region.
    # Fixed seed so benchmarks are reproducible.
    rng = np.random.default_rng(seed)
    initial_point = rng.uniform(low=-0.1, high=0.1, size=ansatz.num_parameters)

    # Closure, not a global, so tests can call run_vqe repeatedly.
    trace: list[float] = []

    def _callback(eval_count: int, params: np.ndarray, value: float, metadata: dict) -> None:
        # float() avoids stray numpy scalars leaking into the trace.
        trace.append(float(value))

    vqe = VQE(
        estimator=estimator,
        ansatz=ansatz,
        optimizer=optimizer,
        initial_point=initial_point,
        callback=_callback,
    )

    result = vqe.compute_minimum_eigenvalue(operator=ham.qubit_op)

    # eigenvalue is complex with a tiny imag part from FP noise; take real.
    eigenvalue = float(result.eigenvalue.real)
    total_energy = eigenvalue + ham.energy_shift
    optimal_params = [float(x) for x in result.optimal_point]

    return VQEResult(
        eigenvalue=eigenvalue,
        energy_shift=ham.energy_shift,
        energy=total_energy,
        trace=trace,
        optimal_params=optimal_params,
        num_iterations=len(trace),
        optimizer_name=name,
    )
