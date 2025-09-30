# Research: Hugo Documentation Retriever

**Date**: 2025-09-30  
**Feature**: Hugo Documentation Retriever  
**Branch**: 001-hetriever-stands-for

## Research Tasks

### 1. ChromaDB Integration with Python 3.13

**Decision**: Use ChromaDB PersistentClient with local storage in current directory

**Rationale**:
- PersistentClient stores data on disk, enabling persistence across sessions
- ChromaDB natively supports vector embeddings and semantic search
- Python 3.13 compatible with chromadb>=0.4.0
- Local storage eliminates external dependencies and network latency
- Built-in embedding functions reduce additional dependencies

**Alternatives Considered**:
- **EphemeralClient**: Rejected - data lost on restart, unsuitable for documentation persistence
- **HttpClient**: Rejected - requires separate ChromaDB server, violates minimal dependency principle
- **FAISS/Pinecone**: Rejected - ChromaDB provides simpler API and built-in persistence layer

**Implementation Notes**:
- Initialize with `chromadb.PersistentClient(path="./chroma_data")`
- Store in current directory as specified by user requirements
- Use default embedding function unless performance benchmarks show need for optimization
- Collection naming: use repository identifier to support multiple doc sources

### 2. Hugo Syntax Cleaning Strategy

**Decision**: Implement regex-based cleaning with frontmatter extraction, shortcode removal, and template directive stripping

**Rationale**:
- Hugo frontmatter (YAML/TOML) contains metadata, not documentation content
- Shortcodes like `{{< ref >}}` disrupt semantic meaning for LLMs
- Template directives and Hugo-specific syntax add noise to embeddings
- Standard library `re` module sufficient for pattern matching
- Preserves Markdown structure (headings, lists, code blocks, links)

**Alternatives Considered**:
- **Hugo CLI parsing**: Rejected - adds external dependency, requires Hugo installation
- **Full Markdown parsing library (markdown-it-py)**: Rejected - overkill for cleaning task
- **LLM-based cleaning**: Rejected - adds latency, API costs, non-deterministic results

**Implementation Patterns**:
1. Extract and parse frontmatter with `re.split(r'^---\s*$', content, flags=re.MULTILINE)`
2. Remove shortcodes with regex: `r'\{\{<.*?>\}\}'` and `r'\{\{%.*?%\}\}'`
3. Remove template directives: `r'\{\{.*?\}\}'`
4. Preserve code blocks (fenced with ```) to avoid cleaning code examples
5. Normalize whitespace while preserving paragraph structure

### 3. Git Submodule Documentation Management

**Decision**: Use Git submodules for documentation repository tracking with manual update workflow

**Rationale**:
- Submodules provide version-controlled documentation snapshots
- Manual update gives user control over when to refresh documentation
- Avoids rate limiting from GitHub API during development
- Standard Git tooling, no custom repository management needed
- Supports offline development and testing

**Alternatives Considered**:
- **GitHub API fetching**: Rejected - rate limits, authentication complexity, API dependency
- **git clone per fetch**: Rejected - inefficient, doesn't track versioning
- **Direct HTTP download**: Rejected - no version tracking, unreliable for large repos

**Workflow**:
1. User adds documentation repo as submodule: `git submodule add <repo-url> docs/<repo-name>`
2. System scans `docs/` directory for submodule repositories
3. User updates documentation: `git submodule update --remote`
4. Processing triggered via CLI command after manual update

### 4. Documentation Chunking Strategy

**Decision**: Semantic chunking based on Markdown headings with overlap to preserve context

**Rationale**:
- Headings represent semantic boundaries in documentation
- Chunk size affects retrieval precision vs context coverage
- Overlap prevents information loss at chunk boundaries
- Markdown heading hierarchy provides natural structure
- Target 512-1024 tokens per chunk for optimal embedding performance

**Alternatives Considered**:
- **Fixed-size chunking**: Rejected - breaks semantic units, poor retrieval quality
- **Paragraph-based chunking**: Rejected - paragraphs vary too much in size
- **Sentence-based chunking**: Rejected - too granular, loses context

**Implementation Strategy**:
1. Parse Markdown using heading hierarchy (H1, H2, H3)
2. Split at H2 boundaries as primary chunks
3. Include parent H1 context in chunk metadata
4. Target chunk size: 800 tokens (balanced for embedding models)
5. Overlap: 100 tokens (preserve continuity between sections)
6. Preserve code blocks as complete units (don't split mid-code)

### 5. Testing Strategy for Documentation Pipeline

**Decision**: Three-layer testing approach - contract tests for ChromaDB, integration tests for pipeline, unit tests for cleaning functions

**Rationale**:
- Contract tests validate ChromaDB API expectations remain stable
- Integration tests verify end-to-end documentation processing
- Unit tests ensure cleaning logic handles edge cases correctly
- pytest fixtures enable isolated testing with temporary ChromaDB instances
- Follows constitutional TDD requirement

**Test Layers**:
1. **Contract Tests**: ChromaDB client initialization, collection creation, embedding storage/retrieval
2. **Integration Tests**: Complete documentation processing workflow from submodule to retrieval
3. **Unit Tests**: Frontmatter extraction, shortcode removal, chunking logic, metadata preservation

**Test Data**:
- Fixture: Sample Hugo documentation files with known shortcodes, frontmatter patterns
- Mock repositories with controlled documentation structure
- Edge cases: empty files, malformed frontmatter, nested shortcodes, large code blocks

### 6. Python 3.13 Feature Utilization

**Decision**: Use PEP 695 type syntax, pattern matching, and exception groups for modern, type-safe code

**Rationale**:
- PEP 695 generic type syntax simplifies type annotations
- Pattern matching improves readability for frontmatter parsing and content classification
- Exception groups handle multiple processing failures gracefully
- Aligns with constitutional requirement for Python 3.13 features

**Features to Use**:
- `type` statement for type aliases: `type DocumentChunk = dict[str, str | list[str]]`
- Pattern matching for frontmatter format detection (YAML vs TOML vs JSON)
- Exception groups to collect and report multiple file processing errors
- `asyncio` for concurrent submodule processing (if multiple repos)

**Example Pattern Match**:
```python
match frontmatter_delimiter:
    case "---":
        return parse_yaml(frontmatter_content)
    case "+++":
        return parse_toml(frontmatter_content)
    case _:
        raise ValueError(f"Unknown frontmatter delimiter: {frontmatter_delimiter}")
```

### 7. Justfile Build Automation

**Decision**: Create minimal justfile with clean recipes for install, test, format, lint, and run commands

**Rationale**:
- User requirement: "justfile for the script without any useless script and echo"
- Just provides cross-platform command automation without shell script complexity
- Recipes replace verbose command-line invocations
- Minimal output (no echo statements) for clean CI/CD logs

**Recipes to Include**:
- `install`: `uv sync` (install dependencies)
- `test`: `uv run pytest` (run test suite)
- `format`: `uv run ruff format` (format code)
- `lint`: `uv run ruff check` (lint code)
- `typecheck`: `uv run mypy` or `uv run pyright` (type checking)
- `process`: Main CLI command to process documentation
- `clean`: Remove generated artifacts and ChromaDB data

**Constitutional Alignment**:
- No unnecessary echo statements (clean output)
- Standard tool invocations (uv, pytest, ruff)
- Supports quality gates (test, format, lint, typecheck)

## Dependencies Justification

| Dependency | Rationale | Standard Library Alternative | Justified? |
|------------|-----------|------------------------------|------------|
| chromadb | Vector database with embeddings, persistence, and semantic search built-in | None - would require custom vector storage + embedding generation | ✅ Yes |
| uv | Fast Python package manager, constitutional requirement | pip/venv - slower, less reliable resolution | ✅ Yes |
| pytest | Industry standard testing framework with rich fixture ecosystem | unittest - less ergonomic, no fixtures | ✅ Yes |
| ruff | Fast linter/formatter, constitutional requirement | pylint + black - slower, separate tools | ✅ Yes |
| pyyaml | Parse Hugo frontmatter (YAML format) | None - YAML parsing complex to implement | ✅ Yes |
| tomli | Parse Hugo frontmatter (TOML format), stdlib in 3.11+ for reading | tomllib (stdlib) available for reading only | ✅ Yes (use tomllib) |

**Rejected Dependencies**:
- `markdown`: Unnecessary - we're cleaning Markdown, not rendering it
- `beautifulsoup4`: Unnecessary - documentation is Markdown, not HTML
- `requests`: Unnecessary - using git submodules, not HTTP API
- `click/typer`: Evaluate during design - stdlib `argparse` may suffice for simple CLI

## Open Questions for Phase 1

1. **CLI Interface Design**: Should the tool accept repository URLs directly or only process existing submodules?
   - **Resolution Path**: Design contract for CLI arguments in Phase 1
   
2. **Incremental Updates**: Should the system detect which documentation files changed and only reprocess those?
   - **Resolution Path**: Define in data model - track file hashes or modification timestamps
   
3. **Embedding Model Selection**: Use ChromaDB default embedding or specify a model?
   - **Resolution Path**: Default initially, add configuration option if benchmarks show performance issues
   
4. **Collection Management**: One collection per repository or single collection with metadata filtering?
   - **Resolution Path**: Design data model to answer - likely one collection per repo for isolation

## Constitutional Compliance Review

**Principle I - Code Quality**: ✅ Research favors standard library (re, tomllib) and minimal external dependencies  
**Principle II - User Experience**: ✅ CLI with clean output, JSON mode planned  
**Principle III - Performance**: ✅ Chunking strategy targets embedding model optimal size, local storage eliminates network latency  
**Principle IV - Python 3.13**: ✅ PEP 695 types, pattern matching, exception groups identified for use  
**Principle V - Minimal Dependencies**: ✅ Only 3-4 external dependencies, all justified (chromadb, pytest, ruff, pyyaml)

## Next Steps

Phase 1 will generate:
1. **data-model.md**: Entity schemas for DocumentRepository, DocumentFile, DocumentChunk, Embedding, ChromaDB collection structure
2. **contracts/**: CLI interface contract, ChromaDB storage contract, cleaning function contracts
3. **quickstart.md**: End-to-end test scenario from submodule add to semantic query
4. **AGENTS.md**: Agent context file for development tools

All design decisions will be validated against constitutional requirements before proceeding to Phase 2 task generation.
