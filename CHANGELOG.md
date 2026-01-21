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
