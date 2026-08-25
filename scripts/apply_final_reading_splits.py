from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]


def make_split(source_name, marker, part1_name, part1_title, part2_name, part2_title, landing):
    path = ROOT / source_name
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise SystemExit(f"Marker not found in {source_name}: {marker}")
    before, after = text.split(marker, 1)
    lines = before.splitlines()
    if not lines or not lines[0].startswith("# Module "):
        raise SystemExit(f"Unexpected H1 in {source_name}")
    lines[0] = "# " + part1_title
    (ROOT / part1_name).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    (ROOT / part2_name).write_text(("# " + part2_title + "\n\n" + marker + after).rstrip() + "\n", encoding="utf-8")
    path.write_text(landing.rstrip() + "\n", encoding="utf-8")


make_split(
    "04-operators-and-logic.md",
    "## Engineering Step-Up: Loops",
    "04-1-decisions-guards-and-variables.md",
    "Module 04.1: Decisions, Guards & Variables",
    "04-2-loops-and-repeated-logic.md",
    "Module 04.2: Loops & Repeated Logic",
    """# Module 04: Operators & Logic

How a running Workflow makes decisions, guards assumptions, shapes data, and repeats work deliberately.

This module is divided into shorter reading units so decision logic and repeated-work logic each have a natural stopping point.

## Reading path

1. [Module 04.1: Decisions, Guards & Variables](04-1-decisions-guards-and-variables.md)
   Build post-start logic with comparisons, branches, combined conditions, type guards, and Workflow variables.
2. [Module 04.2: Loops & Repeated Logic](04-2-loops-and-repeated-logic.md)
   Decide when repetition is real, choose parallel or serial processing, and reason about loop scope, failure, and scale.

**Start here:** [Module 04.1: Decisions, Guards & Variables](04-1-decisions-guards-and-variables.md)

The numbered parts are one module. Read them in order on a first pass; return directly to a part later when you need it as a reference.""",
)

make_split(
    "06-forms-and-interactive-workflows.md",
    "## 6. Core: Information is not approval",
    "06-1-forms-input-and-human-delay.md",
    "Module 06.1: Forms, Input & Human Delay",
    "06-2-approvals-and-interactive-processes.md",
    "Module 06.2: Approvals & Interactive Processes",
    """# Module 06: Forms, Approvals & Interactive Workflows

Choose the right human-interaction model for intake, assigned response, governed approval, and delegated interactive work.

This module is divided into shorter reading units so information gathering and governed decision-making do not compete for attention in one long session.

## Reading path

1. [Module 06.1: Forms, Input & Human Delay](06-1-forms-input-and-human-delay.md)
   Distinguish intake from assigned response and design explicitly for deadlines, cancellation, and human delay.
2. [Module 06.2: Approvals & Interactive Processes](06-2-approvals-and-interactive-processes.md)
   Separate information from approval, reason about Adaptive Approvals, and choose interactive process patterns deliberately.

**Start here:** [Module 06.1: Forms, Input & Human Delay](06-1-forms-input-and-human-delay.md)

The numbered parts are one module. Read them in order on a first pass; return directly to a part later when you need it as a reference.""",
)

make_split(
    "07-testing-debugging-and-execution.md",
    "## 7. Core: Question 4: What did that action actually guarantee?",
    "07-1-safe-testing-and-first-divergence.md",
    "Module 07.1: Safe Testing & First Divergence",
    "07-2-boundary-diagnosis-and-retesting.md",
    "Module 07.2: Boundary Diagnosis & Retesting",
    """# Module 07: Testing, Debugging & Execution

Diagnose Workflow behavior in a disciplined order instead of changing steps and hoping the next run works.

This module is divided into shorter reading units so safe observation and deeper boundary diagnosis can be practiced separately.

## Reading path

1. [Module 07.1: Safe Testing & First Divergence](07-1-safe-testing-and-first-divergence.md)
   Test safely, verify that execution started, inspect the data that arrived, and locate the first unexpected value.
2. [Module 07.2: Boundary Diagnosis & Retesting](07-2-boundary-diagnosis-and-retesting.md)
   Interpret action guarantees, identify the owning system or process, classify the divergence, and retest one hypothesis at a time.

**Start here:** [Module 07.1: Safe Testing & First Divergence](07-1-safe-testing-and-first-divergence.md)

The numbered parts are one module. Read them in order on a first pass; return directly to a part later when you need it as a reference.""",
)

sidebar_path = ROOT / "_sidebar.md"
sidebar = sidebar_path.read_text(encoding="utf-8")
sidebar = sidebar.replace(
    "- [04: Operators & Logic](04-operators-and-logic.md)\n",
    "- [04: Operators & Logic](04-operators-and-logic.md)\n  - [04.1: Decisions, Guards & Variables](04-1-decisions-guards-and-variables.md)\n  - [04.2: Loops & Repeated Logic](04-2-loops-and-repeated-logic.md)\n",
)
sidebar = sidebar.replace(
    "- [06: Forms, Approvals & Interactive Workflows](06-forms-and-interactive-workflows.md)\n",
    "- [06: Forms, Approvals & Interactive Workflows](06-forms-and-interactive-workflows.md)\n  - [06.1: Forms, Input & Human Delay](06-1-forms-input-and-human-delay.md)\n  - [06.2: Approvals & Interactive Processes](06-2-approvals-and-interactive-processes.md)\n",
)
sidebar = sidebar.replace(
    "- [07: Testing, Debugging & Execution](07-testing-debugging-and-execution.md)\n",
    "- [07: Testing, Debugging & Execution](07-testing-debugging-and-execution.md)\n  - [07.1: Safe Testing & First Divergence](07-1-safe-testing-and-first-divergence.md)\n  - [07.2: Boundary Diagnosis & Retesting](07-2-boundary-diagnosis-and-retesting.md)\n",
)
sidebar_path.write_text(sidebar, encoding="utf-8")

readme_path = ROOT / "README.md"
readme_path.write_text(readme_path.read_text(encoding="utf-8").replace("13 modules · 22 reading units", "13 modules · 25 reading units"), encoding="utf-8")

index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")
replacements = {
    "      { path: '04-operators-and-logic', title: 'Module 04: Operators & Logic', category: 'Building Blocks', moduleNumber: '04', part: null, partCount: 1 },": "      { path: '04-1-decisions-guards-and-variables', title: 'Module 04.1: Decisions, Guards & Variables', category: 'Building Blocks', moduleNumber: '04', part: 1, partCount: 2 },\n      { path: '04-2-loops-and-repeated-logic', title: 'Module 04.2: Loops & Repeated Logic', category: 'Building Blocks', moduleNumber: '04', part: 2, partCount: 2 },",
    "      { path: '06-forms-and-interactive-workflows', title: 'Module 06: Forms, Approvals & Interactive Workflows', category: 'Building Blocks', moduleNumber: '06', part: null, partCount: 1 },": "      { path: '06-1-forms-input-and-human-delay', title: 'Module 06.1: Forms, Input & Human Delay', category: 'Building Blocks', moduleNumber: '06', part: 1, partCount: 2 },\n      { path: '06-2-approvals-and-interactive-processes', title: 'Module 06.2: Approvals & Interactive Processes', category: 'Building Blocks', moduleNumber: '06', part: 2, partCount: 2 },",
    "      { path: '07-testing-debugging-and-execution', title: 'Module 07: Testing, Debugging & Execution', category: 'Operating Workflows', moduleNumber: '07', part: null, partCount: 1 },": "      { path: '07-1-safe-testing-and-first-divergence', title: 'Module 07.1: Safe Testing & First Divergence', category: 'Operating Workflows', moduleNumber: '07', part: 1, partCount: 2 },\n      { path: '07-2-boundary-diagnosis-and-retesting', title: 'Module 07.2: Boundary Diagnosis & Retesting', category: 'Operating Workflows', moduleNumber: '07', part: 2, partCount: 2 },",
}
for old, new in replacements.items():
    if old not in index:
        raise SystemExit(f"Expected reading-unit line not found: {old}")
    index = index.replace(old, new, 1)
index_path.write_text(index, encoding="utf-8")

check_path = ROOT / "scripts/check_content.py"
lines = check_path.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("SUBMODULES = "):
        values = ast.literal_eval(line.split("=", 1)[1].strip())
        for value in [
            "04-1-decisions-guards-and-variables.md", "04-2-loops-and-repeated-logic.md",
            "06-1-forms-input-and-human-delay.md", "06-2-approvals-and-interactive-processes.md",
            "07-1-safe-testing-and-first-divergence.md", "07-2-boundary-diagnosis-and-retesting.md",
        ]:
            if value not in values:
                values.append(value)
        lines[i] = "SUBMODULES = " + repr(values)
    elif line.startswith("READING_UNITS = "):
        values = ast.literal_eval(line.split("=", 1)[1].strip())
        substitutions = {
            "04-operators-and-logic.md": ["04-1-decisions-guards-and-variables.md", "04-2-loops-and-repeated-logic.md"],
            "06-forms-and-interactive-workflows.md": ["06-1-forms-input-and-human-delay.md", "06-2-approvals-and-interactive-processes.md"],
            "07-testing-debugging-and-execution.md": ["07-1-safe-testing-and-first-divergence.md", "07-2-boundary-diagnosis-and-retesting.md"],
        }
        updated = []
        for value in values:
            updated.extend(substitutions.get(value, [value]))
        lines[i] = "READING_UNITS = " + repr(updated)
check_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

external_path = ROOT / "scripts/check_external_links.py"
external = external_path.read_text(encoding="utf-8")
match = re.search(r"FILES = \[ROOT / name for name in (\[[^\n]+\])\]", external)
if not match:
    raise SystemExit("Could not locate external-link file list")
values = ast.literal_eval(match.group(1))
substitutions = {
    "04-operators-and-logic.md": ["04-1-decisions-guards-and-variables.md", "04-2-loops-and-repeated-logic.md"],
    "06-forms-and-interactive-workflows.md": ["06-1-forms-input-and-human-delay.md", "06-2-approvals-and-interactive-processes.md"],
    "07-testing-debugging-and-execution.md": ["07-1-safe-testing-and-first-divergence.md", "07-2-boundary-diagnosis-and-retesting.md"],
}
updated = []
for value in values:
    updated.extend(substitutions.get(value, [value]))
external = external[:match.start(1)] + repr(updated) + external[match.end(1):]
external_path.write_text(external, encoding="utf-8")

print("Split Modules 04, 06, and 07 into six reading units.")
print("Course now has 25 linear reading units.")
