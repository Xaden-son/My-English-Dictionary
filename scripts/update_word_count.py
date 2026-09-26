#!/usr/bin/env python3
"""Count vocabulary entries and refresh the word counter in README.md.

Every "## " heading in a collection file (NN-Name.md) is one word.
The counter lives between the WORD-COUNT markers in README.md.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START = "<!-- WORD-COUNT:START -->"
END = "<!-- WORD-COUNT:END -->"


def count_words(path: Path) -> int:
    count = 0
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        elif not in_code and line.startswith("## "):
            count += 1
    return count


def collection_name(path: Path) -> str:
    # "01-My-Own-Dictionary.md" -> "My Own Dictionary"
    return re.sub(r"^\d+-", "", path.stem).replace("-", " ")


def build_block() -> str:
    files = sorted(ROOT.glob("[0-9][0-9]-*.md"))
    rows = [(f, count_words(f)) for f in files]
    total = sum(n for _, n in rows)

    lines = [
        START,
        f"**🔤 Total words: {total}**",
        "",
        "| Collection | Words |",
        "| --- | ---: |",
    ]
    lines += [f"| [{collection_name(f)}](./{f.name}) | {n} |" for f, n in rows]
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print(f"README.md is missing the {START} / {END} markers.", file=sys.stderr)
        return 1

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    updated = pattern.sub(lambda _: build_block(), text, count=1)

    if updated == text:
        print("Word count already up to date.")
    else:
        README.write_text(updated, encoding="utf-8")
        print("README.md word count updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
