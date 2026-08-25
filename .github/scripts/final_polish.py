from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

if "function normalizeHomeModuleLinks()" not in text:
    marker = "    function linkModuleReferences() {\n"
    function = """    function normalizeHomeModuleLinks() {
      if (currentPath()) {
        return;
      }

      const content = document.querySelector('.markdown-section');
      if (!content) {
        return;
      }

      const modulePaths = new Set(modules.map(function (item) { return item.path; }));
      content.querySelectorAll('a[href$=\".md\"]').forEach(function (link) {
        const href = link.getAttribute('href');
        if (!href) {
          return;
        }
        const path = href.replace(/^\\.\\//, '').replace(/\\.md$/, '');
        if (modulePaths.has(path)) {
          link.setAttribute('href', '#/' + path);
        }
      });
    }

"""
    if marker not in text:
        raise SystemExit("Could not find linkModuleReferences marker")
    text = text.replace(marker, function + marker, 1)
    call_marker = "            removeLegacyFooterNavigation();\n"
    if call_marker not in text:
        raise SystemExit("Could not find doneEach navigation marker")
    text = text.replace(
        call_marker,
        call_marker + "            normalizeHomeModuleLinks();\n",
        1,
    )
    path.write_text(text, encoding="utf-8")
