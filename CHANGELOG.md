# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**, and this project follows **Semantic Versioning**.

## [Unreleased]

### Added
- 

### Changed
- Update README for v1.0.0 API / SCM + SystemModel changes

### Fixed
- 

---

## [1.0.2] - 2026-06-22

### Fixed

- **ISI – `check_memory` replaced by correct `covers()` predicate.**
  The previous implementation tested only exact equality between constraint
  tuples, so the queue grew unboundedly and many redundant sub-searches were
  executed.  The new `covers(K_ref, K)` function correctly decides whether the
  search space of `K` is already subsumed by a previously visited constraint
  `K_ref`, mirroring the theoretical subsumption criterion.  Queue entries
  already dominated by a newly added constraint are also pruned proactively.

### Added

- **ISI – approximation / backtracking controls.**
  `iterative_identification` now accepts two optional keyword arguments:
  - `max_backtrack` (int, default -1 = unlimited): stops backtracking after
    this many levels.
  - `sample_backtrack` (int, default -1 = disabled): at each level, retains
    only this many randomly sampled next constraints instead of the full set,
    enabling a controllable speed/completeness trade-off.
  Progress is reported via `tqdm` when `verbose=1`.

- **ISI – pre-built children dict for graph traversal.**
  `desc()` and `expand()` now receive a pre-built `CH` dictionary (mapping
  each variable to its children) rather than recomputing children from `PA`
  on every call, giving a meaningful speedup on large DAGs.

- **SCM - added save/load functions.**
  New functions created `save(path)` and `SCM.load(path)` to save/load an SCM state, params and identified causes.
  `find_causes()` now receive a `save_path` argument to save the identification result as it arrives.

- **SCM - added option to set target variable.**
  `SCM.__init__()` now receive a `target` argument that set the id of the target variable.

---

## [1.0.0] - 2026-01-21

This release accompanies the first official journal submission of the paper describing the package.

### Added
- Introduced an explicit `SCM` class (replacing the previous “dictionary-of-data” representation).
- Introduced an explicit **system model** abstraction/class (replacing the previous use of a generic Python function as the system model/oracle interface).

### Changed
- Updated the ISI algorithm to reflect revisions between the preprint and the current journal-submission version of the paper.
- Updated the LUCB algorithm to reflect revisions between the preprint and the current journal-submission version of the paper.

### Fixed
- Packaging and project-structure robustness improvements (e.g., `src/` layout configuration, test/CI reliability) and general cleanup.


## [0.3] - 2025-07-04

### Added
- Initial public release on PyPI.
