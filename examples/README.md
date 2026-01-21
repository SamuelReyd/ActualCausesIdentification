# Examples

This folder contains small, runnable scripts demonstrating how to use **actualcauses**.

## Quick start

From the repository root:

```bash
python -m pip install -e .
python examples/00_quickstart.py
```

If you installed from PyPI:

```bash
python -m pip install actualcauses
python examples/00_quickstart.py
```

## What you’ll find here

`quickstart.py`
Minimal end-to-end run: imports the suzzy example scm from the module and runs the identification.

`custom_scm.py`
Shows how to implement a custom basic SCM to identify actual causes.

`custom_heuristic.py`
Shows how to use different heuristics with a given system model and SCM.

`vectorized_system_model.py`
Shows how to use the BaseNumpyModel class to accelerate cause identification by vectorizing the intervention evaluations.

`stochastic_system_model.py`
Demonstrates noisy/stochastic evaluation using a naive average estimator and the LUCB estimator.

These examples are designed to be read and modified. 

## Correspondence with the paper

Some scripts correspond to examples from the accompanying research paper. Report to the paper and to the dedicated [GitHub repository](https://github.com/SamuelReyd/SearchingForCauses) for additional examples. 