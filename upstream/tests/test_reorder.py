from spoolman.reorder import ReorderPolicy, calculate_reorders, profile_key, shopify_cart_url


def test_threshold_boundaries_and_zero_are_inclusive():
    rows = [{"profile": "p", "filament_id": 1, "remaining_g": grams, "unused": False} for grams in (0, 149, 150, 151)]
    assert calculate_reorders(rows, ReorderPolicy(threshold_g=150, unopened_min=1)) == []
    assert calculate_reorders(rows[:2], ReorderPolicy(threshold_g=150, unopened_min=1))[0].remaining_g == 149


def test_unopened_reserve_suppresses_empty_spool_reorder():
    rows = [
        {"profile": "p", "filament_id": 1, "remaining_g": 0, "unused": False},
        {"profile": "p", "filament_id": 1, "remaining_g": 1000, "unused": True},
    ]
    assert calculate_reorders(rows, ReorderPolicy()) == []


def test_archived_and_duplicate_profiles_are_ignored_safely():
    rows = [
        {"profile": profile_key(vendor="A", material="PLA", name="Red"), "filament_id": 1, "remaining_g": 0, "unused": False},
        {"profile": profile_key(vendor="A", material="PLA", name="Red"), "filament_id": 1, "remaining_g": 0, "unused": False, "archived": True},
    ]
    assert len(calculate_reorders(rows, ReorderPolicy())) == 1


def test_shopify_link_never_guesses_invalid_variants():
    assert shopify_cart_url("https://eu.store.example", [("123", 2)]) == "https://eu.store.example/cart/123:2?storefront=true"
    assert shopify_cart_url("https://eu.store.example", [("unknown", 1)]) is None

