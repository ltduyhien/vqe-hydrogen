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
