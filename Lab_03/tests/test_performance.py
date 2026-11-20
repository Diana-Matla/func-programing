from __future__ import annotations

from typing import Any

from core import add_label, add_route_point
from model import Parcel, RoutePoint, Status, make_meta


def build_parcel(n_points: int) -> Parcel:
    route = tuple(
        RoutePoint(f"City{i}", "Addr", "2026-11-20T10:00") for i in range(n_points)
    )
    return Parcel(1, Status.CREATED, route, frozenset({"a"}), make_meta(k="v"))


def test_add_point_benchmark(benchmark: Any) -> None:
    p = build_parcel(100)
    point = RoutePoint("X", "Y", "2026-11-20T11:00")
    benchmark(lambda: add_route_point(p, point))


def test_add_label_benchmark(benchmark: Any) -> None:
    p = build_parcel(100)
    benchmark(lambda: add_label(p, "vip"))


def test_large_route_pipeline() -> None:
    p = build_parcel(0)
    for i in range(2000):
        p = add_route_point(p, RoutePoint(f"C{i}", "A", "t"))
    assert len(p.route) == 2000
