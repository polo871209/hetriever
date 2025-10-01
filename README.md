# hetriever

**H**ugo documentation r**etriever** with vector embeddings for semantic search.

A Python tool that indexes markdown documentation from Hugo sites and provides semantic search capabilities using ChromaDB.

## Features

- **Semantic Search**: Find documentation by meaning, not just keywords
- **Multi-Repository Support**: Index and search across multiple documentation repositories
- **Hugo-Aware Cleaning**: Removes frontmatter, shortcodes, and Hugo-specific syntax
- **Context-Preserving Chunking**: Maintains heading hierarchy and document structure
- **Git-Aware Metadata**: Extracts repository information from git context
- **Flexible CLI**: Simple commands for indexing, searching, and managing collections

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [just](https://github.com/casey/just) (optional, for running recipes)

### Install with uv

```bash
git clone https://github.com/yourusername/hetriever.git
cd hetriever
uv sync --all-extras
```

### Install with pip

```bash
git clone https://github.com/yourusername/hetriever.git
cd hetriever
pip install -e ".[dev]"
```

## Quick Start

### 1. Index Documentation

Index a Hugo documentation repository:

```bash
uv run python -m src.cli.main index /path/to/hugo/docs
```

Index a specific repository name:

```bash
uv run python -m src.cli.main index /path/to/docs --repo my-docs
```

### 2. Search Documentation

Search indexed documentation:

```bash
uv run python -m src.cli.main search "how to configure authentication"
```

Limit results:

```bash
uv run python -m src.cli.main search "deployment guide" --limit 5
```

Filter by repository:

```bash
uv run python -m src.cli.main search "API reference" --repo my-docs
```

### 3. List Collections

View all indexed repositories:

```bash
uv run python -m src.cli.main list
```

### 4. Remove Collections

Remove a specific repository:

```bash
uv run python -m src.cli.main remove my-docs
```

Remove all collections:

```bash
uv run python -m src.cli.main remove --all
```

## CLI Commands

### `index`

Index markdown documentation from a directory.

```bash
uv run python -m src.cli.main index [OPTIONS] PATH
```

**Options:**
- `--repo TEXT`: Repository name (defaults to directory name)
- `--force`: Force reindex even if unchanged
- `--verbose, -v`: Show detailed processing logs
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Example:**
```bash
uv run python -m src.cli.main index /path/to/docs --repo production-docs --verbose
```

### `search`

Search indexed documentation with semantic search.

```bash
uv run python -m src.cli.main search [OPTIONS] QUERY
```

**Options:**
- `--repo TEXT`: Filter by repository name
- `--limit INTEGER`: Maximum results to return (default: 10)
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Example:**
```bash
uv run python -m src.cli.main search "authentication setup" --repo my-docs --limit 5
```

### `list`

List all indexed repository collections.

```bash
uv run python -m src.cli.main list [OPTIONS]
```

**Options:**
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

### `remove`

Remove indexed repository collections.

```bash
uv run python -m src.cli.main remove [OPTIONS] [REPO]
```

**Options:**
- `--all`: Remove all collections
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Examples:**
```bash
# Remove specific repository
uv run python -m src.cli.main remove my-docs

# Remove all collections
uv run python -m src.cli.main remove --all
```

## Configuration

### Database Path

Set the ChromaDB storage location:

**Via environment variable:**
```bash
export HETRIEVER_DB_PATH=/path/to/chroma_data
```

**Via command-line option:**
```bash
uv run python -m src.cli.main --db-path /custom/path search "query"
```

### Logging

Set log level via environment:
```bash
export HETRIEVER_LOG_LEVEL=DEBUG
```

## Development

### Install Development Dependencies

```bash
uv sync --all-extras
```

### Run Tests

```bash
# All tests
just test

# Specific test categories
just test-unit
just test-integration
just test-contract
just test-benchmark
just test-property
```

### Linting and Formatting

```bash
# Check code style
just lint

# Format code
just format

# Check formatting without changes
just format-check
```

### Type Checking

```bash
just typecheck
```

### Clean Build Artifacts

```bash
just clean
```

### Run CI Checks

```bash
just ci
```

## Project Structure

```
hetriever/
├── src/
│   ├── cli/              # CLI commands and formatters
│   ├── cleaning/         # Markdown cleaning pipeline
│   ├── models/           # Data models (Document, Collection, etc.)
│   ├── processing/       # Indexing, chunking, metadata extraction
│   └── storage/          # ChromaDB client and storage
├── tests/
│   ├── benchmarks/       # Performance benchmarks
│   ├── contract/         # Contract tests
│   ├── integration/      # Integration tests
│   ├── property/         # Property-based tests
│   └── unit/             # Unit tests
├── justfile              # Build automation recipes
└── pyproject.toml        # Project configuration
```

## How It Works

1. **File Discovery**: Finds all `.md` files in the target directory, respecting `.gitignore`
2. **Cleaning Pipeline**: Removes Hugo frontmatter, shortcodes, code fence metadata, and normalizes whitespace
3. **Context Extraction**: Extracts heading hierarchy and document structure
4. **Chunking**: Splits documents by headings while preserving context
5. **Metadata Enrichment**: Adds git repository info, file paths, and timestamps
6. **Embedding & Storage**: Generates embeddings and stores in ChromaDB for semantic search

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
