
# Implementation Plan: Hugo Documentation Retriever

**Branch**: `001-hetriever-stands-for` | **Date**: 2025-09-30 | **Spec**: /Users/polo/app/hetriever/specs/001-hetriever-stands-for/spec.md
**Input**: Feature specification from `/specs/001-hetriever-stands-for/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
System to fetch Hugo documentation from GitHub repositories, clean Hugo-specific syntax, generate vector embeddings, and store in ChromaDB for semantic retrieval by LLMs. Provides fresh, searchable documentation to replace outdated training data.

## Technical Context
**Language/Version**: Python 3.13  
**Primary Dependencies**: chromadb (PersistentClient), uv (package management), justfile (build automation)  
**Storage**: ChromaDB (PersistentClient in current directory)  
**Testing**: pytest with contract, integration, and unit test layers  
**Target Platform**: CLI tool, cross-platform (Linux/macOS/Windows)  
**Project Type**: single (CLI application with library components)  
**Performance Goals**: Process 10,000 documentation lines/second, embed chunks with <2s latency per batch  
**Constraints**: <512MB memory usage, ChromaDB data persisted locally, no external API dependencies  
**Scale/Scope**: Support multiple documentation repositories, handle 100K+ documentation chunks  
**User-Provided Details**: Use Python 3.13 with ChromaDB library, use justfile for build scripts without unnecessary echo statements, ChromaDB data should use PersistentClient and store in current directory

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Code Quality Standards**
- [ ] All modules have single, clear purpose with minimal coupling
- [ ] No inline comments except for complex algorithms/business logic
- [ ] No print statements or emoji characters
- [ ] All logging uses Python's standard logging module with appropriate levels

**II. User Experience Consistency**
- [ ] CLI accepts input via arguments/stdin, output via stdout, errors via stderr
- [ ] Output supports both human-readable and JSON formats
- [ ] Error messages are actionable and include context

**III. Performance Requirements**
- [ ] Operations complete within defined performance budgets
- [ ] Data processing handles ≥10,000 records/second
- [ ] Memory usage remains below 512MB for typical workloads
- [ ] Performance regressions caught in CI via automated benchmarks

**IV. Python & Tooling Standards**
- [ ] Uses Python 3.13 syntax and features
- [ ] Dependencies managed via uv
- [ ] Uses modern Python idioms (pattern matching, type hints with PEP 695, exception groups)
- [ ] Type annotations cover all public APIs
- [ ] Code passes ruff linting and formatting checks

**V. Minimal Dependencies**
- [ ] External dependencies justified by significant value
- [ ] No duplication of standard library functionality (>80% overlap)
- [ ] New dependencies documented with rationale

**Development Standards**
- [ ] TDD approach: failing tests before implementation
- [ ] Integration tests cover all public contracts
- [ ] New libraries independently testable with contract tests
- [ ] Public APIs include docstrings (Google or NumPy style)

**Quality Gates - Pre-Commit**
- [ ] Type checking passes without errors
- [ ] Linting produces zero violations
- [ ] Code formatting matches project style
- [ ] No print statements or emoji in source
- [ ] All tests pass (unit + integration)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->
```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh opencode`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
The `/tasks` command will transform Phase 1 contracts into actionable implementation tasks following TDD workflow:

1. **Contract Test Tasks** - One task per contract file:
   - `cli-contract.md` → Contract tests for all 5 CLI commands (index, search, list, remove, global options)
   - `chromadb-contract.md` → Contract tests for 7 storage operations (create_collection, add_chunks, search_chunks, etc.)
   - `cleaning-contract.md` → Contract tests for 6 cleaning functions (parse_frontmatter, clean_shortcodes, etc.)
   - Each test validates interface, inputs/outputs, error conditions per contract spec

2. **Data Model Tasks** - From `data-model.md`:
   - DocumentChunk model with validation (content, metadata, embeddings)
   - CollectionMetadata model (name, description, source_url, etc.)
   - Pydantic validators for field constraints

3. **Implementation Tasks** - Per contract module:
   - CLI implementation (argparse-based, exit codes, JSON output)
   - ChromaDB wrapper (PersistentClient, batch processing, error handling)
   - Cleaning pipeline (regex-based, pipeline orchestration)

4. **Integration Tasks** - From `quickstart.md`:
   - End-to-end Istio test scenario (6 phases)
   - Performance validation (10K lines/sec cleaning, <100ms search)
   - Error handling verification

**Ordering Strategy**:
- Phase A: Contract tests first (all [P] parallel execution)
- Phase B: Data models (parallel, no dependencies)
- Phase C: Core implementation (ChromaDB → Cleaning → CLI dependency chain)
- Phase D: Integration tests (after core implementation)

**TDD Workflow Enforcement**:
- All contract tests created before implementation
- Tests written to fail (assert contract violations)
- Implementation done only after test exists
- Each task links to specific contract section

**Dependency Management**:
- Mark [P] for independent tasks (contract tests, model files)
- Sequential ordering for dependent components (CLI depends on storage + cleaning)
- Batch processing optimizations in ChromaDB layer before CLI integration

**Estimated Output**: 30-35 numbered tasks in tasks.md
- 3 contract test suites
- 2 data model creation tasks
- 3 core implementation modules
- 6 integration test phases
- Build automation (justfile targets)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command - 72 tasks created in tasks.md)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (no violations detected in plan)
- [x] Post-Design Constitution Check: PASS (no new violations)
- [x] All NEEDS CLARIFICATION resolved (user provided implementation details)
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
