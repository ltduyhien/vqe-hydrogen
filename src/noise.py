# Noise models + noisy Estimator for the --noise-sweep mode.
# Only imported by main.py when the sweep runs; ideal VQE never touches this.
#
# TODO (next commits): depolarizing model, build_noisy_estimator.

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
