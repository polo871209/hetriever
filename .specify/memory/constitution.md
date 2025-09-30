# Hetriever Constitution

<!--
SYNC IMPACT REPORT
==================
Version: 0.0.0 → 1.0.0 (MAJOR: Initial ratification)

Principles Defined:
- I. Code Quality Standards
- II. User Experience Consistency
- III. Performance Requirements
- IV. Python & Tooling Standards
- V. Minimal Dependencies

Sections Added:
- Core Principles (5 principles)
- Development Standards
- Quality Gates
- Governance

Templates Status:
✅ plan-template.md - Constitution Check section references validated
✅ spec-template.md - Requirements alignment confirmed
✅ tasks-template.md - Task categorization aligned with principles
⚠️  README.md - Empty, no updates needed yet

Follow-up TODOs: None
-->

## Core Principles

### I. Code Quality Standards
Code MUST be well-structured, concise, and maintainable. Every module MUST have a single, clear purpose with minimal coupling. Code MUST NOT include inline comments unless documenting complex algorithms or non-obvious business logic. Code MUST NOT include print statements or emoji characters. All logging MUST use Python's standard logging module with appropriate levels.

**Rationale**: Clean, self-documenting code reduces cognitive load and maintenance burden. Structured logging enables production debugging without cluttering source code.

### II. User Experience Consistency
All user-facing interfaces MUST provide consistent interaction patterns. CLI tools MUST accept input via arguments/stdin and return output via stdout, with errors directed to stderr. Output formats MUST support both human-readable and machine-parseable (JSON) modes. Error messages MUST be actionable and include context.

**Rationale**: Consistency enables composition, scripting, and reliable automation. Users can predict behavior and chain tools effectively.

### III. Performance Requirements
All operations MUST complete within defined performance budgets appropriate to their scope. API endpoints MUST respond within 200ms p95 latency. Data processing MUST handle at least 10,000 records/second. Memory usage MUST remain below 512MB for typical workloads. Performance regressions MUST be caught in CI via automated benchmarks.

**Rationale**: Performance is a feature. Proactive measurement prevents degradation and ensures scalability as the system grows.

### IV. Python & Tooling Standards
All code MUST use Python 3.13 syntax and features. Dependencies MUST be managed via `uv`. Code MUST use modern Python idioms (pattern matching, structural pattern matching, type hints with PEP 695 syntax, exception groups). Type annotations MUST cover all public APIs. Code MUST pass `ruff` linting and formatting checks.

**Rationale**: Latest syntax provides better performance, clarity, and type safety. Consistent tooling reduces friction and ensures reproducible builds.

### V. Minimal Dependencies
External dependencies MUST be justified by significant value and MUST NOT duplicate standard library functionality. Each new dependency MUST be documented with rationale in the project's dependency review log. Prefer batteries-included standard library solutions over third-party packages when functionality overlaps by >80%.

**Rationale**: Fewer dependencies reduce supply chain risk, maintenance burden, and build complexity. Standard library code has stability guarantees.

## Development Standards

All features MUST follow Test-Driven Development: write failing tests, get approval, then implement. Integration tests MUST cover all public contracts and inter-module communication. New libraries MUST be independently testable with contract tests before integration.

Code reviews MUST verify constitutional compliance before merge. All code MUST pass type checking (`mypy` or `pyright`), linting (`ruff check`), formatting (`ruff format --check`), and test suites (unit + integration).

Documentation MUST be maintained inline with code changes. Public APIs MUST include docstrings following Google or NumPy style. Breaking changes MUST follow semantic versioning with migration guides.

## Quality Gates

**Pre-Commit Gates**:
- Type checking passes without errors
- Linting produces zero violations
- Code formatting matches project style
- No print statements or emoji in source
- All tests pass (unit + integration)

**Pre-Merge Gates**:
- All quality gates pass
- Constitution compliance verified
- Performance benchmarks within budget
- Test coverage maintains or improves baseline
- Documentation updated for user-facing changes

**Release Gates**:
- All pre-merge gates pass
- Integration tests pass against production-like environment
- Performance validated under expected load
- Security scan shows no critical vulnerabilities
- Changelog and migration guide updated

## Governance

This constitution supersedes all other development practices. Amendments require documented rationale, approval from project maintainers, and a migration plan for non-compliant code.

All pull requests MUST demonstrate constitutional compliance. Deviations MUST be explicitly justified in PR description with alternatives considered. Complexity that violates principles MUST be reduced or justified with concrete evidence of necessity.

Semantic versioning applies to this constitution:
- **MAJOR**: Principle removal, incompatible governance changes
- **MINOR**: New principle, expanded guidance, new quality gates
- **PATCH**: Clarifications, wording improvements, typo fixes

Constitutional reviews occur quarterly or when significant architectural decisions arise. The review assesses whether principles remain relevant and whether the codebase complies.

**Version**: 1.0.0 | **Ratified**: 2025-09-30 | **Last Amended**: 2025-09-30
