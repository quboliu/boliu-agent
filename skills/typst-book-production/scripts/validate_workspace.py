#!/usr/bin/env python3
"""Validate the canonical root layout and edition matrix for one book."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME_RE = re.compile(r"^name:\s*([^\s#]+)\s*$", re.MULTILINE)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def require_dir(path: Path, failures: list[str]) -> None:
    if not path.is_dir():
        fail(f"missing directory: {path}", failures)


def require_file(path: Path, failures: list[str]) -> None:
    if not path.is_file():
        fail(f"missing file: {path}", failures)


def check_local_skill(workspace: Path, slug: str, failures: list[str]) -> None:
    skill = workspace / ".agents" / "skills" / slug / "SKILL.md"
    require_file(skill, failures)
    if not skill.is_file():
        return
    try:
        text = skill.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read local skill {skill}: {exc}", failures)
        return
    match = NAME_RE.search(text)
    if match is None:
        fail(f"local skill has no frontmatter name: {skill}", failures)
    elif match.group(1) != slug:
        fail(
            f"local skill name {match.group(1)!r} does not match slug {slug!r}",
            failures,
        )


def check_markdown(markdown: Path, failures: list[str]) -> None:
    chapters = markdown / "chapters"
    images = markdown / "images"
    require_dir(chapters, failures)
    require_dir(images, failures)
    if not markdown.is_dir():
        return
    unexpected = sorted(
        path.name for path in markdown.iterdir()
        if path.name not in {"chapters", "images"}
    )
    if unexpected:
        fail(
            "unexpected entries in Markdown root: " + ", ".join(unexpected),
            failures,
        )
    if chapters.is_dir():
        chapter_files = [path for path in chapters.rglob("*") if path.is_file()]
        if not chapter_files:
            fail(f"no Markdown chapters under {chapters}", failures)
        invalid = sorted(
            path.relative_to(chapters).as_posix()
            for path in chapter_files
            if path.suffix.lower() != ".md"
        )
        if invalid:
            fail("non-Markdown files in chapters: " + ", ".join(invalid), failures)


def check_edition(edition: Path, failures: list[str]) -> None:
    required_dirs = (
        "assets/covers/boliu",
        "assets/covers/source",
        "assets/figures",
        "assets/fonts",
        "book/chapters",
        "editorial/content-audit",
        "output/audit",
        "output/build",
        "output/preview",
    )
    required_files = (
        "book/covers.typ",
        "book/core.typ",
        "book/main.typ",
        "book/matter.typ",
        "book/template.typ",
        "book.toml",
        "source-map.json",
    )
    for relative in required_dirs:
        require_dir(edition / relative, failures)
    for relative in required_files:
        require_file(edition / relative, failures)
    allowed_roots = {
        "assets",
        "book",
        "editorial",
        "output",
        "book.toml",
        "source-map.json",
    }
    unexpected_roots = sorted(
        path.name for path in edition.iterdir() if path.name not in allowed_roots
    )
    if unexpected_roots:
        fail(
            f"unexpected entries in edition root {edition}: "
            + ", ".join(unexpected_roots),
            failures,
        )
    for forbidden in ("source", "sources", "raw", "markdown", "scripts"):
        if (edition / forbidden).exists():
            fail(f"forbidden competing role in edition: {edition / forbidden}", failures)


def check_lowercase_generated_names(
    workspace: Path, raw: Path, failures: list[str]
) -> None:
    bad: list[str] = []
    for path in workspace.rglob("*"):
        try:
            path.relative_to(raw)
        except ValueError:
            pass
        else:
            continue
        relative = path.relative_to(workspace)
        if any(part == ".git" for part in relative.parts):
            continue
        if relative == Path(".agents") / "skills" / workspace.name / "SKILL.md":
            continue
        if re.search(r"[A-Z]", relative.as_posix()):
            bad.append(relative.as_posix())
    if bad:
        fail(
            "uppercase English characters in generated paths: " + ", ".join(bad),
            failures,
        )


def validate(workspace: Path, source_language: str) -> list[str]:
    failures: list[str] = []
    workspace = workspace.resolve()
    slug = workspace.name
    if SLUG_RE.fullmatch(slug) is None:
        fail(f"workspace name is not a lowercase English slug: {slug}", failures)

    raw = workspace / f"{slug}-raw"
    markdown = workspace / f"{slug}-markdown"
    require_dir(raw, failures)
    require_dir(markdown, failures)
    if raw.is_dir() and not any(path.is_file() for path in raw.rglob("*")):
        fail(f"raw directory contains no source material: {raw}", failures)
    if raw.is_dir() and any(
        path.suffix.lower() == ".typ" for path in raw.rglob("*")
    ):
        fail(f"Typst files are forbidden in raw material: {raw}", failures)
    check_markdown(markdown, failures)
    check_local_skill(workspace, slug, failures)

    suffixes = ("zh",) if source_language == "zh" else ("en", "dual", "zh")
    expected_editions = {f"{slug}-typst-{suffix}" for suffix in suffixes}
    for name in sorted(expected_editions):
        edition = workspace / name
        require_dir(edition, failures)
        if edition.is_dir():
            check_edition(edition, failures)
    actual_editions = (
        {
            path.name
            for path in workspace.iterdir()
            if path.is_dir() and path.name.startswith(f"{slug}-typst-")
        }
        if workspace.is_dir()
        else set()
    )
    unexpected_editions = sorted(actual_editions - expected_editions)
    if unexpected_editions:
        fail("unexpected Typst editions: " + ", ".join(unexpected_editions), failures)

    allowed_roots = {".agents", ".git", raw.name, markdown.name, *expected_editions}
    if workspace.is_dir():
        unexpected_roots = sorted(
            path.name for path in workspace.iterdir()
            if path.name not in allowed_roots
        )
        if unexpected_roots:
            fail(
                "unexpected workspace-root entries: " + ", ".join(unexpected_roots),
                failures,
            )
    check_lowercase_generated_names(workspace, raw, failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-dir", required=True, type=Path)
    parser.add_argument("--source-language", required=True, choices=("zh", "en"))
    args = parser.parse_args()
    failures = validate(args.workspace_dir, args.source_language)
    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
