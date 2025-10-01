# hetriever

**H**ugo documentation r**etriever** with vector embeddings for semantic search.

A Python tool that indexes markdown documentation from Hugo sites and provides semantic search capabilities using ChromaDB with high-quality embeddings (`sentence-transformers/all-mpnet-base-v2`).

## Features

- **Semantic Search**: Find documentation by meaning, not just keywords
- **High-Quality Embeddings**: Uses `all-mpnet-base-v2` for superior search accuracy
- **Multi-Repository Support**: Index and search across multiple documentation repositories
- **Hugo-Aware Cleaning**: Removes frontmatter, shortcodes, and Hugo-specific syntax
- **Context-Preserving Chunking**: Maintains heading hierarchy and document structure
- **Git-Aware Metadata**: Extracts repository information from git context
- **Flexible CLI**: Simple commands for indexing, searching, and managing collections

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

### Install

```bash
git clone https://github.com/yourusername/hetriever.git
cd hetriever
just init
```

Or manually:

```bash
git clone https://github.com/yourusername/hetriever.git
cd hetriever
git submodule update --init --recursive
uv sync --dev
```

## Quick Start

### 1. Index Documentation

Index a Hugo documentation repository:

```bash
uv run ch index /path/to/hugo/docs
```

Index a specific repository name:

```bash
uv run ch index /path/to/docs --repo my-docs
```

### 2. Search Documentation

Search indexed documentation:

```bash
uv run ch search "how to configure authentication"
```

Limit results:

```bash
uv run ch search "deployment guide" --limit 5
```

Filter by repository:

```bash
uv run ch search "API reference" --repo my-docs
```

### 3. List Collections

View all indexed repositories:

```bash
uv run ch list
```

### 4. Remove Collections

Remove a specific repository:

```bash
uv run ch remove my-docs
```

## CLI Commands

### `index`

Index markdown documentation from a directory.

```bash
uv run ch index [OPTIONS] PATH
```

**Options:**

- `--repo TEXT`: Repository name (defaults to directory name)
- `--force`: Force reindex even if unchanged
- `--verbose, -v`: Show detailed processing logs
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Example:**

```bash
uv run ch index /path/to/docs --repo production-docs --verbose
```

### `search`

Search indexed documentation with semantic search.

```bash
uv run ch search [OPTIONS] QUERY
```

**Options:**

- `--repo TEXT`: Filter by repository name
- `--limit INTEGER`: Maximum results to return (default: 10)
- `--format [text|json]`: Output format (default: text)
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Example:**

```bash
uv run ch search "authentication setup" --repo my-docs --limit 5
```

### `list`

List all indexed repository collections.

```bash
uv run ch list [OPTIONS]
```

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

### `remove`

Remove indexed repository collections.

```bash
uv run ch remove [OPTIONS] REPO
```

**Options:**

- `--confirm`: Skip confirmation prompt
- `--db-path PATH`: ChromaDB storage path (default: `./chroma_data`)

**Example:**

```bash
uv run ch remove my-docs --confirm
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
uv run ch --db-path /custom/path search "query"
```

## Development

### Setup

```bash
just init
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

### Clean Build Artifacts

```bash
just clean
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
