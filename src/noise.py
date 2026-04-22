# Noise models + noisy Estimator for the --noise-sweep mode.
# Only imported by main.py when the sweep runs; ideal VQE never touches this.
#
# TODO (next commits): NoiseParameters, depolarizing model, build_noisy_estimator.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
