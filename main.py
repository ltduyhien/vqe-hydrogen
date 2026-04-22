# CLI entry point for QuantumH2.
# Runs VQE for a chosen molecule or sweeps noise, and writes plots to disk.
#
#   python main.py --molecule H2
#   python main.py --molecule LiH --optimizer COBYLA --maxiter 200
#   python main.py --molecule H2 --noise-sweep
#
# This is the only orchestrator. The other modules never import main and
# never import each other across unrelated seams.

from __future__ import annotations

import argparse
from pathlib import Path

from src.molecules import available_molecules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QuantumH2 - VQE for small hydrogen-storage molecules",
    )
    # Only required arg for now; rest land in later commits.
    parser.add_argument(
        "--molecule",
        choices=available_molecules(),
        required=True,
        help="Target molecule: H2, LiH, or BeH2.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Stub; real pipeline wired in next commit.
    print(f"(stub) molecule = {args.molecule}")


if __name__ == "__main__":
    main()
