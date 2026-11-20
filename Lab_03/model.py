from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType


class Status(str, Enum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"


def make_meta(
    data: Mapping[str, str] | None = None, **kwargs: str
) -> MappingProxyType[str, str]:
    """Копіюємо джерело, щоб ззовні ніхто не тримав посилання на сирий dict."""
    base: dict[str, str] = dict(data) if data else {}
    base.update(kwargs)
    return MappingProxyType(base)


@dataclass(frozen=True, slots=True)
class RoutePoint:
    city: str
    address: str
    timestamp: str


@dataclass(frozen=True, slots=True)
class Parcel:
    id: int
    status: Status
    route: tuple[RoutePoint, ...]
    labels: frozenset[str]
    meta: Mapping[str, str] = field(hash=False)
