from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from model import Parcel, RoutePoint, Status, make_meta

ALLOWED_TRANSITIONS: Mapping[Status, frozenset[Status]] = MappingProxyType(
    {
        Status.CREATED: frozenset({Status.IN_TRANSIT}),
        Status.IN_TRANSIT: frozenset({Status.OUT_FOR_DELIVERY, Status.RETURNED}),
        Status.OUT_FOR_DELIVERY: frozenset({Status.DELIVERED, Status.RETURNED}),
        Status.DELIVERED: frozenset(),
        Status.RETURNED: frozenset(),
    }
)


def add_route_point(parcel: Parcel, point: RoutePoint) -> Parcel:
    return replace(parcel, route=parcel.route + (point,))


def add_label(parcel: Parcel, label: str) -> Parcel:
    return replace(parcel, labels=parcel.labels | frozenset({label}))


def remove_label(parcel: Parcel, label: str) -> Parcel:
    return replace(parcel, labels=parcel.labels - frozenset({label}))


def set_status(parcel: Parcel, new_status: Status) -> Parcel:
    if new_status not in ALLOWED_TRANSITIONS[parcel.status]:
        raise ValueError(
            f"Неможливий перехід: {parcel.status.value} -> {new_status.value}"
        )
    return replace(parcel, status=new_status)


def update_meta(parcel: Parcel, **changes: str) -> Parcel:
    return replace(parcel, meta=make_meta({**parcel.meta, **changes}))


def current_location(parcel: Parcel) -> RoutePoint | None:
    return parcel.route[-1] if parcel.route else None


def route_cities(parcel: Parcel) -> tuple[str, ...]:
    return tuple(p.city for p in parcel.route)


def carrier(meta: Mapping[str, str]) -> str:
    return meta.get("carrier", "unknown")
