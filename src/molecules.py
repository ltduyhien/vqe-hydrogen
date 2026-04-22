# Molecule definitions: H2, LiH, BeH2 in STO-3G.
# Read only by hamiltonian.py; main.py picks one by name.
# No Qiskit or PySCF imports here, keep it plain data.
#
# Active space: subset of electrons/orbitals we correlate in VQE.
# Core orbitals frozen, high virtuals dropped -> fewer qubits.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ActiveSpace:
    # Electrons/orbitals kept after freezing the core.
    num_electrons: int
    num_spatial_orbitals: int
    freeze_core: bool = True


@dataclass(frozen=True)
class MoleculeSpec:
    name: str
    geometry: str          # PySCF atom string, coords in Angstrom
    basis: str
    charge: int
    spin: int              # 2S, 0 = singlet
    active_space: Optional[ActiveSpace]
    expected_qubits: int   # after parity + 2-qubit reduction


# H2: no active space needed. 2 qubits after reduction.
# 0.735 A is close enough to the equilibrium 0.7414 A.
H2 = MoleculeSpec(
    name="H2",
    geometry="H 0.0 0.0 0.0; H 0.0 0.0 0.735",
    basis="sto-3g",
    charge=0,
    spin=0,
    active_space=None,
    expected_qubits=2,
)


# LiH: freeze core, 2e in 3 orbitals -> 4 qubits after reduction.
# 1.5949 A = experimental equilibrium.
LIH = MoleculeSpec(
    name="LiH",
    geometry="Li 0.0 0.0 0.0; H 0.0 0.0 1.5949",
    basis="sto-3g",
    charge=0,
    spin=0,
    active_space=ActiveSpace(
        num_electrons=2,
        num_spatial_orbitals=3,
        freeze_core=True,
    ),
    expected_qubits=4,
)


# BeH2: linear, freeze core, 4e in 4 orbitals -> 6 qubits.
BEH2 = MoleculeSpec(
    name="BeH2",
    geometry="Be 0.0 0.0 0.0; H 0.0 0.0 1.326; H 0.0 0.0 -1.326",
    basis="sto-3g",
    charge=0,
    spin=0,
    active_space=ActiveSpace(
        num_electrons=4,
        num_spatial_orbitals=4,
        freeze_core=True,
    ),
    expected_qubits=6,
)


# Order here drives CLI help text and error messages.
_REGISTRY: dict[str, MoleculeSpec] = {
    "H2": H2,
    "LiH": LIH,
    "BeH2": BEH2,
}


def get_molecule(name: str) -> MoleculeSpec:
    # ValueError (not KeyError) so the CLI message stays readable.
    if name in _REGISTRY:
        return _REGISTRY[name]
    valid = ", ".join(_REGISTRY.keys())
    raise ValueError(f"Unknown molecule '{name}'. Expected one of: {valid}.")


def available_molecules() -> list[str]:
    return list(_REGISTRY.keys())
