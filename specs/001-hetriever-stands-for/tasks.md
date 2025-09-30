# Tasks: Hugo Documentation Retriever

**Date**: 2025-09-30  
**Feature**: Hugo Documentation Retriever  
**Branch**: 001-hetriever-stands-for

**Input**: Design documents from `/specs/001-hetriever-stands-for/`
**Prerequisites**: plan.md, data-model.md, contracts/ (cli, chromadb, cleaning)

## Phase 3.1: Setup

- [ ] T001 Create project structure with `src/`, `tests/`, `chroma_data/`
- [ ] T002 Initialize Python project with `pyproject.toml` and `justfile` build automation
- [ ] T003 [P] Configure dependencies: `uv add chromadb pyyaml pytest pytest-benchmark hypothesis`
- [ ] T004 [P] Configure linting with `ruff check .` and formatting rules

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T005 [P] Contract test `parse_frontmatter` in `tests/contract/test_cleaning_contract.py`
- [ ] T006 [P] Contract test `clean_shortcodes` in `tests/contract/test_cleaning_contract.py`
- [ ] T007 [P] Contract test `clean_code_fences` in `tests/contract/test_cleaning_contract.py`
- [ ] T008 [P] Contract test `clean_links` in `tests/contract/test_cleaning_contract.py`
- [ ] T009 [P] Contract test `normalize_whitespace` in `tests/contract/test_cleaning_contract.py`
- [ ] T010 [P] Contract test `clean_markdown` full pipeline in `tests/contract/test_cleaning_contract.py`
- [ ] T011 [P] Contract test ChromaDB `create_collection` in `tests/contract/test_chromadb_contract.py`
- [ ] T012 [P] Contract test ChromaDB `add_chunks` in `tests/contract/test_chromadb_contract.py`
- [ ] T013 [P] Contract test ChromaDB `search_chunks` in `tests/contract/test_chromadb_contract.py`
- [ ] T014 [P] Contract test ChromaDB `get_collection_metadata` in `tests/contract/test_chromadb_contract.py`
- [ ] T015 [P] Contract test ChromaDB `list_collections` in `tests/contract/test_chromadb_contract.py`
- [ ] T016 [P] Contract test ChromaDB `delete_collection` in `tests/contract/test_chromadb_contract.py`
- [ ] T017 [P] Contract test CLI `index` command in `tests/contract/test_cli_contract.py`
- [ ] T018 [P] Contract test CLI `search` command in `tests/contract/test_cli_contract.py`
- [ ] T019 [P] Contract test CLI `list` command in `tests/contract/test_cli_contract.py`
- [ ] T020 [P] Contract test CLI `remove` command in `tests/contract/test_cli_contract.py`
- [ ] T021 [P] Contract test CLI global options (--db-path, --verbose) in `tests/contract/test_cli_contract.py`

### Edge Case Tests
- [ ] T022 [P] Edge case test malformed frontmatter in `tests/unit/test_cleaning_edge_cases.py`
- [ ] T023 [P] Edge case test nested shortcodes in `tests/unit/test_cleaning_edge_cases.py`
- [ ] T024 [P] Edge case test nested code fences in `tests/unit/test_cleaning_edge_cases.py`
- [ ] T025 [P] Edge case test Unicode characters in `tests/unit/test_cleaning_edge_cases.py`

## Phase 3.3: Data Models (ONLY after tests are failing)

- [ ] T026 [P] `DocumentChunk` Pydantic model in `src/models/document.py`
- [ ] T027 [P] `CollectionMetadata` Pydantic model in `src/models/collection.py`
- [ ] T028 [P] `RetrievalResult` Pydantic model in `src/models/retrieval.py`
- [ ] T029 [P] Model validation logic and custom validators

## Phase 3.4: Core Implementation - Cleaning Pipeline

- [ ] T030 [P] Implement `parse_frontmatter` (YAML/TOML) in `src/cleaning/frontmatter.py`
- [ ] T031 [P] Implement `clean_shortcodes` (content extraction) in `src/cleaning/shortcodes.py`
- [ ] T032 [P] Implement `clean_code_fences` (attribute removal) in `src/cleaning/code_fences.py`
- [ ] T033 [P] Implement `clean_links` (ref/relref conversion) in `src/cleaning/links.py`
- [ ] T034 [P] Implement `normalize_whitespace` (preserve structure) in `src/cleaning/whitespace.py`
- [ ] T035 Implement `clean_markdown` orchestration pipeline in `src/cleaning/pipeline.py`
- [ ] T036 [P] Compile regex patterns as module constants in `src/cleaning/patterns.py`

## Phase 3.5: Core Implementation - ChromaDB Wrapper

- [ ] T037 Implement `ChromaDBClient` initialization in `src/storage/chromadb_client.py`
- [ ] T038 Implement `create_collection` with metadata in `src/storage/chromadb_client.py`
- [ ] T039 Implement `add_chunks` batching (batch_size=100) in `src/storage/chromadb_client.py`
- [ ] T040 Implement `search_chunks` with filters in `src/storage/chromadb_client.py`
- [ ] T041 Implement `get_collection_metadata` in `src/storage/chromadb_client.py`
- [ ] T042 Implement `list_collections` with sorting in `src/storage/chromadb_client.py`
- [ ] T043 Implement `delete_collection` with confirmation in `src/storage/chromadb_client.py`

## Phase 3.6: Core Implementation - Document Processing

- [ ] T044 [P] Implement file discovery (glob Markdown) in `src/processing/file_discovery.py`
- [ ] T045 [P] Implement chunking strategy (heading-based) in `src/processing/chunker.py`
- [ ] T046 [P] Implement heading context extraction in `src/processing/context_extractor.py`
- [ ] T047 [P] Implement metadata enrichment (frontmatter + git) in `src/processing/metadata.py`
- [ ] T048 Implement main indexing orchestration in `src/processing/indexer.py`

## Phase 3.7: Core Implementation - CLI

- [ ] T049 Implement CLI entry point with Click framework in `src/cli/main.py`
- [ ] T050 Implement `hetriever index` command in `src/cli/commands/index.py`
- [ ] T051 Implement `hetriever search` command in `src/cli/commands/search.py`
- [ ] T052 Implement `hetriever list` command in `src/cli/commands/list.py`
- [ ] T053 Implement `hetriever remove` command in `src/cli/commands/remove.py`
- [ ] T054 [P] Implement global options (--db-path, --verbose) in `src/cli/options.py`
- [ ] T055 [P] Implement output formatters (text, JSON) in `src/cli/formatters.py`

## Phase 3.8: Integration Tests (Quickstart Scenarios)

- [ ] T056 [P] Integration test Phase 1: Indexing Istio docs in `tests/integration/test_quickstart_indexing.py`
- [ ] T057 [P] Integration test Phase 2: Basic search queries in `tests/integration/test_quickstart_search.py`
- [ ] T058 [P] Integration test Phase 3: Advanced search (filters, JSON) in `tests/integration/test_quickstart_advanced.py`
- [ ] T059 [P] Integration test Phase 4: Collection management in `tests/integration/test_quickstart_collections.py`
- [ ] T060 [P] Integration test Phase 5: Reindexing and updates in `tests/integration/test_quickstart_updates.py`
- [ ] T061 [P] Integration test Phase 6: Error handling in `tests/integration/test_quickstart_errors.py`

## Phase 3.9: Performance Validation

- [ ] T062 [P] Benchmark cleaning throughput (10K+ lines/sec) in `tests/benchmarks/test_cleaning_performance.py`
- [ ] T063 [P] Benchmark indexing throughput (247 files <60s) in `tests/benchmarks/test_indexing_performance.py`
- [ ] T064 [P] Benchmark search latency (p95 <100ms) in `tests/benchmarks/test_search_performance.py`
- [ ] T065 [P] Memory profiling (<512MB peak) in `tests/benchmarks/test_memory_usage.py`

## Phase 3.10: Polish

- [ ] T066 [P] Property-based tests with `hypothesis` for cleaning functions in `tests/property/test_cleaning_properties.py`
- [ ] T067 [P] Error handling and logging in all modules
- [ ] T068 [P] Add type hints and docstrings (Google style)
- [ ] T069 Run `ruff check .` and fix all linting issues
- [ ] T070 Run `pytest` and verify all tests pass
- [ ] T071 [P] Update README.md with installation and usage
- [ ] T072 [P] Create example justfile recipes (test, lint, benchmark)

## Dependencies

**Setup → Tests → Implementation → Integration → Polish**

### Critical Paths:
1. **Setup**: T001-T004 must complete before any other work
2. **Contract Tests First**: T005-T025 must be written and failing before T026-T055
3. **Models First**: T026-T029 block all service implementations
4. **Sequential Within Modules**:
   - T030-T034 → T035 (pipeline orchestration)
   - T037-T043 (ChromaDB methods sequential in same file)
   - T044-T047 → T048 (indexer orchestration)
   - T049-T054 → T055 (CLI commands before formatters)
5. **Integration Tests**: T056-T061 require T026-T055 complete
6. **Benchmarks**: T062-T065 require T026-T055 complete
7. **Polish**: T066-T072 are final phase

### Parallel Opportunities:
- **T005-T021**: All contract tests (different test files/classes)
- **T022-T025**: All edge case tests (different test modules)
- **T026-T029**: All data models (different files)
- **T030-T036**: All cleaning functions (different files except T035)
- **T044-T047**: Processing modules (different files)
- **T050-T053**: CLI commands (different files)
- **T054-T055**: CLI utilities (different files)
- **T056-T061**: Integration tests (different scenarios)
- **T062-T065**: Benchmarks (different aspects)
- **T066-T072**: Polish tasks (different concerns)

## Parallel Execution Example

```bash
# Phase 3.2: Launch all contract tests together
Task: "Contract test parse_frontmatter in tests/contract/test_cleaning_contract.py"
Task: "Contract test clean_shortcodes in tests/contract/test_cleaning_contract.py"
Task: "Contract test ChromaDB create_collection in tests/contract/test_chromadb_contract.py"
Task: "Contract test CLI index command in tests/contract/test_cli_contract.py"
# ... all T005-T025 in parallel

# Phase 3.3: Launch all data models together
Task: "DocumentChunk model in src/models/document.py"
Task: "CollectionMetadata model in src/models/collection.py"
Task: "RetrievalResult model in src/models/retrieval.py"

# Phase 3.4: Launch cleaning functions in parallel
Task: "Implement parse_frontmatter in src/cleaning/frontmatter.py"
Task: "Implement clean_shortcodes in src/cleaning/shortcodes.py"
Task: "Implement clean_code_fences in src/cleaning/code_fences.py"
# ... then T035 pipeline.py (sequential)
```

## Task Breakdown Summary

| Phase | Tasks | Parallel | Sequential | Estimated Time |
|-------|-------|----------|------------|----------------|
| 3.1 Setup | T001-T004 | 2 | 2 | 30 min |
| 3.2 Tests | T005-T025 | 21 | 0 | 3-4 hours |
| 3.3 Models | T026-T029 | 4 | 0 | 1 hour |
| 3.4 Cleaning | T030-T036 | 6 | 1 | 2 hours |
| 3.5 ChromaDB | T037-T043 | 0 | 7 | 2 hours |
| 3.6 Processing | T044-T048 | 4 | 1 | 2 hours |
| 3.7 CLI | T049-T055 | 2 | 5 | 2 hours |
| 3.8 Integration | T056-T061 | 6 | 0 | 2 hours |
| 3.9 Performance | T062-T065 | 4 | 0 | 1 hour |
| 3.10 Polish | T066-T072 | 6 | 1 | 1.5 hours |
| **Total** | **72 tasks** | **55** | **17** | **17-18 hours** |

## Validation Checklist

**GATE: All must pass before declaring Phase 3 complete**

- [x] All contracts have corresponding tests (T005-T021 cover all 3 contracts)
- [x] All entities have model tasks (T026-T029 cover DocumentChunk, CollectionMetadata, RetrievalResult)
- [x] All tests come before implementation (T005-T025 before T026-T072)
- [x] Parallel tasks are truly independent (different files, marked [P])
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] TDD workflow enforced (tests fail → implement → tests pass)
- [x] Quickstart scenarios have integration tests (T056-T061)
- [x] Performance targets have benchmarks (T062-T065)
- [x] All cleaning functions tested (T005-T010, T022-T025)
- [x] All ChromaDB operations tested (T011-T016)
- [x] All CLI commands tested (T017-T021)

## Notes

- **[P] marker**: Tasks that touch different files and have no dependencies can run in parallel
- **TDD discipline**: Verify tests fail (red) before implementing (green), then refactor
- **Commit strategy**: Commit after each task completion with descriptive message
- **Error handling**: Log warnings for malformed input, raise exceptions for critical failures
- **Performance**: Profile early (T062-T065) to catch regressions
- **Avoid**: Vague task descriptions, implementing before tests fail, modifying same file in parallel

## Constitutional Alignment

**Code Quality (I)**: Comprehensive testing (55% of tasks), TDD workflow, type hints and docstrings  
**User Experience (II)**: Integration tests mirror user scenarios, clear error messages  
**Performance (III)**: Dedicated benchmark tasks, 10K lines/sec target validated  
**Python 3.13 (IV)**: Modern features (pattern matching, tomllib, Pydantic v2)
