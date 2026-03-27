#!/usr/bin/env python3
"""Compress skills to telegraphic English — preserve structure, remove prose.

Rules:
- Keep YAML frontmatter (eval_cases) untouched
- Keep markdown headers (##, ###)
- Keep code blocks verbatim
- Keep bullet points but compress to telegraphic English
- Remove filler words, articles, verbose explanations
- Keep technical terms, function names, patterns
- Output: same file, ~40-60% smaller

No LLM needed — pure rule-based compression.
"""

import os
import re
import sys
from pathlib import Path


def compress_line(line: str) -> str:
    """Compress a single prose line to telegraphic style."""
    if not line.strip():
        return line
    # Skip code, headers, frontmatter, bullets with code
    if line.strip().startswith(("#", "```", "---", "|", "-", "*")) and "`" in line:
        return line
    if line.strip().startswith(("```", "---", "|")):
        return line

    s = line
    # Remove articles
    s = re.sub(r'\b(the|a|an|The|A|An)\s+', '', s)
    # Remove filler phrases
    s = re.sub(r'\b(In order to|in order to)\b', 'To', s)
    s = re.sub(r'\b(make sure|Make sure|ensure that|Ensure that)\b', 'ensure', s)
    s = re.sub(r'\b(This is because|This means that|This ensures that)\b', '→', s)
    s = re.sub(r'\b(for example|For example|e\.g\.|for instance)\b', 'eg', s)
    s = re.sub(r'\b(such as|Such as)\b', 'eg', s)
    s = re.sub(r'\b(in this case|In this case)\b', 'here', s)
    s = re.sub(r'\b(it is important to|It is important to)\b', 'must', s)
    s = re.sub(r'\b(you should|You should|we should|We should)\b', '', s)
    s = re.sub(r'\b(you can|You can|we can|We can)\b', 'can', s)
    s = re.sub(r'\b(please note that|Please note that|Note that|note that)\b', 'NB:', s)
    s = re.sub(r'\b(However|however|Nevertheless|nevertheless)\b', 'but', s)
    s = re.sub(r'\b(Additionally|additionally|Furthermore|furthermore|Moreover|moreover)\b', '+', s)
    s = re.sub(r'\b(Therefore|therefore|Thus|thus|Hence|hence)\b', '→', s)
    s = re.sub(r'\b(which means|that means)\b', '→', s)
    s = re.sub(r'\b(is used to|are used to|is designed to)\b', '→', s)
    s = re.sub(r'\b(instead of|Instead of)\b', 'not', s)
    s = re.sub(r'\b(whether or not)\b', 'if', s)
    s = re.sub(r'\b(as well as)\b', '+', s)
    s = re.sub(r'\b(When you|when you|If you|if you)\b', 'when', s)
    s = re.sub(r'\b(will be|would be|should be|could be|might be)\b', 'is', s)
    s = re.sub(r'\b(that is|which is|that are|which are)\b', '=', s)
    s = re.sub(r'\b(does not|do not|don\'t|doesn\'t)\b', "won't", s)
    s = re.sub(r'\b(is not|are not|isn\'t|aren\'t)\b', "!=", s)
    # Remove "it/this/that" sentence starters
    s = re.sub(r'^(It|This|That)\s+(is|was|will|can|should)\s+', '', s)
    # Compress whitespace
    s = re.sub(r'  +', ' ', s)
    return s


def compress_skill(content: str) -> str:
    """Compress a skill file preserving frontmatter and code blocks."""
    lines = content.split('\n')
    out = []
    in_frontmatter = False
    in_code_block = False

    for i, line in enumerate(lines):
        # Frontmatter — keep untouched
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            out.append(line)
            continue
        if in_frontmatter:
            out.append(line)
            if line.strip() == '---':
                in_frontmatter = False
            continue

        # Code blocks — keep untouched
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            out.append(line)
            continue
        if in_code_block:
            out.append(line)
            continue

        # Headers — keep but compress
        if line.strip().startswith('#'):
            out.append(compress_line(line))
            continue

        # Empty lines — keep max 1
        if not line.strip():
            if out and not out[-1].strip():
                continue  # skip double empty
            out.append('')
            continue

        # Prose — compress
        out.append(compress_line(line))

    return '\n'.join(out)


def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/sylvain/_MACARON-SOFTWARE/_SOFTWARE_FACTORY/skills")

    total_before = 0
    total_after = 0
    compressed = 0

    for f in sorted(skills_dir.glob("*.md")):
        content = f.read_text(errors='ignore')
        before = len(content)
        if before < 2000:  # Skip small files
            continue

        after_content = compress_skill(content)
        after = len(after_content)

        if after < before * 0.95:  # Only write if >5% reduction
            f.write_text(after_content)
            ratio = (1 - after/before) * 100
            compressed += 1
            total_before += before
            total_after += after

    print(f"Compressed {compressed} skills")
    if total_before > 0:
        print(f"Before: {total_before/1024:.0f} KB → After: {total_after/1024:.0f} KB ({(1-total_after/total_before)*100:.0f}% reduction)")


if __name__ == "__main__":
    main()
