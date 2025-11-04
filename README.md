QuantumH2 — VQE for Hydrogen Storage Materials

A small, laptop-runnable Qiskit project that uses the Variational Quantum
Eigensolver (VQE) to estimate the electronic ground-state energy of three
molecules relevant to hydrogen-storage research:

- H₂ — 2 qubits after reduction; canonical benchmark.
- LiH — 4 qubits; appears in hydrogen-storage studies.
- BeH₂ — 6 qubits; pushes the size limit for a laptop.

Every result is compared against the exact classical answer (Full
Configuration Interaction via `NumPyMinimumEigensolver`) so the project has a
concrete, checkable success metric.


Why this project exists

- Hydrogen fuel cells are a real clean-energy technology.
- The practical bottleneck is finding safe, dense materials to store hydrogen.
- Designing such materials requires the ground-state energy of the molecules
  involved.
- On classical hardware those calculations scale badly; VQE is the
  prototypical near-term quantum algorithm that targets them.
- H₂, LiH, and BeH₂ are the canonical small test cases where published
  reference values exist and the problem still fits on a simulator.


What the project actually does

One run of the program performs these steps, in order:

1. Build the molecule — geometry + basis set defined in `src/molecules.py`.
2. Classical chemistry step — PySCF (via `qiskit-nature`) computes the one-
   and two-electron integrals and produces a second-quantized Hamiltonian.
3. Fermion → qubit mapping — Jordan-Wigner or parity mapping turns the
   fermionic operator into a qubit operator. For H₂, a two-qubit reduction
   exploits Z₂ symmetries so the final problem lives on 2 qubits.
4. Ansatz construction — a hardware-efficient parameterized circuit
   (`EfficientSU2`-style) with enough expressibility for the target molecule.
5. VQE loop — a Qiskit `Estimator` evaluates ⟨ψ(θ)|H|ψ(θ)⟩; a classical
   optimizer (COBYLA or SPSA) updates θ; the energy trace is recorded per
   iteration.
6. Exact reference — `NumPyMinimumEigensolver` diagonalizes the qubit
   Hamiltonian directly; this is the ground-truth number VQE must approach.
7. Noise study (optional) — the same loop is re-run with a `qiskit-aer`
   noise model at several error strengths, showing how the final energy
   drifts away from the exact value.
8. Plots — two figures are produced:
   - energy vs. iteration (with the FCI reference line);
   - final error vs. noise strength.

Runtime target: under 5 minutes on a laptop. No quantum hardware needed.


Repository layout

```
vqe-hydrogen/
├── README.md              # this file
├── requirements.txt       # pip dependencies (install-time only)
├── .gitignore
├── main.py                # CLI entry point; the ONLY orchestrator
└── src/
    ├── molecules.py       # geometries, basis sets, active-space config
    ├── hamiltonian.py     # molecule -> qubit Hamiltonian
    ├── ansatz.py          # parameterized circuit
    ├── fci.py             # exact reference energy (classical)
    ├── vqe_runner.py      # VQE loop + energy trace
    ├── noise.py           # qiskit-aer noise models
    └── plot.py            # convergence & noise plots
```


How the modules connect

- `main.py` is the only module that imports from the others; data flows in
  one direction.
- `molecules.py` feeds `hamiltonian.py`.
- `hamiltonian.py` and `ansatz.py` feed `vqe_runner.py`.
- `noise.py` optionally feeds `vqe_runner.py` (swaps the ideal estimator for
  a noisy one).
- `fci.py` feeds `plot.py` as the reference line.
- `vqe_runner.py` feeds `plot.py` with the energy trace.
- No module below `main.py` imports another one except as a data source;
  `ansatz.py` does not know what molecule is being solved, `vqe_runner.py`
  does not know how the Hamiltonian was built, and so on.


Build-time vs. runtime

- Build/install time (`pip install -r requirements.txt`): pulls Qiskit,
  qiskit-nature, qiskit-aer, PySCF, numpy, scipy, matplotlib. No project
  code runs.
- Runtime (`python main.py ...`): everything in the "What the project
  actually does" section happens in one process. There is no server, no
  generated code, no daemon.


Install

1. Create an isolated environment so system Python stays clean:

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

3. Optional but recommended — freeze the exact versions you got so future
   clones are bit-for-bit reproducible:

```bash
pip freeze > requirements.lock
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

The CLI flags are finalised in `main.py` (step 10 of the build); the list
above describes the intended usage.


Expected accuracy

- With a hardware-efficient ansatz of sufficient depth and COBYLA/SPSA, VQE
  should reach chemical accuracy (≈ 1.6 × 10⁻³ Hartree) relative to FCI on
  the ideal simulator for all three molecules.
- Under noise, the error grows roughly linearly with the two-qubit gate
  error rate; the noise-sweep plot makes that trend visible.


Branching policy

This repo uses two long-lived branches and a strict, asymmetric workflow:

- `dev` — the working branch. Every source file carries full inline
  comments explaining syntax, purpose, and design decisions. All real edits
  happen here. `dev` is the source of truth.
- `main` — a derived branch. It holds the same commits with the same commit
  messages as `dev`, but with all comments stripped from the code. `main`
  is never edited directly; it is only produced by merging `dev` into it
  and then running the comment-stripping step.

Enforced by the "commit to main" workflow:

1. Check out `main`.
2. Merge `dev` into `main`.
3. Strip all comments from the merged files.
4. Commit the stripped result on `main`.
5. Switch back to `dev`. `dev` is never amended or rewritten.

Read `dev` if you want to understand why each line is there. Read `main`
if you want the clean library view.


References

- Peruzzo et al., "A variational eigenvalue solver on a photonic quantum
  processor", Nature Communications 5, 4213 (2014).
- Kandala et al., "Hardware-efficient variational quantum eigensolver for
  small molecules and quantum magnets", Nature 549, 242–246 (2017).
- Qiskit Nature documentation: https://qiskit-community.github.io/qiskit-nature/
- Remote repo: https://github.com/ltduyhien/vqe-hydrogen
