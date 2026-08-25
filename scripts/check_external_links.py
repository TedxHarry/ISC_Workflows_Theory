from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / name for name in ['README.md', '00-orientation.md', '01-the-workflow-model.md', '02-1-data-and-payload-shape.md', '02-2-variables-and-jsonpath.md', '03-1-choosing-the-right-trigger.md', '03-2-filters-and-specialized-triggers.md', '04-1-decisions-guards-and-variables.md', '04-2-loops-and-repeated-logic.md', '05-1-action-contracts-and-core-actions.md', '05-2-error-handling-external-actions-and-success-boundaries.md', '06-1-forms-input-and-human-delay.md', '06-2-approvals-and-interactive-processes.md', '07-1-safe-testing-and-first-divergence.md', '07-2-boundary-diagnosis-and-retesting.md', '08-1-operating-a-workflow.md', '08-2-limits-change-and-governance.md', '09-1-capability-ownership.md', '09-2-architecture-decisions-and-tradeoffs.md', '10-1-pattern-method-and-core-patterns.md', '10-2-working-engineer-patterns.md', '10-3-advanced-patterns-and-pattern-transfer.md', '11-1-repetition-partial-failure-and-concurrency.md', '11-2-scale-correlation-and-external-state.md', '12-1-paper-design-framework.md', '12-2-capstone-design-lab.md']]
pattern = re.compile(r'https://[^\s)>"\']+')
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
