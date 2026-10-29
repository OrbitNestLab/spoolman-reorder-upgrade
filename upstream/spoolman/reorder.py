"""Pure reorder calculations and safe optional shop links."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class ReorderPolicy:
    threshold_g: float = 150
    unopened_min: int = 1
    order_qty: int = 1

    def __post_init__(self) -> None:
        if self.threshold_g < 0:
            raise ValueError("threshold_g must be non-negative")
        if self.unopened_min < 0 or self.order_qty < 1:
            raise ValueError("unopened_min must be non-negative and order_qty must be positive")


@dataclass(frozen=True)
class ReorderItem:
    profile: str
    filament_id: int
    remaining_g: float
    unopened: int
    order_qty: int
    variant_id: str | None = None
    product_url: str | None = None

    @property
    def needs_reorder(self) -> bool:
        return self.remaining_g <= 0 or self.unopened < 1


def profile_key(*, vendor: str | None, material: str | None, name: str | None,
                color: str | None = None, finish: str | None = None) -> str:
    """Build a stable, human-readable key without collapsing distinct profiles."""
    return "|".join((vendor or "", material or "", name or "", color or "", finish or ""))


def calculate_reorders(rows: list[dict], defaults: ReorderPolicy,
                       overrides: dict[str, ReorderPolicy] | None = None) -> list[ReorderItem]:
    """Aggregate active spools by filament profile and return only missing reserve stock.

    ``unused`` is the authoritative unopened marker supplied by the API caller. A spool with
    zero remaining grams is still harmless when an unopened reserve exists, because the reserve
    count is evaluated independently per profile.
    """
    overrides = overrides or {}
    groups: dict[str, dict] = {}
    for row in rows:
        if row.get("archived", False):
            continue
        key = row["profile"]
        group = groups.setdefault(key, {"filament_id": row["filament_id"], "remaining": 0.0, "unopened": 0})
        group["remaining"] += max(float(row.get("remaining_g", 0)), 0)
        if row.get("unused", False):
            group["unopened"] += 1

    result = []
    for key, group in groups.items():
        policy = overrides.get(key, defaults)
        if group["remaining"] > policy.threshold_g or group["unopened"] >= policy.unopened_min:
            continue
        result.append(ReorderItem(key, group["filament_id"], group["remaining"], group["unopened"], policy.order_qty))
    return sorted(result, key=lambda item: item.profile)


def shopify_cart_url(base_url: str, variant_ids: list[tuple[str, int]]) -> str | None:
    """Build a Shopify cart permalink only from explicitly verified numeric variant IDs."""
    if not base_url or not base_url.startswith(("https://", "http://")) or not variant_ids:
        return None
    if any(not variant.isdigit() or qty < 1 for variant, qty in variant_ids):
        return None
    return f"{base_url.rstrip('/')}/cart/{quote(','.join(f'{variant}:{qty}' for variant, qty in variant_ids), safe=':,')}?storefront=true"

