"""Apply generated eval_cases from data/skill_enrichment/ to actual skill files.

Run: python3 scripts/apply_eval_cases.py [--dry-run]
"""

import re
import sys
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parent.parent / "skills"
ENRICHMENT_DIR = Path(__file__).parent.parent / "data" / "skill_enrichment"


def apply_to_skill(skill_path: Path, new_yaml_path: Path, dry_run: bool = False) -> bool:
    """Append new eval_cases to an existing skill file."""
    content = skill_path.read_text()
    if not content.startswith("---"):
        print(f"  [SKIP] {skill_path.name}: no frontmatter")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    try:
        fm = yaml.safe_load(parts[1])
    except Exception:
        print(f"  [SKIP] {skill_path.name}: invalid YAML")
        return False

    if not fm or "eval_cases" not in fm:
        print(f"  [SKIP] {skill_path.name}: no eval_cases section")
        return False

    existing_count = len(fm["eval_cases"])
    new_yaml = new_yaml_path.read_text().strip()

    # Parse new eval_cases
    try:
        new_cases = yaml.safe_load(new_yaml)
        if isinstance(new_cases, list):
            pass
        elif isinstance(new_cases, dict) and "eval_cases" in new_cases:
            new_cases = new_cases["eval_cases"]
        else:
            # Try wrapping in list
            new_cases = yaml.safe_load(f"[{new_yaml}]") if new_yaml.startswith("-") else None
    except Exception:
        # Try as raw list items
        try:
            new_cases = yaml.safe_load(f"eval_cases:\n{new_yaml}")
            if isinstance(new_cases, dict):
                new_cases = new_cases.get("eval_cases", [])
        except Exception:
            print(f"  [FAIL] {skill_path.name}: could not parse new eval_cases")
            return False

    if not new_cases or not isinstance(new_cases, list):
        print(f"  [FAIL] {skill_path.name}: no valid eval_cases parsed")
        return False

    # Dedup by id
    existing_ids = {ec.get("id", "") for ec in fm["eval_cases"]}
    unique_new = [ec for ec in new_cases if ec.get("id") and ec["id"] not in existing_ids]

    if not unique_new:
        print(f"  [SKIP] {skill_path.name}: all new cases are duplicates")
        return False

    if dry_run:
        print(f"  [DRY] {skill_path.name}: would add {len(unique_new)} eval_cases ({existing_count} → {existing_count + len(unique_new)})")
        return True

    # Append to frontmatter
    fm["eval_cases"].extend(unique_new)

    # Bump version if present
    if "version" in fm:
        v = fm["version"]
        try:
            major, minor, patch = str(v).split(".")
            fm["version"] = f"{major}.{minor}.{int(patch) + 1}"
        except Exception:
            pass

    # Rebuild file
    new_content = "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False) + "---" + parts[2]
    skill_path.write_text(new_content)
    print(f"  [OK] {skill_path.name}: added {len(unique_new)} eval_cases ({existing_count} → {existing_count + len(unique_new)})")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not ENRICHMENT_DIR.exists():
        print(f"No enrichment data at {ENRICHMENT_DIR}")
        sys.exit(1)

    enrichment_files = list(ENRICHMENT_DIR.glob("*.yaml"))
    print(f"Found {len(enrichment_files)} enrichment files")

    ok = 0
    for ef in sorted(enrichment_files):
        skill_name = ef.stem + ".md"
        skill_path = SKILLS_DIR / skill_name
        if not skill_path.exists():
            print(f"  [SKIP] {skill_name}: skill file not found")
            continue
        if apply_to_skill(skill_path, ef, dry_run=args.dry_run):
            ok += 1

    print(f"\nApplied: {ok}/{len(enrichment_files)}")


if __name__ == "__main__":
    main()
