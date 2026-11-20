from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core import (
    add_label,
    add_route_point,
    current_location,
    remove_label,
    route_cities,
    set_status,
    update_meta,
)
from model import Parcel, RoutePoint, Status, make_meta


@pytest.fixture
def parcel() -> Parcel:
    return Parcel(
        id=1,
        status=Status.CREATED,
        route=(RoutePoint("Lviv", "Hub 1", "2026-11-20T09:00:00"),),
        labels=frozenset({"fragile", "priority"}),
        meta=make_meta(carrier="NovaPost", source="shop"),
    )


def snapshot(p: Parcel) -> tuple[object, ...]:
    # deepcopy не працює з mappingproxy, тому робимо "знімок" вручну
    return (p.id, p.status, p.route, p.labels, dict(p.meta))


# ---------- немутація ----------
def test_add_route_point_no_mutation(parcel: Parcel) -> None:
    before = snapshot(parcel)
    new = add_route_point(parcel, RoutePoint("Kyiv", "Hub 2", "2026-11-20T15:00"))
    assert snapshot(parcel) == before
    assert new is not parcel
    assert len(new.route) == len(parcel.route) + 1
    assert route_cities(new) == ("Lviv", "Kyiv")


def test_add_and_remove_label(parcel: Parcel) -> None:
    before = snapshot(parcel)
    with_label = add_label(parcel, "vip")
    assert "vip" in with_label.labels
    assert "vip" not in parcel.labels
    assert remove_label(with_label, "vip") == parcel
    assert snapshot(parcel) == before


def test_set_status_valid_and_invalid(parcel: Parcel) -> None:
    moved = set_status(parcel, Status.IN_TRANSIT)
    assert moved.status is Status.IN_TRANSIT
    assert parcel.status is Status.CREATED
    with pytest.raises(ValueError):
        set_status(parcel, Status.DELIVERED)


def test_update_meta_returns_new_copy(parcel: Parcel) -> None:
    new = update_meta(parcel, carrier="UkrPost")
    assert new.meta["carrier"] == "UkrPost"
    assert parcel.meta["carrier"] == "NovaPost"
    assert new.meta["source"] == "shop"


def test_current_location(parcel: Parcel) -> None:
    assert current_location(parcel) == parcel.route[-1]


# ---------- read-only ----------
def test_frozen_fields(parcel: Parcel) -> None:
    with pytest.raises(FrozenInstanceError):
        parcel.status = Status.DELIVERED  # type: ignore[misc]


def test_meta_is_read_only(parcel: Parcel) -> None:
    with pytest.raises(TypeError):
        parcel.meta["carrier"] = "x"  # type: ignore[index]


def test_route_and_labels_have_no_mutators(parcel: Parcel) -> None:
    assert not hasattr(parcel.route, "append")
    assert not hasattr(parcel.labels, "add")


def test_make_meta_copies_source() -> None:
    src = {"a": "1"}
    meta = make_meta(src)
    src["a"] = "changed"
    src["b"] = "2"
    assert dict(meta) == {"a": "1"}


# ---------- хешованість ----------
def test_hashability(parcel: Parcel) -> None:
    other = add_route_point(parcel, RoutePoint("Kyiv", "Hub 2", "2026-11-20T15:00"))
    assert len({parcel, other}) == 2
    assert hash(parcel) == hash(parcel)


def test_parcel_as_dict_key(parcel: Parcel) -> None:
    index = {parcel: "first"}
    assert index[parcel] == "first"


def test_equal_parcels_have_equal_hash(parcel: Parcel) -> None:
    twin = Parcel(
        parcel.id,
        parcel.status,
        parcel.route,
        parcel.labels,
        make_meta(dict(parcel.meta)),
    )
    assert twin == parcel
    assert hash(twin) == hash(parcel)
