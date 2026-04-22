QuantumH2 - VQE for hydrogen storage materials

This project runs the Variational Quantum Eigensolver (VQE) from Qiskit
against a few small molecules that come up in hydrogen-storage research:
H2, LiH, and BeH2. Everything runs on a laptop using the qiskit-aer
simulator, so no access to real quantum hardware is needed.

Qubit counts after the usual reductions:

- H2: 2 qubits
- LiH: 4 qubits
- BeH2: 6 qubits (this is where the simulator starts to slow down)

For each molecule the VQE energy is compared against the exact answer from
Full Configuration Interaction, computed by `NumPyMinimumEigensolver`, so
there is a real number to check against instead of just "it converged".


Why bother

Hydrogen fuel cells already work, the hard part is finding materials that
store hydrogen safely and at useful densities. Designing those materials
means computing accurate electronic energies, which is where classical
methods get expensive. VQE is one of the near-term quantum algorithms
people try on this class of problem, and H2 / LiH / BeH2 are the usual
small test cases: published reference numbers exist, and the problems
still fit on a simulator.


What a run produces

One invocation of `main.py` does the following:

1. Builds a qubit Hamiltonian for the chosen molecule using
   `qiskit-nature`, with PySCF doing the classical integrals under the
   hood.
2. Runs VQE and records the energy at every optimizer iteration.
3. Plots energy vs. iteration with the exact FCI energy drawn as a
   horizontal reference line.
4. Prints the final error, i.e. VQE energy minus FCI energy, in Hartree.
5. If `--noise-sweep` is passed, repeats the run with a qiskit-aer noise
   model at several gate-error levels and plots error vs. noise.


Layout

```
vqe-hydrogen/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
└── src/
    ├── molecules.py
    ├── hamiltonian.py
    ├── ansatz.py
    ├── fci.py
    ├── vqe_runner.py
    ├── noise.py
    └── plot.py
```


Install

Use a virtualenv so you don't pollute system Python:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

PySCF compiles native code on first install, so you need a working C and
Fortran toolchain:

- macOS: `xcode-select --install` (gives clang + gfortran via Homebrew if
  needed).
- Debian / Ubuntu: `sudo apt install build-essential gfortran libopenblas-dev`.
- If the install fails on PySCF, it is almost always a missing compiler,
  not a Python problem.


Run

```bash
python main.py --molecule H2
python main.py --molecule LiH
python main.py --molecule BeH2
python main.py --molecule H2 --noise-sweep
```

H2 finishes in a few seconds. LiH is slower. BeH2 is the slowest and can
take a few minutes. The noise sweep runs the whole VQE loop several
times, so it is the most expensive option.


Accuracy

On the ideal simulator, a hardware-efficient ansatz with enough depth plus
COBYLA or SPSA reaches chemical accuracy (about 1.6e-3 Hartree) for all
three molecules. With noise on, the final error grows roughly with the
two-qubit gate error rate; the noise-sweep plot makes that visible.


References

- Peruzzo et al., A variational eigenvalue solver on a photonic quantum
  processor, Nature Communications 5, 4213 (2014).
- Kandala et al., Hardware-efficient variational quantum eigensolver for
  small molecules and quantum magnets, Nature 549, 242-246 (2017).
- Qiskit Nature: https://qiskit-community.github.io/qiskit-nature/
