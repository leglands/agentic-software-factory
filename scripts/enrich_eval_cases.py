"""Batch enrich eval_cases for skills with <5 eval_cases.

Uses MiniMax M2.7 via opencode to generate new eval_cases for each skill.
Run: python3 scripts/enrich_eval_cases.py [--limit N] [--dry-run]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"
OPENCODE = "/opt/homebrew/bin/opencode"
MODEL = "minimax/MiniMax-M2.7"
TARGET_EVALS = 15
MIN_EVALS = 5  # Only enrich skills with fewer than this


def parse_frontmatter(content: str) -> tuple[dict | None, str, str]:
    """Parse YAML frontmatter. Returns (frontmatter_dict, frontmatter_raw, body)."""
    if not content.startswith("---"):
        return None, "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "", content
    import yaml
    try:
        fm = yaml.safe_load(parts[1])
        return fm, parts[1], parts[2]
    except Exception:
        return None, parts[1], parts[2]


def count_eval_cases(skill_path: Path) -> int:
    content = skill_path.read_text()
    fm, _, _ = parse_frontmatter(content)
    if fm and "eval_cases" in fm:
        return len(fm["eval_cases"])
    return 0


def enrich_skill(skill_path: Path, dry_run: bool = False) -> bool:
    """Call MiniMax to generate new eval_cases for a skill."""
    name = skill_path.stem
    current_count = count_eval_cases(skill_path)
    needed = TARGET_EVALS - current_count
    if needed <= 0:
        return False

    prompt = (
        f"Read the skill file at {skill_path} and generate {needed} new eval_cases "
        f"to add (currently has {current_count}, target is {TARGET_EVALS}). "
        f"Each eval_case needs: id (unique), prompt (realistic scenario), "
        f"checks (deterministic: regex, length_min, has_keyword, not_regex, no_placeholder), "
        f"expectations (for LLM judge). Checks must be DISCRIMINANT — a stub must FAIL. "
        f"Output ONLY valid YAML for the new eval_cases list items (starting with '  - id:')."
    )

    if dry_run:
        print(f"  [DRY] Would enrich {name}: {current_count} → {TARGET_EVALS}")
        return True

    try:
        result = subprocess.run(
            [OPENCODE, "run", "-m", MODEL, prompt],
            capture_output=True, text=True, timeout=120,
        )
        output = result.stdout.strip()
        if not output or "Error:" in output:
            print(f"  [FAIL] {name}: opencode error")
            return False

        # Extract YAML from output (between ```yaml and ```)
        yaml_match = re.search(r"```ya?ml\s*\n(.*?)```", output, re.DOTALL)
        if yaml_match:
            new_yaml = yaml_match.group(1).strip()
        else:
            # Try to find eval_case blocks directly
            lines = output.split("\n")
            yaml_lines = [l for l in lines if l.strip().startswith("- id:") or l.strip().startswith("prompt:") or l.strip().startswith("checks:") or l.strip().startswith("expectations:") or l.strip().startswith("-") or l.strip().startswith("\"")]
            new_yaml = "\n".join(yaml_lines)

        if not new_yaml or "- id:" not in new_yaml:
            print(f"  [FAIL] {name}: no valid eval_cases in output")
            return False

        # Save raw output for manual review
        out_dir = Path(__file__).parent.parent / "data" / "skill_enrichment"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{name}.yaml").write_text(new_yaml)
        print(f"  [OK] {name}: generated {needed} new eval_cases → {out_dir / f'{name}.yaml'}")
        return True

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {name}")
        return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20, help="Max skills to process")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-size", type=int, default=3000, help="Min skill file size (skip tiny)")
    args = parser.parse_args()

    # Find skills needing enrichment
    candidates = []
    for f in sorted(SKILLS_DIR.iterdir()):
        if not f.suffix == ".md":
            continue
        if f.stat().st_size < args.min_size:
            continue
        count = count_eval_cases(f)
        if count < MIN_EVALS:
            candidates.append((f, count))

    candidates.sort(key=lambda x: (-x[0].stat().st_size, x[1]))
    print(f"Found {len(candidates)} skills with <{MIN_EVALS} eval_cases")
    print(f"Processing top {args.limit}...")

    ok = 0
    for skill_path, count in candidates[:args.limit]:
        print(f"\n[{ok+1}/{args.limit}] {skill_path.name} ({count} evals, {skill_path.stat().st_size//1024}KB)")
        if enrich_skill(skill_path, dry_run=args.dry_run):
            ok += 1

    print(f"\nDone: {ok}/{min(len(candidates), args.limit)} enriched")


if __name__ == "__main__":
    main()
