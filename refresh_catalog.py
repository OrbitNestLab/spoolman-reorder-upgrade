"""Refresh public Bambu EU filament variants, without cookies or shop writes."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent / "spoolman_reorder"
BASE = "https://bambulab-eu.myshopify.com"


def get(path):
    request = Request(BASE + path, headers={"User-Agent": "OrbitNestLab-Spoolman-Catalog/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    products = []
    for page in range(1, 51):
        batch = get(f"/products.json?limit=250&page={page}")["products"]
        if not batch:
            break
        products.extend(p for p in batch if re.match(r"^(PLA|PETG|TPU|ABS|ASA|PA6|PAHT|PPA|PC\b|PVA)", p["title"]))
    else:
        raise RuntimeError("Pagination did not end; preserving the previous catalog")
    catalog = []
    for p in products:
        product = get("/products/" + p["handle"] + ".js")
        catalog.append({key:product[key] for key in ("title","handle")}|{
            "variants":[{key:v.get(key) for key in ("id","title","sku","available","option1","option2","option3")}
                        for v in product["variants"]]})
    variants = [v for p in catalog for v in p["variants"]]
    if len(catalog) < 30 or len(variants) != len({v["id"] for v in variants}):
        raise ValueError("Incomplete or duplicate catalog; preserving the previous snapshot")
    metadata = {"provider":"Bambu Lab EU","source":BASE+"/products.json",
                "retrieved":datetime.now(timezone.utc).isoformat(),
                "products":len(catalog),"variants":len(variants),
                "note":"Public EU catalog snapshot. Shop availability and future products can change."}
    (ROOT/"bambu_eu_catalog.json").write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+"\n")
    (ROOT/"catalog-source.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(f"{len(catalog)} filament products, {len(variants)} unique variants")


if __name__ == "__main__":
    main()
