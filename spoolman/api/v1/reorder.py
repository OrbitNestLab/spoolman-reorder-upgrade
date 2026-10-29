"""Read-only reorder planning endpoints."""

import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from spoolman.database.database import get_db_session
from spoolman.database.models import Filament, Spool
from spoolman.reorder import ReorderPolicy, calculate_reorders, profile_key, shopify_cart_url
from spoolman.database import setting
from spoolman.settings import parse_setting
from spoolman.exceptions import ItemNotFoundError

router = APIRouter(prefix="/reorder", tags=["reorder"])
CATALOG_PATH = Path(__file__).resolve().parents[2] / "bambu_eu_catalog.json"


class ReorderResponse(BaseModel):
    profile: str
    filament_id: int
    remaining_g: float
    unopened: int
    order_qty: int = Field(ge=1)
    variant_id: str | None = None
    cart_url: str | None = None


@router.get("/bambu-catalog", summary="Get the stored Bambu EU filament catalog")
async def bambu_catalog() -> list[dict]:
    """Return the versioned, read-only catalog of verified Bambu EU variants.

    The catalog is shipped with the upgrade so future reorder mappings can be
    resolved without changing a shop session or placing an order.
    """
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _policy(raw: str) -> ReorderPolicy:
    value = json.loads(raw)
    return ReorderPolicy(
        threshold_g=float(value.get("threshold_g", 150)),
        unopened_min=int(value.get("unopened_min", 1)),
        order_qty=int(value.get("order_qty", 1)),
    )


async def _setting_value(db: AsyncSession, key: str) -> str:
    definition = parse_setting(key)
    try:
        return (await setting.get(db, definition)).value
    except ItemNotFoundError:
        return definition.default


@router.get("", response_model=list[ReorderResponse], summary="Get the current reorder plan")
async def find(db: Annotated[AsyncSession, Depends(get_db_session)]) -> list[ReorderResponse]:
    """Calculate a plan without changing spools, tags, usage or provider sessions."""
    defaults = _policy(await _setting_value(db, "reorder_defaults"))
    profile_settings = json.loads(await _setting_value(db, "reorder_profiles"))
    provider = json.loads(await _setting_value(db, "reorder_providers"))
    policies = {key: _policy(json.dumps(value)) for key, value in profile_settings.items()}
    rows = []
    result = await db.execute(select(Spool).options(selectinload(Spool.filament).selectinload(Filament.vendor)))
    for spool in result.scalars().all():
        filament = spool.filament
        vendor = filament.vendor.name if filament.vendor else None
        rows.append({
            "profile": profile_key(vendor=vendor, material=filament.material, name=filament.name),
            "filament_id": filament.id,
            "remaining_g": max((spool.initial_weight or filament.weight or 0) - spool.used_weight, 0),
            "unused": spool.first_used is None,
            "archived": bool(spool.archived),
        })
    plan = calculate_reorders(rows, defaults, policies)
    variants = provider.get("variants", {}) if isinstance(provider, dict) else {}
    base_url = provider.get("base_url", "") if isinstance(provider, dict) else ""
    response = []
    for item in plan:
        variant = variants.get(item.profile)
        variant_id = str(variant) if isinstance(variant, str) and variant.isdigit() else None
        cart_url = shopify_cart_url(base_url, [(variant_id, item.order_qty)]) if variant_id else None
        response.append(ReorderResponse(**item.__dict__, variant_id=variant_id, cart_url=cart_url))
    return response
