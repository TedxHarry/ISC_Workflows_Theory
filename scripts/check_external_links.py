from pathlib import Path
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
pattern = re.compile(r"https://[^\s)>\"']+")
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
