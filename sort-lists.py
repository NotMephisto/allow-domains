#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

DEFAULT_PATTERNS = [
    "Categories/*.lst",
    "Services/*.lst",
]

def sort_content(original: str) -> str:
    lines = original.splitlines()

    groups: list[list[str]] = [[]]
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            if groups[-1]:
                groups.append([])
        else:
            groups[-1].append(stripped)

    if groups and not groups[-1]:
        groups.pop()

    out_lines: list[str] = []
    for i, group in enumerate(groups):
        unique_sorted = sorted(dict.fromkeys(group), key=str.lower)
        out_lines.extend(unique_sorted)
        if i != len(groups) - 1:
            out_lines.append("")

    return "\n".join(out_lines) + "\n"


def collect_files(root: Path, patterns: list[str]) -> list[Path]:
    seen = set()
    files = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("patterns", nargs="*", default=DEFAULT_PATTERNS,
                         help="glob patterns relative to --root (default: RAW list locations)")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--check", action="store_true",
                         help="don't write files; exit 1 if any file is not sorted")
    args = parser.parse_args()

    root = Path(args.root)
    changed_files = []

    for path in collect_files(root, args.patterns):
        original = path.read_text(encoding="utf-8")
        new_content = sort_content(original)
        if new_content != original:
            changed_files.append(str(path.relative_to(root)))
            if not args.check:
                path.write_text(new_content, encoding="utf-8")

    if changed_files:
        label = "Not sorted" if args.check else "Sorted"
        print(f"{label}:")
        for f in changed_files:
            print(f" - {f}")
        if args.check:
            sys.exit(1)
    else:
        print("All files already sorted.")


if __name__ == "__main__":
    main()
