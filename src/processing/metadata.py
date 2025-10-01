import subprocess
from pathlib import Path


def enrich_metadata(
    base_metadata: dict,
    file_path: Path,
    repository_name: str,
) -> dict[str, str | bool | list[str]]:
    """Enrich chunk metadata with file and git information.

    Combines base metadata from frontmatter with file path, repository name,
    and git metadata (commit SHA, last modified date, branch).

    Args:
        base_metadata: Base metadata dictionary (typically from frontmatter).
        file_path: Path to the source file.
        repository_name: Name of the repository being indexed.

    Returns:
        Enriched metadata dictionary with file_path, repository, and optional git fields.
    """
    metadata: dict[str, str | bool | list[str]] = {**base_metadata}

    metadata["file_path"] = str(file_path)
    metadata["repository"] = repository_name

    try:
        git_info = get_git_info(file_path)
        metadata.update(git_info)
    except Exception:
        pass

    return metadata


def get_git_info(file_path: Path) -> dict[str, str]:
    """Extract git metadata for a file.

    Runs git commands to retrieve last commit SHA, last modified date,
    and current branch for the specified file.

    Args:
        file_path: Path to the file to get git info for.

    Returns:
        Dictionary with optional keys: last_commit_sha, last_modified, git_branch.
        Returns empty dict if git commands fail or file not in git.
    """
    git_info: dict[str, str] = {}

    try:
        last_commit = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=file_path.parent,
        )
        if last_commit.stdout.strip():
            git_info["last_commit_sha"] = last_commit.stdout.strip()

        last_modified = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=file_path.parent,
        )
        if last_modified.stdout.strip():
            git_info["last_modified"] = last_modified.stdout.strip()

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=file_path.parent,
        )
        if branch.stdout.strip():
            git_info["git_branch"] = branch.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return git_info
