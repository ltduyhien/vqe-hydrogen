QuantumH2 — VQE for Hydrogen Storage Materials

A small, laptop-runnable Qiskit project that uses the Variational Quantum
Eigensolver (VQE) to estimate the electronic ground-state energy of three
molecules relevant to hydrogen-storage research:

- H₂ — 2 qubits after reduction; canonical benchmark.
- LiH — 4 qubits; appears in hydrogen-storage studies.
- BeH₂ — 6 qubits; pushes the size limit for a laptop.

Every result is compared against the exact classical answer (Full
Configuration Interaction via `NumPyMinimumEigensolver`) so the project has
a concrete, checkable success metric.

Runtime target: under 5 minutes on a laptop. No quantum hardware needed.


Why hydrogen?

- Hydrogen fuel cells are a real clean-energy technology.
- The bottleneck is finding safe, dense materials to store hydrogen.
- Designing such materials requires the ground-state energy of the
  molecules involved, which is exactly what VQE targets.
- H₂, LiH, and BeH₂ are canonical small test cases where published
  reference values exist and the problem still fits on a simulator.


What one run produces

1. A qubit Hamiltonian built from the molecule via `qiskit-nature` + PySCF.
2. An energy-vs-iteration convergence curve from the VQE loop, plotted with
   the exact FCI reference as a horizontal line.
3. A final error number (VQE energy − FCI energy) in Hartree.
4. Optionally, a noise-sweep plot showing how the final error grows with
   increasing simulated gate error.


Repository layout

```
vqe-hydrogen/
├── README.md              # this file
├── requirements.txt       # pip dependencies (install-time only)
├── .gitignore
├── main.py                # CLI entry point
└── src/
    ├── molecules.py       # geometries, basis sets, active-space config
    ├── hamiltonian.py     # molecule -> qubit Hamiltonian
    ├── ansatz.py          # parameterized circuit
    ├── fci.py             # exact reference energy (classical)
    ├── vqe_runner.py      # VQE loop + energy trace
    ├── noise.py           # qiskit-aer noise models
    └── plot.py            # convergence & noise plots
```


Install

1. Create an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```


Run

- Smallest, fastest problem:

```bash
python main.py --molecule H2
```

- Medium (still seconds on a laptop):

```bash
python main.py --molecule LiH
```

- Largest supported; a few minutes:

```bash
python main.py --molecule BeH2
```

- Noise study — sweep depolarizing error strength:

```bash
python main.py --molecule H2 --noise-sweep
```


Expected accuracy

- With a hardware-efficient ansatz of sufficient depth and COBYLA/SPSA, VQE
  should reach chemical accuracy (≈ 1.6 × 10⁻³ Hartree) relative to FCI on
  the ideal simulator for all three molecules.
- Under noise, the error grows roughly linearly with the two-qubit gate
  error rate; the noise-sweep plot makes that trend visible.


Branches

- `dev` is the active development branch; source files carry full inline
  comments.
- `main` holds the same commits as `dev` with comments stripped — the clean
  "library" view. Read `dev` to understand the code; read `main` for the
  terse version.


References

- Peruzzo et al., "A variational eigenvalue solver on a photonic quantum
  processor", Nature Communications 5, 4213 (2014).
- Kandala et al., "Hardware-efficient variational quantum eigensolver for
  small molecules and quantum magnets", Nature 549, 242–246 (2017).
- Qiskit Nature documentation: https://qiskit-community.github.io/qiskit-nature/
