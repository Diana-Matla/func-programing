from __future__ import annotations

from core import (
    add_label,
    add_route_point,
    current_location,
    route_cities,
    set_status,
    update_meta,
)
from model import Parcel, RoutePoint, Status, make_meta


def main() -> None:
    parcel = Parcel(
        id=1,
        status=Status.CREATED,
        route=(RoutePoint("Lviv", "Hub 1", "2026-11-20T09:00:00"),),
        labels=frozenset({"fragile"}),
        meta=make_meta(carrier="NovaPost", source="shop"),
    )

    p2 = add_route_point(parcel, RoutePoint("Kyiv", "Hub 2", "2026-11-20T15:00:00"))
    p3 = add_label(p2, "priority")
    p4 = set_status(p3, Status.IN_TRANSIT)
    p5 = update_meta(p4, carrier="UkrPost")

    print("Початкова посилка:")
    print(f"  статус: {parcel.status.value}, маршрут: {route_cities(parcel)}")
    print(f"  мітки: {sorted(parcel.labels)}, перевізник: {parcel.meta['carrier']}")

    print("Після pure-оновлень (початкова не змінилась):")
    print(f"  статус: {p5.status.value}, маршрут: {route_cities(p5)}")
    print(f"  мітки: {sorted(p5.labels)}, перевізник: {p5.meta['carrier']}")
    print(f"  поточна точка: {current_location(p5)}")

    print(f"Це різні об'єкти: {parcel is not p5}")
    print(f"Хеші різні: {hash(parcel) != hash(p5)}")


if __name__ == "__main__":
    main()
