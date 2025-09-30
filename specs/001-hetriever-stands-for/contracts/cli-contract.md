# CLI Contract: Hugo Documentation Retriever

**Date**: 2025-09-30  
**Feature**: Hugo Documentation Retriever  
**Branch**: 001-hetriever-stands-for

## Overview

This contract defines the command-line interface for the Hugo Documentation Retriever. All CLI commands follow POSIX conventions, provide clear feedback, and exit with appropriate status codes.

## Command Structure

```bash
hetriever <command> [options] [arguments]
```

## Commands

### 1. `hetriever index`

Index all documentation repositories (Git submodules in `docs/`).

**Signature**:
```bash
hetriever index [--repo REPO_NAME] [--force] [--verbose]
```

**Arguments**:
- `--repo REPO_NAME` (optional): Index only specified repository
- `--force` (optional): Reindex even if commit hash unchanged
- `--verbose` (optional): Show detailed processing logs

**Behavior**:
1. Scan `docs/` directory for Git submodules
2. For each repository (or specified repo):
   - Check current commit hash
   - Skip if unchanged (unless `--force`)
   - Process all `.md` files recursively
   - Clean Hugo syntax, chunk content
   - Generate embeddings and store in ChromaDB
3. Update repository metadata with processing timestamp

**Exit Codes**:
- `0`: Success (all files indexed)
- `1`: Partial failure (some files failed, see logs)
- `2`: Complete failure (ChromaDB unavailable, no submodules found)

**Output Format** (default):
```
Indexing repositories...
✓ istio-docs (127 files, 3,421 chunks) - 12.3s
✓ hugo-docs (89 files, 1,892 chunks) - 8.7s
Indexed 2 repositories, 216 files, 5,313 chunks in 21.0s
```

**Output Format** (`--verbose`):
```
Indexing repositories...
[istio-docs] Found 127 markdown files
[istio-docs] Processing docs/concepts/traffic.md (4 chunks)
[istio-docs] Processing docs/setup/install.md (7 chunks)
...
[istio-docs] Stored 3,421 chunks to ChromaDB
✓ istio-docs (127 files, 3,421 chunks) - 12.3s
...
```

**Error Handling**:
- Invalid repo name: `Error: Repository 'foo' not found in docs/`
- ChromaDB unavailable: `Error: Cannot connect to ChromaDB at ./chroma_data`
- Processing failure: `Warning: Failed to process docs/broken.md: InvalidMarkdownError`

**Test Cases**:
```python
def test_index_all_repos_success():
    result = run_cli(["index"])
    assert result.exit_code == 0
    assert "Indexed 2 repositories" in result.stdout

def test_index_specific_repo():
    result = run_cli(["index", "--repo", "istio-docs"])
    assert result.exit_code == 0
    assert "istio-docs" in result.stdout
    assert "hugo-docs" not in result.stdout

def test_index_no_submodules():
    result = run_cli(["index"])  # Empty docs/
    assert result.exit_code == 2
    assert "no submodules found" in result.stderr

def test_index_force_reindex():
    run_cli(["index"])  # First run
    result = run_cli(["index", "--force"])  # Force reindex
    assert result.exit_code == 0
    assert "Indexed" in result.stdout
```

---

### 2. `hetriever search`

Search indexed documentation using semantic similarity.

**Signature**:
```bash
hetriever search <query> [--repo REPO_NAME] [--limit N] [--format FORMAT]
```

**Arguments**:
- `query` (required): Search query string
- `--repo REPO_NAME` (optional): Search only specified repository
- `--limit N` (optional, default=10): Maximum results to return
- `--format FORMAT` (optional, default=text): Output format (`text`, `json`)

**Behavior**:
1. Parse query string
2. Generate query embedding
3. Search ChromaDB collection(s) for similar chunks
4. Rank results by similarity score
5. Return top N results with metadata

**Exit Codes**:
- `0`: Success (results found or not found)
- `2`: Error (ChromaDB unavailable, invalid repo)

**Output Format** (`--format text`):
```
Results for "install istio" (3 matches):

1. [istio-docs] docs/setup/install.md (score: 0.89)
   Installation > Prerequisites
   
   To install Istio, you need a Kubernetes cluster with at least 4GB of RAM
   and 2 CPUs. Supported versions are 1.28, 1.29, and 1.30.
   
2. [istio-docs] docs/setup/platforms/gke.md (score: 0.82)
   Platform Setup > Google Kubernetes Engine
   
   This guide shows you how to install Istio on GKE. Create a new cluster
   with the following command: gcloud container clusters create...
   
3. [istio-docs] docs/tasks/traffic/ingress.md (score: 0.76)
   Traffic Management > Ingress Gateway
   
   After installing Istio, configure an ingress gateway to allow external
   traffic into your service mesh...
```

**Output Format** (`--format json`):
```json
{
  "query": "install istio",
  "total_results": 3,
  "search_time_ms": 45.2,
  "matches": [
    {
      "chunk_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "repository": "istio-docs",
      "file_path": "docs/setup/install.md",
      "heading_context": "Installation > Prerequisites",
      "content": "To install Istio, you need a Kubernetes cluster...",
      "score": 0.89,
      "metadata": {
        "title": "Install Istio",
        "section": "Prerequisites",
        "has_code": true,
        "tags": ["installation", "setup"]
      }
    }
  ]
}
```

**Error Handling**:
- Empty query: `Error: Query cannot be empty`
- Invalid repo: `Error: Repository 'foo' not indexed`
- ChromaDB unavailable: `Error: Cannot connect to ChromaDB at ./chroma_data`
- Invalid limit: `Error: Limit must be between 1 and 100`

**Test Cases**:
```python
def test_search_finds_results():
    result = run_cli(["search", "install istio"])
    assert result.exit_code == 0
    assert "matches" in result.stdout or "Results for" in result.stdout

def test_search_no_results():
    result = run_cli(["search", "xyzabc nonexistent"])
    assert result.exit_code == 0
    assert "0 matches" in result.stdout or "No results" in result.stdout

def test_search_specific_repo():
    result = run_cli(["search", "routing", "--repo", "istio-docs"])
    assert result.exit_code == 0
    assert "istio-docs" in result.stdout

def test_search_json_format():
    result = run_cli(["search", "install", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "query" in data
    assert "matches" in data

def test_search_empty_query():
    result = run_cli(["search", ""])
    assert result.exit_code == 2
    assert "cannot be empty" in result.stderr
```

---

### 3. `hetriever list`

List indexed repositories and their metadata.

**Signature**:
```bash
hetriever list [--format FORMAT]
```

**Arguments**:
- `--format FORMAT` (optional, default=text): Output format (`text`, `json`)

**Behavior**:
1. Query ChromaDB for all collections
2. Retrieve metadata for each collection
3. Display repository information

**Exit Codes**:
- `0`: Success
- `2`: Error (ChromaDB unavailable)

**Output Format** (`--format text`):
```
Indexed repositories:

istio-docs
  URL: https://github.com/istio/istio.io
  Branch: master
  Last updated: 2025-09-30 14:32:01
  Commit: a1b2c3d4e5f6789012345678901234567890abcd
  Files: 127 | Chunks: 3,421

hugo-docs
  URL: https://github.com/gohugoio/hugo
  Branch: main
  Last updated: 2025-09-30 14:31:45
  Commit: 9876543210fedcba0987654321fedcba09876543
  Files: 89 | Chunks: 1,892
```

**Output Format** (`--format json`):
```json
{
  "repositories": [
    {
      "name": "istio-docs",
      "remote_url": "https://github.com/istio/istio.io",
      "branch": "master",
      "last_updated": "2025-09-30T14:32:01Z",
      "commit_hash": "a1b2c3d4e5f6789012345678901234567890abcd",
      "file_count": 127,
      "chunk_count": 3421
    }
  ]
}
```

**Test Cases**:
```python
def test_list_shows_repositories():
    result = run_cli(["list"])
    assert result.exit_code == 0
    assert "istio-docs" in result.stdout

def test_list_json_format():
    result = run_cli(["list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "repositories" in data

def test_list_no_repos():
    result = run_cli(["list"])  # No indexed repos
    assert result.exit_code == 0
    assert "No indexed repositories" in result.stdout
```

---

### 4. `hetriever remove`

Remove an indexed repository from ChromaDB.

**Signature**:
```bash
hetriever remove <repo> [--confirm]
```

**Arguments**:
- `repo` (required): Repository name to remove
- `--confirm` (optional): Skip confirmation prompt

**Behavior**:
1. Prompt for confirmation (unless `--confirm`)
2. Delete ChromaDB collection
3. Display success message

**Exit Codes**:
- `0`: Success
- `1`: User cancelled operation
- `2`: Error (invalid repo, ChromaDB unavailable)

**Output Format**:
```
Remove repository 'istio-docs'? This will delete 3,421 chunks. [y/N]: y
✓ Removed istio-docs (3,421 chunks deleted)
```

**Error Handling**:
- Invalid repo: `Error: Repository 'foo' not found`
- User cancels: `Operation cancelled`

**Test Cases**:
```python
def test_remove_with_confirm():
    result = run_cli(["remove", "istio-docs", "--confirm"])
    assert result.exit_code == 0
    assert "Removed istio-docs" in result.stdout

def test_remove_invalid_repo():
    result = run_cli(["remove", "nonexistent"])
    assert result.exit_code == 2
    assert "not found" in result.stderr
```

---

## Global Options

Available for all commands:

- `--help, -h`: Show command help
- `--version, -v`: Show version information
- `--db-path PATH`: Override ChromaDB path (default: `./chroma_data`)

**Examples**:
```bash
hetriever --version
hetriever index --help
hetriever search "query" --db-path /custom/path
```

---

## Environment Variables

- `HETRIEVER_DB_PATH`: Override default ChromaDB path
- `HETRIEVER_DOCS_DIR`: Override default docs directory (default: `./docs`)

**Precedence**: CLI flags > Environment variables > Defaults

---

## Constitutional Alignment

**User Experience (II)**: Clear, consistent CLI following POSIX conventions. Helpful error messages with actionable guidance.  
**Code Quality (I)**: Single responsibility per command. Exit codes follow standard conventions.  
**Performance (III)**: Commands provide progress feedback for long operations. JSON format enables scripting.

---

## Implementation Notes

**Technology**:
- Use Python 3.13 with `argparse` for CLI parsing (stdlib, no external dependencies)
- Rich output formatting with simple string templates (avoid external libraries)
- Async operations use `asyncio` for concurrent file processing

**Testing**:
- Use `pytest` with `subprocess.run()` to invoke CLI
- Mock ChromaDB operations for unit tests
- Integration tests with real submodules
