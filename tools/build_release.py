from __future__ import annotations

import argparse
import re
import shutil
import tarfile
from pathlib import Path


APP_NAME = "PlayerokCardinal"
PLACEHOLDERS = {
    "__GITHUB_REPO__": "OWNER/REPO",
    "__GITHUB_REF__": "main",
}

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".idea",
    ".venv",
    "__pycache__",
    "build",
    "configs",
    "dist",
    "logs",
    "release-build",
    "storage",
    "venv",
    "venv2",
}

EXCLUDED_FILES = {
    "0.13.0",
    "0.34.0",
    "0.4.6",
    "3.10.0",
    "3.4.3",
    "4.12.3",
    "4.2.0",
    "4.67.1",
    "5.2.2",
    "5.9.4",
    "6.9.0",
    "9.3.0",
    "backup.zip",
}

TEXT_SUFFIXES = {".md", ".txt", ".py", ".bat", ".sh", ".service", ".yml", ".yaml"}


def detect_version(repo_root: Path) -> str:
    main_py = (repo_root / "main.py").read_text(encoding="utf-8")
    match = re.search(r'^VERSION = "([^"]+)"', main_py, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not detect VERSION in main.py")
    return match.group(1)


def ignore_filter(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    dir_path = Path(directory)
    for name in names:
        path = dir_path / name
        if name in EXCLUDED_DIRS and path.is_dir():
            ignored.add(name)
            continue
        if name in EXCLUDED_FILES and path.is_file():
            ignored.add(name)
            continue
        if path.is_file() and path.suffix in {".pyc", ".pyo", ".log"}:
            ignored.add(name)
    return ignored


def replace_placeholders(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        if text != original:
            path.write_text(text, encoding="utf-8")


def prepare_runtime_layout(stage_root: Path) -> None:
    for rel in [
        "configs",
        "logs",
        "storage/cache",
        "storage/products",
        "plugins",
    ]:
        path = stage_root / rel
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("", encoding="utf-8")

    (stage_root / "configs" / "auto_delivery.cfg").write_text("", encoding="utf-8")
    (stage_root / "configs" / "auto_response.cfg").write_text("", encoding="utf-8")


def build_archives(stage_root: Path, output_dir: Path, version: str) -> tuple[Path, Path]:
    windows_archive = output_dir / f"{APP_NAME}-{version}-windows.zip"
    linux_archive = output_dir / f"{APP_NAME}-{version}-linux.tar.gz"

    if windows_archive.exists():
        windows_archive.unlink()
    if linux_archive.exists():
        linux_archive.unlink()

    shutil.make_archive(
        base_name=str(windows_archive.with_suffix("")),
        format="zip",
        root_dir=stage_root.parent,
        base_dir=stage_root.name,
    )

    with tarfile.open(linux_archive, "w:gz") as tar:
        tar.add(stage_root, arcname=stage_root.name)

    return windows_archive, linux_archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Build clean GitHub release archives.")
    parser.add_argument("--repo-root", default=None, help="Repository root. Defaults to the current script parent.")
    parser.add_argument("--output-dir", default=None, help="Output directory for built archives.")
    parser.add_argument("--github-repo", default=PLACEHOLDERS["__GITHUB_REPO__"], help="GitHub repo slug, for example owner/repo.")
    parser.add_argument("--github-ref", default=None, help="GitHub tag or ref, for example v1.1.2.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    version = detect_version(repo_root)
    github_ref = args.github_ref or f"v{version}"
    output_dir = Path(args.output_dir).resolve() if args.output_dir else repo_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_root = output_dir / f"{APP_NAME}-{version}"
    if stage_root.exists():
        shutil.rmtree(stage_root)

    shutil.copytree(repo_root, stage_root, ignore=ignore_filter)
    prepare_runtime_layout(stage_root)
    replace_placeholders(
        stage_root,
        {
            "__APP_VERSION__": version,
            "__GITHUB_REPO__": args.github_repo,
            "__GITHUB_REF__": github_ref,
        },
    )

    windows_archive, linux_archive = build_archives(stage_root, output_dir, version)

    print(f"Stage: {stage_root}")
    print(f"Windows: {windows_archive}")
    print(f"Linux: {linux_archive}")


if __name__ == "__main__":
    main()
