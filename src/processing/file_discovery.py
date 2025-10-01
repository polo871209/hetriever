from pathlib import Path


def discover_markdown_files(root_path: Path, pattern: str = "**/*.md") -> list[Path]:
    """Discover markdown files in a directory using glob pattern.

    Args:
        root_path: Root directory to search from.
        pattern: Glob pattern for file matching (default: '**/*.md' for recursive search).

    Returns:
        Sorted list of Path objects for discovered markdown files.

    Raises:
        FileNotFoundError: If root_path does not exist.
        NotADirectoryError: If root_path is not a directory.
    """
    if not root_path.exists():
        raise FileNotFoundError(f"Root path does not exist: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root_path}")

    markdown_files = sorted(root_path.glob(pattern))
    return [f for f in markdown_files if f.is_file()]


def filter_by_git_submodule(files: list[Path], submodule_path: Path) -> list[Path]:
    """Filter file list to only include files within a git submodule.

    Args:
        files: List of file paths to filter.
        submodule_path: Path to the git submodule directory.

    Returns:
        Filtered list containing only files within the submodule path.
    """
    resolved_submodule = submodule_path.resolve()
    return [
        f
        for f in files
        if resolved_submodule in f.resolve().parents or f.resolve() == resolved_submodule
    ]
