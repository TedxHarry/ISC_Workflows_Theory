from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[2]


def write(path, content):
    path.write_text(content, encoding="utf-8")


# Heading hierarchy: canonical modules have one H1.
for filename in ["03-triggers.md", "10-use-case-patterns.md"]:
    path = ROOT / filename
    lines = path.read_text(encoding="utf-8").splitlines()
    seen_h1 = False
    output = []
    for line in lines:
        if line.startswith("# "):
            if seen_h1:
                line = "#" + line
            else:
                seen_h1 = True
        output.append(line)
    write(path, "\n".join(output) + "\n")


# README links should work on GitHub and Docsify.
readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
module_paths = [
    "00-orientation",
    "01-the-workflow-model",
    "02-data-variables-and-expressions",
    "03-triggers",
    "04-operators-and-logic",
    "05-actions",
    "06-forms-and-interactive-workflows",
    "07-testing-debugging-and-execution",
    "08-operations-limits-and-governance",
    "09-when-to-use-workflows",
    "10-use-case-patterns",
    "11-challenges-and-edge-cases",
    "12-readiness-and-paper-design",
]
for module_path in module_paths:
    readme = readme.replace(f'href="#/{module_path}"', f'href="{module_path}.md"')
website = '  <div class="repo-website"><a href="https://tedxharry.github.io/ISC_Workflows_Theory/">View the Course Website</a></div>\n'
if 'class="repo-website"' not in readme:
    marker = '  <div class="independent-note">Independent learning guide. Not official SailPoint documentation.</div>\n'
    readme = readme.replace(marker, marker + website)
write(readme_path, readme)


# Make Official References part of the Markdown source of truth.
reference_blocks = {
    "00-orientation.md": """## Official References

- [Workflows - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/index.html)
- [Building Workflows - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)

---
""",
    "01-the-workflow-model.md": """## Official References

- [Building Workflows - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-build.html)
- [Workflow Actions - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-actions.html)
- [Workflow Operators - SailPoint Identity Services](https://documentation.sailpoint.com/saas/help/workflows/workflow-operators.html)

---
""",
}
for filename, block in reference_blocks.items():
    path = ROOT / filename
    content = path.read_text(encoding="utf-8")
    if "## Official References" not in content:
        if "\n---\n\n[" not in content:
            raise RuntimeError(f"Could not find final navigation boundary in {filename}")
        content = content.replace("\n---\n\n[", "\n" + block + "\n[", 1)
        write(path, content)


# Remove duplicate technical callout/reference data from the site shell.
index_path = ROOT / "index.html"
html = index_path.read_text(encoding="utf-8")
html = re.sub(
    r"\n    const moduleHighlights = \{.*?\n    \};\n\n    const officialReferences = \{.*?\n    \};\n",
    "\n",
    html,
    flags=re.S,
)
html = re.sub(
    r"\n    function insertModuleCallouts\(\) \{.*?\n    \}\n\n    function addCopyButtons",
    "\n    function addCopyButtons",
    html,
    flags=re.S,
)
html = re.sub(
    r"\n    function referencesHtml\(path\) \{.*?\n    \}\n\n    window\.\$docsify",
    "\n    window.$docsify",
    html,
    flags=re.S,
)
html = html.replace("              html += referencesHtml(module.path);\n", "")
html = html.replace("            insertModuleCallouts();\n", "")


# Accessibility and keyboard usability.
if ".skip-link {" not in html:
    css_anchor = "    body {\n      color: var(--course-text);\n    }\n"
    accessibility_css = """

    .skip-link {
      position: fixed;
      top: 0.5rem;
      left: 0.5rem;
      z-index: 1000;
      padding: 0.65rem 0.85rem;
      border-radius: 6px;
      background: #fff;
      color: var(--course-navy);
      font-weight: 700;
      transform: translateY(-160%);
      transition: transform 0.15s ease;
    }

    .skip-link:focus {
      transform: translateY(0);
    }

    a:focus-visible,
    button:focus-visible {
      outline: 3px solid #1f704f;
      outline-offset: 3px;
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
      }
    }
"""
    html = html.replace(css_anchor, css_anchor + accessibility_css)

if 'href="#main-content"' not in html:
    html = html.replace(
        '<body>\n  <div id="app">',
        '<body>\n  <a class="skip-link" href="#main-content">Skip to course content</a>\n  <div id="app">',
    )

html = html.replace(
    "        button.setAttribute('aria-label', 'Copy code');\n",
    "        button.setAttribute('aria-label', 'Copy code');\n        button.setAttribute('aria-live', 'polite');\n",
)
old_clipboard = """          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
              button.textContent = 'Copied';
              setTimeout(function () { button.textContent = 'Copy'; }, 1400);
            });
          }
"""
new_clipboard = """          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
              button.textContent = 'Copied';
              setTimeout(function () { button.textContent = 'Copy'; }, 1400);
            }).catch(function () {
              button.textContent = 'Copy failed';
              setTimeout(function () { button.textContent = 'Copy'; }, 1400);
            });
          } else {
            button.textContent = 'Copy unavailable';
            setTimeout(function () { button.textContent = 'Copy'; }, 1400);
          }
"""
html = html.replace(old_clipboard, new_clipboard)

done_marker = "          hook.doneEach(function () {\n"
accessibility_js = """          hook.doneEach(function () {
            const mainContent = document.querySelector('.markdown-section');
            if (mainContent) {
              mainContent.id = 'main-content';
              mainContent.setAttribute('tabindex', '-1');
            }

            const activeSidebarLink = document.querySelector('.sidebar-nav li.active > a');
            if (activeSidebarLink) {
              activeSidebarLink.setAttribute('aria-current', 'page');
            }
"""
if "mainContent.id = 'main-content'" not in html:
    html = html.replace(done_marker, accessibility_js, 1)
write(index_path, html)


# Reusable quality tooling.
scripts_dir = ROOT / "scripts"
scripts_dir.mkdir(exist_ok=True)
check_content = r'''from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "00-orientation.md",
    "01-the-workflow-model.md",
    "02-data-variables-and-expressions.md",
    "03-triggers.md",
    "04-operators-and-logic.md",
    "05-actions.md",
    "06-forms-and-interactive-workflows.md",
    "07-testing-debugging-and-execution.md",
    "08-operations-limits-and-governance.md",
    "09-when-to-use-workflows.md",
    "10-use-case-patterns.md",
    "11-challenges-and-edge-cases.md",
    "12-readiness-and-paper-design.md",
]
CHECK_LINKS = MODULES + ["README.md", "_sidebar.md", "AUTHORING-GUIDE.md", "COURSE-STATUS.md"]
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

for name in MODULES:
    path = ROOT / name
    if not path.exists():
        errors.append(f"Missing canonical module: {name}")
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
for module in MODULES:
    if module not in readme:
        errors.append(f"README.md: missing canonical module link {module}")
    if module not in sidebar:
        errors.append(f"_sidebar.md: missing canonical module link {module}")

if errors:
    print("Content quality checks failed:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print(f"Content quality checks passed for {len(MODULES)} canonical modules.")
'''
write(scripts_dir / "check_content.py", textwrap.dedent(check_content))

check_external = r'''from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "00-orientation.md",
    ROOT / "01-the-workflow-model.md",
    ROOT / "02-data-variables-and-expressions.md",
    ROOT / "03-triggers.md",
    ROOT / "04-operators-and-logic.md",
    ROOT / "05-actions.md",
    ROOT / "06-forms-and-interactive-workflows.md",
    ROOT / "07-testing-debugging-and-execution.md",
    ROOT / "08-operations-limits-and-governance.md",
    ROOT / "09-when-to-use-workflows.md",
    ROOT / "10-use-case-patterns.md",
    ROOT / "11-challenges-and-edge-cases.md",
    ROOT / "12-readiness-and-paper-design.md",
    ROOT / "README.md",
]
pattern = re.compile(r"https://[^\s)>]+")
urls = set()
for path in FILES:
    if path.exists():
        urls.update(url.rstrip(".,;") for url in pattern.findall(path.read_text(encoding="utf-8")))

hard_failures = []
warnings = []
for url in sorted(urls):
    request = Request(url, headers={"User-Agent": "ISC-Workflows-Theory-link-check/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            print(f"{response.getcode()} {url}")
    except HTTPError as exc:
        if exc.code in (404, 410):
            hard_failures.append(f"{exc.code} {url}")
        else:
            warnings.append(f"{exc.code} {url}")
    except (URLError, TimeoutError) as exc:
        warnings.append(f"{url}: {exc}")

if warnings:
    print("Reachability warnings:")
    for warning in warnings:
        print(f" - {warning}")

if hard_failures:
    print("Broken external links:")
    for failure in hard_failures:
        print(f" - {failure}")
    sys.exit(1)

print(f"Checked {len(urls)} unique external links.")
'''
write(scripts_dir / "check_external_links.py", textwrap.dedent(check_external))


workflows_dir = ROOT / ".github" / "workflows"
workflows_dir.mkdir(parents=True, exist_ok=True)
content_quality = """name: Content quality

on:
  pull_request:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
      - name: Validate course content
        run: python scripts/check_content.py
"""
write(workflows_dir / "content-quality.yml", content_quality)

external_links = """name: External link check

on:
  schedule:
    - cron: '17 13 1 * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
      - name: Check external links
        run: python scripts/check_external_links.py
"""
write(workflows_dir / "external-link-check.yml", external_links)


# Remove bootstrap artifacts before the final commit.
for temporary in [
    ROOT / ".github" / "workflows" / "apply-hardening.yml",
    ROOT / ".github" / "scripts" / "apply_hardening.py",
]:
    if temporary.exists():
        temporary.unlink()
try:
    (ROOT / ".github" / "scripts").rmdir()
except OSError:
    pass
