"""Generate the reviewable patch against the exact currently installed upstream."""
import difflib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT.parent / "spoolman-upstream"
BASE = "bed3f14ee77a3a571d31b14215d54b0b88a7519c"
FILES = [
    "spoolman/reorder.py", "spoolman/settings.py", "spoolman/api/v1/reorder.py",
    "spoolman/api/v1/router.py", "tests/test_reorder.py",
    "client_v2/src/lib/api/reorder.ts", "client_v2/src/lib/components/NavTabs.svelte",
    "client_v2/src/routes/reorder/+page.svelte", "client_v2/src/lib/stores/settings.svelte.ts",
    "client_v2/src/routes/settings/+page.svelte", "client_v2/locales/en/common.json",
    "client_v2/locales/de/common.json",
]
patches = []
for name in FILES:
    old = subprocess.run(["git", "show", f"{BASE}:{name}"], cwd=UPSTREAM, capture_output=True, text=True)
    before = old.stdout if old.returncode == 0 else ""
    after = (ROOT / "source" / name).read_text()
    if "/locales/" in name:
        original, current = json.loads(before), json.loads(after)
        original.update({k:v for k,v in current.items() if k.startswith("reorder.")})
        after = json.dumps(original, indent=4, ensure_ascii=False) + "\n"
    for line in difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                   fromfile=f"a/{name}" if before else "/dev/null", tofile=f"b/{name}"):
        patches.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
(ROOT / "spoolman_reorder/upstream.patch").write_text("".join(patches))

catalog_path = ROOT/"spoolman_reorder/bambu_eu_catalog.json"
if catalog_path.exists():
    catalog = json.loads(catalog_path.read_text())
else:
    catalog = json.loads(subprocess.check_output(["git","show","50ee57c:spoolman/bambu_eu_catalog.json"],cwd=UPSTREAM))
catalog = [p for p in catalog if not p["title"].startswith("PC4-")]
variants = [v for p in catalog for v in p["variants"]]
assert len({v["id"] for v in variants}) == len(variants)
(ROOT/"spoolman_reorder/bambu_eu_catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+"\n")
(ROOT/"spoolman_reorder/catalog-source.json").write_text(json.dumps({
    "provider":"Bambu Lab EU","source":"https://bambulab-eu.myshopify.com/products.json",
    "retrieved":"2026-10-29","products":len(catalog),"variants":len(variants),
    "note":"Snapshot of publicly listed EU filament variants. Availability and future products can change."
},indent=2)+"\n")
print(f"Generated patch for {len(FILES)} files; catalog: {len(catalog)} products, {len(variants)} variants")
