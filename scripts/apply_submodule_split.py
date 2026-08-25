from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

SPECS = [
    {
        "source": "02-data-variables-and-expressions.md",
        "title": "Module 02: Data, Payloads, Variables & JSONPath",
        "summary": "Learn to inspect Workflow data before referencing it, then turn that structure into reliable JSONPath and variable references.",
        "parts": [
            ("02-1-data-and-payload-shape.md", "Module 02.1: Data & Payload Shape", None, "Read JSON values, objects, arrays, nested structures, and understand when Workflow data becomes available."),
            ("02-2-variables-and-jsonpath.md", "Module 02.2: Variables & JSONPath", "## JSONPath: turn the structure into a route", "Reference real runtime data with JSONPath, selectors, predicates, and a repeatable inspection method."),
        ],
    },
    {
        "source": "03-triggers.md",
        "title": "Module 03: Triggers & Filters",
        "summary": "Choose the event boundary first, then decide how filters and specialized trigger families refine that starting point.",
        "parts": [
            ("03-1-choosing-the-right-trigger.md", "Module 03.1: Choosing the Right Trigger", None, "Choose among the Core trigger boundaries and understand what each event does and does not prove."),
            ("03-2-filters-and-specialized-triggers.md", "Module 03.2: Filters & Specialized Triggers", "## Filters narrow the right trigger", "Narrow qualifying events, diagnose non-starts, and recognize specialized and advanced trigger families."),
        ],
    },
    {
        "source": "05-actions.md",
        "title": "Module 05: Actions & Error Handling",
        "summary": "Read actions as contracts, understand their success boundaries, and handle external dependencies and failures deliberately.",
        "parts": [
            ("05-1-action-contracts-and-core-actions.md", "Module 05.1: Action Contracts & Core Actions", None, "Use the action-contract method across notification, retrieval, access, and account work."),
            ("05-2-error-handling-external-actions-and-success-boundaries.md", "Module 05.2: Error Handling, External Actions & Success Boundaries", "## 8. Integrate: HTTP Request and the dependency you do not control", "Work with external HTTP calls, waits, native Error paths, fallbacks, and truthful execution outcomes."),
        ],
    },
    {
        "source": "08-operations-limits-and-governance.md",
        "title": "Module 08: Operations, Limits & Governance",
        "summary": "Treat a production Workflow as an owned asset with dependencies, constraints, evidence, safe change, and a lifecycle.",
        "parts": [
            ("08-1-operating-a-workflow.md", "Module 08.1: Operating a Workflow", None, "Move from one execution to production ownership, dependencies, and supportability."),
            ("08-2-limits-change-and-governance.md", "Module 08.2: Limits, Change & Governance", "## 5. Core: What constrains it?", "Reason about limits, evidence, promotion, scheduled overlap, handoff, governance, and retirement."),
        ],
    },
    {
        "source": "09-when-to-use-workflows.md",
        "title": "Module 09: When to Use Workflows and When Not",
        "summary": "Choose the capability that naturally owns the outcome before deciding whether Workflow should orchestrate around it.",
        "parts": [
            ("09-1-capability-ownership.md", "Module 09.1: Capability Ownership", None, "Identify the primary capability owner and compare Workflow with neighboring ISC capabilities."),
            ("09-2-architecture-decisions-and-tradeoffs.md", "Module 09.2: Architecture Decisions & Tradeoffs", "## 5. Core: Workflow as an orchestrator, not a replacement engine", "Recognize good Workflow fits, architecture anti-patterns, constraints, and defend the final capability choice."),
        ],
    },
    {
        "source": "10-use-case-patterns.md",
        "title": "Module 10: Real-World Workflow Patterns",
        "summary": "Recognize reusable Workflow shapes, adapt them to real requirements, and distinguish Core, Working Engineer, and Advanced patterns.",
        "parts": [
            ("10-1-pattern-method-and-core-patterns.md", "Module 10.1: Pattern Method & Core Patterns", None, "Learn the seven-part pattern anatomy and apply it to the Core pattern library."),
            ("10-2-working-engineer-patterns.md", "Module 10.2: Working Engineer Patterns", "## Part II: Working Engineer Patterns", "Apply the pattern method to access, account, approval, collection, and certification orchestration."),
            ("10-3-advanced-patterns-and-pattern-transfer.md", "Module 10.3: Advanced Patterns & Pattern Transfer", "## Part III: Advanced Recognition", "Recognize advanced security and integration patterns, combine shapes, and practice transferring patterns to new requirements."),
        ],
    },
    {
        "source": "11-challenges-and-edge-cases.md",
        "title": "Module 11: Challenges, Failure Modes & Edge Cases",
        "summary": "Stress good-looking designs against repetition, overlap, partial failure, external uncertainty, scale, and correlation.",
        "parts": [
            ("11-1-repetition-partial-failure-and-concurrency.md", "Module 11.1: Repetition, Partial Failure & Concurrency", None, "Stress designs against replay, colliding executions, partial completion, and ambiguous external outcomes."),
            ("11-2-scale-correlation-and-external-state.md", "Module 11.2: Scale, Correlation & External State", "## 6. Working Engineer: When the design grows", "Handle growth, cross-execution correlation, unsupported assumptions, signals, and the final production stress test."),
        ],
    },
    {
        "source": "12-readiness-and-paper-design.md",
        "title": "Module 12: Readiness & Paper Design",
        "summary": "Turn the course into a defensible paper architecture before opening the Workflow builder.",
        "parts": [
            ("12-1-paper-design-framework.md", "Module 12.1: Paper Design Framework", None, "Use the ownership gate, seven engineering questions, and paper architecture template."),
            ("12-2-capstone-design-lab.md", "Module 12.2: Capstone Design Lab", "## 5. Core: One complete worked design", "Work through a complete design, then take increasing ownership of independent and ambiguous design challenges."),
        ],
    },
]

UNSPLIT = [
    ("00-orientation.md", "Module 00: Orientation", "00", "Foundations"),
    ("01-the-workflow-model.md", "Module 01: The Workflow Model", "01", "Foundations"),
    ("04-operators-and-logic.md", "Module 04: Operators & Logic", "04", "Building Blocks"),
    ("06-forms-and-interactive-workflows.md", "Module 06: Forms, Approvals & Interactive Workflows", "06", "Building Blocks"),
    ("07-testing-debugging-and-execution.md", "Module 07: Testing, Debugging & Execution", "07", "Operating Workflows"),
]

MODULES = [
    ("00", "00-orientation", "Module 00: Orientation", "Foundations"),
    ("01", "01-the-workflow-model", "Module 01: The Workflow Model", "Foundations"),
    ("02", "02-data-variables-and-expressions", "Module 02: Data, Payloads, Variables & JSONPath", "Foundations"),
    ("03", "03-triggers", "Module 03: Triggers & Filters", "Building Blocks"),
    ("04", "04-operators-and-logic", "Module 04: Operators & Logic", "Building Blocks"),
    ("05", "05-actions", "Module 05: Actions & Error Handling", "Building Blocks"),
    ("06", "06-forms-and-interactive-workflows", "Module 06: Forms, Approvals & Interactive Workflows", "Building Blocks"),
    ("07", "07-testing-debugging-and-execution", "Module 07: Testing, Debugging & Execution", "Operating Workflows"),
    ("08", "08-operations-limits-and-governance", "Module 08: Operations, Limits & Governance", "Operating Workflows"),
    ("09", "09-when-to-use-workflows", "Module 09: When to Use Workflows and When Not", "Engineering Judgment"),
    ("10", "10-use-case-patterns", "Module 10: Real-World Workflow Patterns", "Engineering Judgment"),
    ("11", "11-challenges-and-edge-cases", "Module 11: Challenges, Failure Modes & Edge Cases", "Engineering Judgment"),
    ("12", "12-readiness-and-paper-design", "Module 12: Readiness & Paper Design", "Engineering Judgment"),
]

READING_UNITS = [
    ("00-orientation.md", "Module 00: Orientation", "00", None, 1, "Foundations"),
    ("01-the-workflow-model.md", "Module 01: The Workflow Model", "01", None, 1, "Foundations"),
    ("02-1-data-and-payload-shape.md", "Module 02.1: Data & Payload Shape", "02", 1, 2, "Foundations"),
    ("02-2-variables-and-jsonpath.md", "Module 02.2: Variables & JSONPath", "02", 2, 2, "Foundations"),
    ("03-1-choosing-the-right-trigger.md", "Module 03.1: Choosing the Right Trigger", "03", 1, 2, "Building Blocks"),
    ("03-2-filters-and-specialized-triggers.md", "Module 03.2: Filters & Specialized Triggers", "03", 2, 2, "Building Blocks"),
    ("04-operators-and-logic.md", "Module 04: Operators & Logic", "04", None, 1, "Building Blocks"),
    ("05-1-action-contracts-and-core-actions.md", "Module 05.1: Action Contracts & Core Actions", "05", 1, 2, "Building Blocks"),
    ("05-2-error-handling-external-actions-and-success-boundaries.md", "Module 05.2: Error Handling, External Actions & Success Boundaries", "05", 2, 2, "Building Blocks"),
    ("06-forms-and-interactive-workflows.md", "Module 06: Forms, Approvals & Interactive Workflows", "06", None, 1, "Building Blocks"),
    ("07-testing-debugging-and-execution.md", "Module 07: Testing, Debugging & Execution", "07", None, 1, "Operating Workflows"),
    ("08-1-operating-a-workflow.md", "Module 08.1: Operating a Workflow", "08", 1, 2, "Operating Workflows"),
    ("08-2-limits-change-and-governance.md", "Module 08.2: Limits, Change & Governance", "08", 2, 2, "Operating Workflows"),
    ("09-1-capability-ownership.md", "Module 09.1: Capability Ownership", "09", 1, 2, "Engineering Judgment"),
    ("09-2-architecture-decisions-and-tradeoffs.md", "Module 09.2: Architecture Decisions & Tradeoffs", "09", 2, 2, "Engineering Judgment"),
    ("10-1-pattern-method-and-core-patterns.md", "Module 10.1: Pattern Method & Core Patterns", "10", 1, 3, "Engineering Judgment"),
    ("10-2-working-engineer-patterns.md", "Module 10.2: Working Engineer Patterns", "10", 2, 3, "Engineering Judgment"),
    ("10-3-advanced-patterns-and-pattern-transfer.md", "Module 10.3: Advanced Patterns & Pattern Transfer", "10", 3, 3, "Engineering Judgment"),
    ("11-1-repetition-partial-failure-and-concurrency.md", "Module 11.1: Repetition, Partial Failure & Concurrency", "11", 1, 2, "Engineering Judgment"),
    ("11-2-scale-correlation-and-external-state.md", "Module 11.2: Scale, Correlation & External State", "11", 2, 2, "Engineering Judgment"),
    ("12-1-paper-design-framework.md", "Module 12.1: Paper Design Framework", "12", 1, 2, "Engineering Judgment"),
    ("12-2-capstone-design-lab.md", "Module 12.2: Capstone Design Lab", "12", 2, 2, "Engineering Judgment"),
]


def strip_existing_navigation(text):
    lines = text.rstrip().splitlines()
    for i in range(len(lines) - 1, max(-1, len(lines) - 20), -1):
        line = lines[i]
        if "Course home" in line and ("Previous" in line or "Next" in line):
            lines = lines[:i]
            while lines and not lines[-1].strip():
                lines.pop()
            if lines and lines[-1].strip() == "---":
                lines.pop()
            while lines and not lines[-1].strip():
                lines.pop()
            break
    return "\n".join(lines).rstrip() + "\n"


def nav_line(index):
    items = []
    if index > 0:
        prev_file, prev_title, *_ = READING_UNITS[index - 1]
        items.append(f"[← Previous: {prev_title}]({prev_file})")
    items.append("[Course home](README.md)")
    if index < len(READING_UNITS) - 1:
        next_file, next_title, *_ = READING_UNITS[index + 1]
        items.append(f"[Next: {next_title} →]({next_file})")
    return " | ".join(items)


def with_navigation(text, unit_file):
    index = next(i for i, unit in enumerate(READING_UNITS) if unit[0] == unit_file)
    return strip_existing_navigation(text).rstrip() + "\n\n---\n\n" + nav_line(index) + "\n"


def landing_page(spec):
    lines = [
        f"# {spec['title']}",
        "",
        spec["summary"],
        "",
        "This module is divided into shorter reading units so you can stop at a natural checkpoint without losing the full technical depth.",
        "",
        "## Reading path",
        "",
    ]
    for i, (filename, title, _marker, description) in enumerate(spec["parts"], 1):
        lines.append(f"{i}. [{title}]({filename})")
        lines.append(f"   {description}")
    lines += [
        "",
        f"**Start here:** [{spec['parts'][0][1]}]({spec['parts'][0][0]})",
        "",
        "The numbered parts are one module. Read them in order on a first pass; return directly to a part later when you need it as a reference.",
        "",
    ]
    return "\n".join(lines)


def split_module(spec):
    path = ROOT / spec["source"]
    original = path.read_text(encoding="utf-8")
    first_newline = original.find("\n")
    if first_newline < 0 or not original.startswith("# Module "):
        raise SystemExit(f"Unexpected module H1 in {spec['source']}")
    body = strip_existing_navigation(original[first_newline + 1 :])

    markers = [part[2] for part in spec["parts"] if part[2] is not None]
    positions = []
    for marker in markers:
        pos = body.find(marker)
        if pos < 0:
            raise SystemExit(f"Missing split marker in {spec['source']}: {marker}")
        positions.append(pos)
    if positions != sorted(positions):
        raise SystemExit(f"Split markers out of order in {spec['source']}")

    starts = [0] + positions
    ends = positions + [len(body)]
    chunks = [body[start:end] for start, end in zip(starts, ends)]
    if "".join(chunks) != body:
        raise SystemExit(f"Content integrity failure while splitting {spec['source']}")
    if len(chunks) != len(spec["parts"]):
        raise SystemExit(f"Part count mismatch for {spec['source']}")

    for chunk, (filename, title, _marker, _description) in zip(chunks, spec["parts"]):
        part_text = f"# {title}\n" + chunk.lstrip("\n")
        (ROOT / filename).write_text(with_navigation(part_text, filename), encoding="utf-8")

    path.write_text(landing_page(spec), encoding="utf-8")


for spec in SPECS:
    split_module(spec)

for filename, _title, _number, _category in UNSPLIT:
    path = ROOT / filename
    path.write_text(with_navigation(path.read_text(encoding="utf-8"), filename), encoding="utf-8")

sidebar = """- [Home](README.md)

## Foundations

- [00: Orientation](00-orientation.md)
- [01: The Workflow Model](01-the-workflow-model.md)
- [02: Data, Payloads, Variables & JSONPath](02-data-variables-and-expressions.md)
  - [02.1: Data & Payload Shape](02-1-data-and-payload-shape.md)
  - [02.2: Variables & JSONPath](02-2-variables-and-jsonpath.md)

## Building Blocks

- [03: Triggers & Filters](03-triggers.md)
  - [03.1: Choosing the Right Trigger](03-1-choosing-the-right-trigger.md)
  - [03.2: Filters & Specialized Triggers](03-2-filters-and-specialized-triggers.md)
- [04: Operators & Logic](04-operators-and-logic.md)
- [05: Actions & Error Handling](05-actions.md)
  - [05.1: Action Contracts & Core Actions](05-1-action-contracts-and-core-actions.md)
  - [05.2: Error Handling, External Actions & Success Boundaries](05-2-error-handling-external-actions-and-success-boundaries.md)
- [06: Forms, Approvals & Interactive Workflows](06-forms-and-interactive-workflows.md)

## Operating Workflows

- [07: Testing, Debugging & Execution](07-testing-debugging-and-execution.md)
- [08: Operations, Limits & Governance](08-operations-limits-and-governance.md)
  - [08.1: Operating a Workflow](08-1-operating-a-workflow.md)
  - [08.2: Limits, Change & Governance](08-2-limits-change-and-governance.md)

## Engineering Judgment

- [09: When to Use Workflows and When Not](09-when-to-use-workflows.md)
  - [09.1: Capability Ownership](09-1-capability-ownership.md)
  - [09.2: Architecture Decisions & Tradeoffs](09-2-architecture-decisions-and-tradeoffs.md)
- [10: Real-World Workflow Patterns](10-use-case-patterns.md)
  - [10.1: Pattern Method & Core Patterns](10-1-pattern-method-and-core-patterns.md)
  - [10.2: Working Engineer Patterns](10-2-working-engineer-patterns.md)
  - [10.3: Advanced Patterns & Pattern Transfer](10-3-advanced-patterns-and-pattern-transfer.md)
- [11: Challenges, Failure Modes & Edge Cases](11-challenges-and-edge-cases.md)
  - [11.1: Repetition, Partial Failure & Concurrency](11-1-repetition-partial-failure-and-concurrency.md)
  - [11.2: Scale, Correlation & External State](11-2-scale-correlation-and-external-state.md)
- [12: Readiness & Paper Design](12-readiness-and-paper-design.md)
  - [12.1: Paper Design Framework](12-1-paper-design-framework.md)
  - [12.2: Capstone Design Lab](12-2-capstone-design-lab.md)
"""
(ROOT / "_sidebar.md").write_text(sidebar, encoding="utf-8")

readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    '<div class="course-stats">13 modules · Foundations to engineering to design</div>',
    '<div class="course-stats">13 modules · 22 reading units · Foundations to engineering to design</div>',
)
readme = readme.replace(
    '<div class="callout-key">\n  <span class="callout-label">How to use this guide</span>\n  Read the modules in order if you are new to ISC Workflows. If you already build workflows, use the sidebar to jump directly to the topic you need.\n</div>',
    '<div class="callout-key">\n  <span class="callout-label">How to use this guide</span>\n  Read the modules in order if you are new to ISC Workflows. Longer modules are divided into numbered reading units, giving you natural stopping points while preserving the 00-12 course structure. If you already build workflows, use the sidebar to jump directly to the topic you need.\n</div>',
)
readme_path.write_text(readme, encoding="utf-8")

module_js = "    const modules = [\n" + ",\n".join(
    f"      {{ number: '{number}', path: '{path}', title: '{title.replace(chr(39), chr(92)+chr(39))}', category: '{category}' }}"
    for number, path, title, category in MODULES
) + "\n    ];\n\n"

unit_js_rows = []
for filename, title, module_number, part, part_count, category in READING_UNITS:
    path = filename[:-3]
    js_part = "null" if part is None else str(part)
    safe_title = title.replace("'", "\\'")
    unit_js_rows.append(
        f"      {{ path: '{path}', title: '{safe_title}', category: '{category}', moduleNumber: '{module_number}', part: {js_part}, partCount: {part_count} }}"
    )
reading_js = "    const readingUnits = [\n" + ",\n".join(unit_js_rows) + "\n    ];\n\n"

index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")
index, count = re.subn(r"    const modules = \[.*?\n    \];\n\n", module_js + reading_js, index, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not replace modules array in index.html")

new_info_functions = r'''    function currentReadingInfo() {
      const path = currentPath();
      const index = readingUnits.findIndex(function (item) {
        return item.path === path;
      });
      return index >= 0 ? { unit: readingUnits[index], index: index } : null;
    }

    function currentModuleInfo() {
      const path = currentPath();
      let index = modules.findIndex(function (item) {
        return item.path === path;
      });
      if (index >= 0) {
        return { module: modules[index], index: index };
      }

      const unitInfo = currentReadingInfo();
      if (!unitInfo) {
        return null;
      }
      index = modules.findIndex(function (item) {
        return item.number === unitInfo.unit.moduleNumber;
      });
      return index >= 0 ? { module: modules[index], index: index } : null;
    }

'''
index, count = re.subn(
    r"    function currentModuleInfo\(\) \{.*?\n    \}\n\n",
    new_info_functions,
    index,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("Could not replace currentModuleInfo in index.html")

index = index.replace("function normalizeHomeModuleLinks()", "function normalizeCourseLinks()")
index = index.replace(
    "      if (currentPath()) {\n        return;\n      }\n\n      const content = document.querySelector('.markdown-section');",
    "      const content = document.querySelector('.markdown-section');",
    1,
)
index = index.replace(
    "      const modulePaths = new Set(modules.map(function (item) { return item.path; }));",
    "      const modulePaths = new Set(modules.map(function (item) { return item.path; }).concat(readingUnits.map(function (item) { return item.path; })));",
    1,
)
index = index.replace("normalizeHomeModuleLinks();", "normalizeCourseLinks();")

start = index.find("          hook.afterEach(function (html) {")
end = index.find("          hook.doneEach(function () {", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate afterEach block in index.html")
new_after_each = '''          hook.afterEach(function (html) {
            const unitInfo = currentReadingInfo();
            const moduleInfo = currentModuleInfo();

            if (unitInfo) {
              const unit = unitInfo.unit;
              let progress = '· Module ' + unit.moduleNumber;
              if (unit.partCount > 1) {
                progress += ' · Part ' + unit.part + ' of ' + unit.partCount;
              }
              progress += ' · Reading unit ' + (unitInfo.index + 1) + ' of ' + readingUnits.length;
              html = '<div class="module-category">' + unit.category + ' <span class="module-progress">' + progress + '</span></div>' + html;

              const previous = unitInfo.index > 0
                ? readingUnits[unitInfo.index - 1]
                : { path: '', title: 'Course Home' };
              const next = unitInfo.index < readingUnits.length - 1
                ? readingUnits[unitInfo.index + 1]
                : null;

              let navigation = '<nav class="course-navigation" aria-label="Course navigation">';
              navigation += '<a class="previous" href="#/' + previous.path + '">' +
                '<span class="nav-label">Previous</span>' +
                '<span class="nav-title">' + previous.title + '</span>' +
                '</a>';

              if (next) {
                navigation += '<a class="next" href="#/' + next.path + '">' +
                  '<span class="nav-label">Next</span>' +
                  '<span class="nav-title">' + next.title + '</span>' +
                  '</a>';
              } else {
                navigation += '<a class="next" href="#/">' +
                  '<span class="nav-label">Course complete</span>' +
                  '<span class="nav-title">Return to Course Home</span>' +
                  '</a>';
              }

              navigation += '</nav>';
              html += navigation;
            } else if (moduleInfo) {
              const module = moduleInfo.module;
              html = '<div class="module-category">' + module.category + ' <span class="module-progress">· Module ' + module.number + ' overview</span></div>' + html;
            }

            return html + '<footer class="course-footer">© TedxHarry · SailPoint ISC Workflows</footer>';
          });

'''
index = index[:start] + new_after_each + index[end:]

old_title = "            const info = currentModuleInfo();\n            document.title = info ? info.module.title + ' | SailPoint ISC Workflows' : 'SailPoint ISC Workflows';"
new_title = "            const unitInfo = currentReadingInfo();\n            const moduleInfo = currentModuleInfo();\n            document.title = unitInfo ? unitInfo.unit.title + ' | SailPoint ISC Workflows' : (moduleInfo ? moduleInfo.module.title + ' | SailPoint ISC Workflows' : 'SailPoint ISC Workflows');"
if old_title not in index:
    raise SystemExit("Could not locate document.title logic in index.html")
index = index.replace(old_title, new_title, 1)

index_path.write_text(index, encoding="utf-8")

canonical_modules = [f"{path}.md" for _number, path, _title, _category in MODULES]
submodules = [unit[0] for unit in READING_UNITS if unit[0] not in canonical_modules]
reading_unit_files = [unit[0] for unit in READING_UNITS]

check_content = f'''from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MODULES = {canonical_modules!r}
SUBMODULES = {submodules!r}
READING_UNITS = {reading_unit_files!r}
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
    if text is not None and "\\u2014" in text:
        errors.append(f"Em dash found: {{path.relative_to(ROOT)}}")

for name in READER_PAGES:
    path = ROOT / name
    if not path.exists():
        errors.append(f"Missing course page: {{name}}")
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
        match = re.match(r"^(#{{1,6}})\\s+\\S", line)
        if match:
            headings.append((line_number, len(match.group(1)), line))
    h1s = [heading for heading in headings if heading[1] == 1]
    if len(h1s) != 1:
        errors.append(f"{{name}}: expected exactly one H1, found {{len(h1s)}}")
    elif not h1s[0][2].startswith("# Module "):
        errors.append(f'{{name}}: H1 must start with "# Module "')
    previous = None
    for line_number, level, line in headings:
        if previous is not None and level > previous + 1:
            errors.append(f"{{name}}:{{line_number}}: heading level jumps from H{{previous}} to H{{level}}: {{line}}")
        previous = level

link_pattern = re.compile(r"\\[[^\\]]*\\]\\(([^)]+)\\)")
for name in CHECK_LINKS:
    path = ROOT / name
    if not path.exists():
        continue
    content = path.read_text(encoding="utf-8")
    if "chatgpt.com/" in content:
        errors.append(f"{{name}}: contains an absolute chatgpt.com link")
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
            errors.append(f"{{name}}: link escapes repository: {{target}}")
            continue
        if not resolved.exists():
            errors.append(f"{{name}}: broken internal link: {{target}}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
sidebar = (ROOT / "_sidebar.md").read_text(encoding="utf-8")
for module in CANONICAL_MODULES:
    if module not in readme:
        errors.append(f"README.md: missing canonical module link {{module}}")
    if module not in sidebar:
        errors.append(f"_sidebar.md: missing canonical module link {{module}}")
for unit in READING_UNITS:
    if unit not in sidebar:
        errors.append(f"_sidebar.md: missing reading-unit link {{unit}}")

if errors:
    print("Content quality checks failed:")
    for error in errors:
        print(f" - {{error}}")
    sys.exit(1)

print(f"Content quality checks passed for {{len(CANONICAL_MODULES)}} conceptual modules and {{len(READING_UNITS)}} reading units.")
'''
(ROOT / "scripts/check_content.py").write_text(check_content, encoding="utf-8")

external_checker = f'''from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / name for name in {(['README.md'] + reading_unit_files)!r}]
pattern = re.compile(r'https://[^\\s)>"\\']+')
urls = set()
for path in FILES:
    if path.exists():
        urls.update(url.rstrip(".,;") for url in pattern.findall(path.read_text(encoding="utf-8")))

hard_failures = []
warnings = []
for url in sorted(urls):
    request = Request(url, headers={{"User-Agent": "ISC-Workflows-Theory-link-check/1.0"}})
    try:
        with urlopen(request, timeout=20) as response:
            print(f"{{response.getcode()}} {{url}}")
    except HTTPError as exc:
        if exc.code in (404, 410):
            hard_failures.append(f"{{exc.code}} {{url}}")
        else:
            warnings.append(f"{{exc.code}} {{url}}")
    except (URLError, TimeoutError) as exc:
        warnings.append(f"{{url}}: {{exc}}")

if warnings:
    print("Reachability warnings:")
    for warning in warnings:
        print(f" - {{warning}}")

if hard_failures:
    print("Broken external links:")
    for failure in hard_failures:
        print(f" - {{failure}}")
    sys.exit(1)

print(f"Checked {{len(urls)}} unique external links.")
'''
(ROOT / "scripts/check_external_links.py").write_text(external_checker, encoding="utf-8")

authoring_path = ROOT / "AUTHORING-GUIDE.md"
authoring = authoring_path.read_text(encoding="utf-8")
section = '''\n\n## Reading-unit structure\n\nThe course keeps **13 conceptual modules, numbered 00 through 12**. Longer modules may be divided into numbered reading units such as `10.1`, `10.2`, and `10.3` when there is a genuine learner stopping point.\n\n- Keep the conceptual module landing page and repository path stable.\n- Split at an existing conceptual boundary rather than an arbitrary word count.\n- Preserve the full teaching and technical substance unless a separate content revision is approved.\n- Keep first-pass navigation linear across reading units.\n- Use the module landing page for cross-module references such as “Module 10.”\n- Do not split a short module merely to make the file structure symmetrical.\n'''
if "## Reading-unit structure" not in authoring:
    authoring_path.write_text(authoring.rstrip() + section + "\n", encoding="utf-8")

print("Created 17 submodule pages across 8 long modules.")
print("Preserved 13 conceptual module landing paths.")
print("Configured 22 linear reading units.")
