# Quickstart: End-to-End Integration Test

**Date**: 2025-09-30  
**Feature**: Hugo Documentation Retriever  
**Branch**: 001-hetriever-stands-for

## Overview

This quickstart provides a comprehensive end-to-end test scenario that validates the complete Hugo Documentation Retriever system. It serves as both integration test specification and user onboarding guide.

## Test Scenario: Istio Documentation Retrieval

### Setup Phase

**Objective**: Initialize project with Istio documentation as test submodule.

**Steps**:

```bash
# 1. Create test environment
mkdir -p docs
cd docs

# 2. Add Istio documentation as Git submodule
git submodule add -b release-1.20 https://github.com/istio/istio.io.git istio-docs
git submodule update --init --recursive

# 3. Verify submodule structure
ls -la istio-docs/content/en/docs/
# Expected: concepts/ setup/ tasks/ reference/ ops/

# 4. Return to project root
cd ..
```

**Expected State**:
```
./docs/istio-docs/
├── .git
├── content/
│   └── en/
│       └── docs/
│           ├── concepts/
│           ├── setup/
│           ├── tasks/
│           ├── reference/
│           └── ops/
└── ...
```

**Validation**:
- Submodule exists at `docs/istio-docs/`
- `.gitmodules` contains istio-docs entry
- Markdown files exist in `content/en/docs/`

---

### Phase 1: Indexing

**Objective**: Index Istio documentation into ChromaDB.

**Command**:
```bash
hetriever index --verbose
```

**Expected Output**:
```
Indexing repositories...
[istio-docs] Found 247 markdown files
[istio-docs] Processing content/en/docs/setup/install/istioctl.md (12 chunks)
[istio-docs] Processing content/en/docs/concepts/traffic-management.md (18 chunks)
[istio-docs] Processing content/en/docs/tasks/security/authentication.md (15 chunks)
...
[istio-docs] Cleaning Hugo syntax from 247 files
[istio-docs] Generated 6,842 chunks (avg 27.7 chunks/file)
[istio-docs] Storing chunks to ChromaDB collection 'istio-docs'
[istio-docs] Stored 6,842 chunks in 142 batches
✓ istio-docs (247 files, 6,842 chunks) - 28.4s
Indexed 1 repository, 247 files, 6,842 chunks in 28.4s
```

**Performance Validation**:
- Processing rate: ≥10,000 lines/second
- Time per file: <200ms average
- Total time: <60 seconds for 247 files
- Memory usage: <512MB peak

**Storage Validation**:
```bash
# Check ChromaDB directory created
ls -lh chroma_data/
# Expected: chroma.sqlite3 + collection directories

# Check collection metadata
hetriever list --format json
# Expected: istio-docs collection with 6,842 chunks
```

**Data Integrity Checks**:

```python
# Test: Verify all chunks stored
collection = client.get_collection("istio-docs")
assert collection.count() == 6842

# Test: Verify metadata structure
result = collection.get(limit=1, include=["metadatas"])
metadata = result["metadatas"][0]
assert "file_path" in metadata
assert "repository" in metadata
assert "heading_context" in metadata
assert metadata["repository"] == "istio-docs"

# Test: Verify frontmatter extraction
result = collection.get(
    where={"file_path": "content/en/docs/setup/install/istioctl.md"},
    limit=1,
    include=["metadatas"]
)
assert "title" in result["metadatas"][0]
```

---

### Phase 2: Search - Basic Queries

**Objective**: Validate semantic search functionality.

**Test Case 2.1: Installation Query**

```bash
hetriever search "how to install istio with istioctl" --limit 5
```

**Expected Output**:
```
Results for "how to install istio with istioctl" (5 matches):

1. [istio-docs] content/en/docs/setup/install/istioctl.md (score: 0.91)
   Installation > Install with Istioctl
   
   This guide shows you how to install Istio using istioctl. The istioctl
   command provides rich customization of the installation configuration...

2. [istio-docs] content/en/docs/setup/getting-started.md (score: 0.87)
   Getting Started > Download Istio
   
   Download the latest Istio release which includes the istioctl client binary.
   The istioctl binary is used to install and configure Istio...

3. [istio-docs] content/en/docs/setup/install/operator.md (score: 0.82)
   Installation > Install with Operator
   
   Besides istioctl, you can also install Istio using the Istio operator.
   The operator provides a declarative API...

4. [istio-docs] content/en/docs/setup/platform-setup.md (score: 0.79)
   Platform Setup > Prerequisites
   
   Before you begin installing Istio, ensure your platform meets the following
   requirements. Istio requires a Kubernetes cluster...

5. [istio-docs] content/en/docs/reference/commands/istioctl.md (score: 0.76)
   Reference > Istioctl Commands
   
   The istioctl command-line tool provides various commands for managing your
   Istio service mesh...
```

**Validation**:
- Top result is highly relevant (score >0.85)
- Results are ranked by similarity
- Heading context preserved
- Content is cleaned (no `{{< >}}` shortcodes)

**Test Case 2.2: Concept Query**

```bash
hetriever search "explain virtual services and destination rules"
```

**Expected Top Result**:
```
1. [istio-docs] content/en/docs/concepts/traffic-management.md (score: 0.89)
   Concepts > Traffic Management > Virtual Services
   
   Virtual services and destination rules are the key building blocks of Istio's
   traffic routing functionality. A virtual service lets you configure how requests
   are routed to a service within an Istio service mesh...
```

**Validation**:
- Semantic understanding (query uses "explain", result is conceptual)
- Correct section matching (Concepts, not Tasks)

**Test Case 2.3: Troubleshooting Query**

```bash
hetriever search "debugging mutual TLS authentication issues"
```

**Expected Top Result**:
```
1. [istio-docs] content/en/docs/ops/diagnostic-tools/proxy-cmd.md (score: 0.84)
   Operations > Diagnostic Tools > Debugging TLS
   
   This page describes how to use istioctl and Envoy's admin interface to
   troubleshoot mutual TLS configuration issues...
```

**Validation**:
- Correctly identifies operational/troubleshooting content
- Matches on semantic concept (TLS authentication = mutual TLS)

---

### Phase 3: Search - Advanced Queries

**Objective**: Test filtering, formatting, and edge cases.

**Test Case 3.1: Repository Filtering**

```bash
# Add second repository for contrast
cd docs
git submodule add https://github.com/gohugoio/hugoDocs.git hugo-docs
cd ..
hetriever index --repo hugo-docs

# Search only istio-docs
hetriever search "installation" --repo istio-docs --limit 3
```

**Expected Behavior**:
- All results from istio-docs only
- No hugo-docs results in output

**Test Case 3.2: JSON Output Format**

```bash
hetriever search "security policies" --format json --limit 2
```

**Expected Output**:
```json
{
  "query": "security policies",
  "total_results": 2,
  "search_time_ms": 42.3,
  "matches": [
    {
      "chunk_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "repository": "istio-docs",
      "file_path": "content/en/docs/concepts/security.md",
      "heading_context": "Security > Authorization Policies",
      "content": "Istio authorization policies enable access control...",
      "score": 0.88,
      "metadata": {
        "title": "Security",
        "section": "Authorization Policies",
        "has_code": true,
        "tags": ["security", "authorization"]
      }
    }
  ]
}
```

**Validation**:
- Valid JSON structure
- All fields present
- Parseable by `jq` or `json.loads()`

**Test Case 3.3: No Results**

```bash
hetriever search "xyzabc nonexistent gibberish"
```

**Expected Output**:
```
Results for "xyzabc nonexistent gibberish" (0 matches):

No results found.
```

**Validation**:
- Exit code 0 (not an error)
- Helpful message
- No exceptions raised

**Test Case 3.4: Empty Query**

```bash
hetriever search ""
```

**Expected Output**:
```
Error: Query cannot be empty
```

**Validation**:
- Exit code 2
- Clear error message
- No ChromaDB query executed

---

### Phase 4: Collection Management

**Objective**: Test listing and removing collections.

**Test Case 4.1: List Collections**

```bash
hetriever list
```

**Expected Output**:
```
Indexed repositories:

hugo-docs
  URL: https://github.com/gohugoio/hugoDocs.git
  Branch: main
  Last updated: 2025-09-30 15:12:34
  Commit: 9876543210fedcba0987654321fedcba09876543
  Files: 142 | Chunks: 3,204

istio-docs
  URL: https://github.com/istio/istio.io.git
  Branch: release-1.20
  Last updated: 2025-09-30 15:10:22
  Commit: a1b2c3d4e5f6789012345678901234567890abcd
  Files: 247 | Chunks: 6,842
```

**Validation**:
- Alphabetically sorted
- All metadata fields present
- Matches indexed repositories

**Test Case 4.2: Remove Collection**

```bash
hetriever remove hugo-docs --confirm
```

**Expected Output**:
```
✓ Removed hugo-docs (3,204 chunks deleted)
```

**Validation**:
```bash
hetriever list
# Should only show istio-docs

# Verify collection deleted from ChromaDB
# Should raise CollectionNotFoundError if queried
```

---

### Phase 5: Reindexing and Updates

**Objective**: Test incremental updates and forced reindexing.

**Test Case 5.1: No-Op Reindex**

```bash
# Index again without changes
hetriever index
```

**Expected Output**:
```
Indexing repositories...
✓ istio-docs (unchanged, skipped)
Indexed 0 repositories (1 skipped)
```

**Validation**:
- Detects unchanged commit hash
- Skips processing
- Fast execution (<1 second)

**Test Case 5.2: Forced Reindex**

```bash
hetriever index --force
```

**Expected Output**:
```
Indexing repositories...
[istio-docs] Forcing reindex (commit unchanged)
✓ istio-docs (247 files, 6,842 chunks) - 28.1s
Indexed 1 repository, 247 files, 6,842 chunks in 28.1s
```

**Validation**:
- Processes all files despite unchanged commit
- Same chunk count as initial index
- Collection recreated (old data deleted)

**Test Case 5.3: Submodule Update**

```bash
# Update submodule to new commit
cd docs/istio-docs
git checkout release-1.21
cd ../..

# Reindex
hetriever index
```

**Expected Output**:
```
Indexing repositories...
[istio-docs] Detected new commit: def456... (was: abc123...)
✓ istio-docs (251 files, 6,987 chunks) - 29.3s
Indexed 1 repository, 251 files, 6,987 chunks in 29.3s
```

**Validation**:
- Detects commit change
- Processes new/modified files
- Updates collection metadata

---

### Phase 6: Error Handling

**Objective**: Validate graceful error handling.

**Test Case 6.1: Missing ChromaDB Path**

```bash
rm -rf chroma_data
hetriever search "test" --db-path /nonexistent/path
```

**Expected Output**:
```
Error: Cannot connect to ChromaDB at /nonexistent/path
```

**Validation**:
- Exit code 2
- Clear error message
- No stack trace shown to user

**Test Case 6.2: Invalid Repository Name**

```bash
hetriever index --repo nonexistent-repo
```

**Expected Output**:
```
Error: Repository 'nonexistent-repo' not found in docs/
```

**Validation**:
- Exit code 2
- Helpful error message
- Lists available repositories?

**Test Case 6.3: Malformed Markdown**

Create test file: `docs/istio-docs/test-malformed.md`
```markdown
---
invalid: yaml: syntax:: broken:
---
Content here
```

```bash
hetriever index --repo istio-docs --verbose
```

**Expected Output**:
```
[istio-docs] Processing test-malformed.md
[istio-docs] Warning: Failed to parse frontmatter in test-malformed.md
[istio-docs] Continuing with empty frontmatter
✓ istio-docs (248 files, 6,845 chunks) - 28.7s
```

**Validation**:
- Logs warning but continues
- File still processed (content extracted)
- Exit code 0 (partial success)

---

## Success Criteria

### Functional Requirements ✅

- [x] Index Hugo documentation from Git submodules
- [x] Clean Hugo-specific syntax (shortcodes, code fence attrs, links)
- [x] Generate semantic embeddings using ChromaDB
- [x] Perform similarity search with ranking
- [x] List indexed repositories with metadata
- [x] Remove collections
- [x] Handle incremental updates (detect commit changes)
- [x] Support multiple repositories

### Performance Requirements ✅

- [x] Index 10,000+ lines/second
- [x] Search queries <100ms (p95)
- [x] Memory usage <512MB
- [x] Process 247 files in <60 seconds

### Quality Requirements ✅

- [x] Exit codes follow conventions (0=success, 1=partial, 2=error)
- [x] Clear, actionable error messages
- [x] Preserve semantic content during cleaning
- [x] Handle malformed input gracefully
- [x] Idempotent operations (safe to re-run)

---

## Constitutional Alignment

**User Experience (II)**: Quickstart demonstrates clear CLI workflow with expected outputs.  
**Performance (III)**: All performance targets validated through end-to-end scenario.  
**Code Quality (I)**: Comprehensive error handling and edge cases tested.  
**Python 3.13 (IV)**: Modern Python features demonstrated in test assertions.

---

## Running This Quickstart

### Automated Test Script

```bash
# Run full quickstart as integration test
just test-quickstart

# Or manually:
pytest tests/integration/test_quickstart.py -v
```

### Manual Execution

Follow each phase sequentially, validating output at each step. This doubles as user onboarding.

### CI/CD Integration

```yaml
# .github/workflows/quickstart.yml
name: Quickstart Integration Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: uv sync
      - run: just test-quickstart
```

---

## Next Steps

After successful quickstart:
1. Explore advanced features (custom embedding models, chunking strategies)
2. Integrate with LLM applications (RAG pipelines)
3. Scale to larger documentation sets (100K+ chunks)
4. Customize cleaning rules for other static site generators
