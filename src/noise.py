# Noise models + noisy Estimator for the --noise-sweep mode.
# Only imported by main.py when the sweep runs; ideal VQE never touches this.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Single-dial parameterization: p2q is the sweep variable, everything else
# derives from it by default. Real hardware has many knobs; we deliberately
# collapse them so the sweep produces one curve, not a 3D surface.
@dataclass(frozen=True)
class NoiseParameters:
    p2q: float                        # 2-qubit depolarizing error (the knob)
    p1q: Optional[float] = None       # 1-qubit error; None -> p2q / 10
    p_readout: Optional[float] = None # readout bit-flip; None -> p2q

    def resolved_p1q(self) -> float:
        # p2q/10 roughly matches the 1q/2q ratio on IBM hardware.
        return self.p1q if self.p1q is not None else self.p2q / 10.0

    def resolved_p_readout(self) -> float:
        return self.p_readout if self.p_readout is not None else self.p2q


def build_depolarizing_noise_model(params: NoiseParameters):
    # Lazy import: qiskit_aer only needed when we actually build a model.
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

    p1 = params.resolved_p1q()
    p2 = params.p2q
    p_ro = params.resolved_p_readout()

    model = NoiseModel()

    # 1q error attached to everything the transpiler might emit for our ansatz.
    error_1q = depolarizing_error(p1, num_qubits=1)
    for gate in ("u1", "u2", "u3", "rx", "ry", "rz", "sx", "x", "h"):
        model.add_all_qubit_quantum_error(error_1q, [gate])

    # 2q error on entanglers.
    error_2q = depolarizing_error(p2, num_qubits=2)
    for gate in ("cx", "cz"):
        model.add_all_qubit_quantum_error(error_2q, [gate])

    # Symmetric bit-flip readout: rows = true state, cols = observed.
    readout_matrix = [
        [1 - p_ro, p_ro],
        [p_ro, 1 - p_ro],
    ]
    model.add_all_qubit_readout_error(ReadoutError(readout_matrix))

    return model


# Wraps the noise model in an AerEstimator so vqe_runner.run_vqe can take it
# via its estimator= kwarg -- no changes to the VQE loop itself.
def build_noisy_estimator(params: NoiseParameters, shots: int = 1024):
    from qiskit_aer.primitives import Estimator as AerEstimator

    noise_model = build_depolarizing_noise_model(params)

    # density_matrix propagates the full mixed state exactly. O(4^n) memory,
    # fine up to 6 qubits on a laptop.
    return AerEstimator(
        backend_options={
            "method": "density_matrix",
            "noise_model": noise_model,
        },
        # Finite shots so expectation values carry realistic variance.
        run_options={"shots": shots},
    )
