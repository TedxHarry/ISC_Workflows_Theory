from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MODULES = ['00-orientation.md', '01-the-workflow-model.md', '02-data-variables-and-expressions.md', '03-triggers.md', '04-operators-and-logic.md', '05-actions.md', '06-forms-and-interactive-workflows.md', '07-testing-debugging-and-execution.md', '08-operations-limits-and-governance.md', '09-when-to-use-workflows.md', '10-use-case-patterns.md', '11-challenges-and-edge-cases.md', '12-readiness-and-paper-design.md']
SUBMODULES = ['02-1-data-and-payload-shape.md', '02-2-variables-and-jsonpath.md', '03-1-choosing-the-right-trigger.md', '03-2-filters-and-specialized-triggers.md', '05-1-action-contracts-and-core-actions.md', '05-2-error-handling-external-actions-and-success-boundaries.md', '08-1-operating-a-workflow.md', '08-2-limits-change-and-governance.md', '09-1-capability-ownership.md', '09-2-architecture-decisions-and-tradeoffs.md', '10-1-pattern-method-and-core-patterns.md', '10-2-working-engineer-patterns.md', '10-3-advanced-patterns-and-pattern-transfer.md', '11-1-repetition-partial-failure-and-concurrency.md', '11-2-scale-correlation-and-external-state.md', '12-1-paper-design-framework.md', '12-2-capstone-design-lab.md']
READING_UNITS = ['00-orientation.md', '01-the-workflow-model.md', '02-1-data-and-payload-shape.md', '02-2-variables-and-jsonpath.md', '03-1-choosing-the-right-trigger.md', '03-2-filters-and-specialized-triggers.md', '04-operators-and-logic.md', '05-1-action-contracts-and-core-actions.md', '05-2-error-handling-external-actions-and-success-boundaries.md', '06-forms-and-interactive-workflows.md', '07-testing-debugging-and-execution.md', '08-1-operating-a-workflow.md', '08-2-limits-change-and-governance.md', '09-1-capability-ownership.md', '09-2-architecture-decisions-and-tradeoffs.md', '10-1-pattern-method-and-core-patterns.md', '10-2-working-engineer-patterns.md', '10-3-advanced-patterns-and-pattern-transfer.md', '11-1-repetition-partial-failure-and-concurrency.md', '11-2-scale-correlation-and-external-state.md', '12-1-paper-design-framework.md', '12-2-capstone-design-lab.md']
READER_PAGES = CANONICAL_MODULES + SUBMODULES
CHECK_LINKS = READER_PAGES + ["README.md", "_sidebar.md", "AUTHORING-GUIDE.md", "COURSE-STATUS.md"]
errors = []


def read_utf8(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    text = read_utf8(path)
    if text is not None and "\u2014" in text:
        errors.append(f"Em dash found: {path.relative_to(ROOT)}")

for name in READER_PAGES:
    path = ROOT / name
    if not path.exists():
        errors.append(f"Missing course page: {name}")
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = []
    in_fence = False
    for line_number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+\S", line)
        if match:
            headings.append((line_number, len(match.group(1)), line))
    h1s = [heading for heading in headings if heading[1] == 1]
    if len(h1s) != 1:
        errors.append(f"{name}: expected exactly one H1, found {len(h1s)}")
    elif not h1s[0][2].startswith("# Module "):
        errors.append(f'{name}: H1 must start with "# Module "')
    previous = None
    for line_number, level, line in headings:
        if previous is not None and level > previous + 1:
            errors.append(f"{name}:{line_number}: heading level jumps from H{previous} to H{level}: {line}")
        previous = level

link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
for name in CHECK_LINKS:
    path = ROOT / name
    if not path.exists():
        continue
    content = path.read_text(encoding="utf-8")
    if "chatgpt.com/" in content:
        errors.append(f"{name}: contains an absolute chatgpt.com link")
    for target in link_pattern.findall(content):
        target = target.strip().split()[0].strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{name}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{name}: broken internal link: {target}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
sidebar = (ROOT / "_sidebar.md").read_text(encoding="utf-8")
for module in CANONICAL_MODULES:
    if module not in readme:
        errors.append(f"README.md: missing canonical module link {module}")
    if module not in sidebar:
        errors.append(f"_sidebar.md: missing canonical module link {module}")
for unit in READING_UNITS:
    if unit not in sidebar:
        errors.append(f"_sidebar.md: missing reading-unit link {unit}")

if errors:
    print("Content quality checks failed:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print(f"Content quality checks passed for {len(CANONICAL_MODULES)} conceptual modules and {len(READING_UNITS)} reading units.")
