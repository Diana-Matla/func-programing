from __future__ import annotations

import timeit

from core import add_label, add_route_point
from model import Parcel, RoutePoint, Status, make_meta

# мутабельна версія
mutable = {
    "id": 1,
    "route": [RoutePoint(f"C{i}", "A", "t") for i in range(100)],
    "labels": {"a"},
}
immutable = Parcel(
    1,
    Status.CREATED,
    tuple(RoutePoint(f"C{i}", "A", "t") for i in range(100)),
    frozenset({"a"}),
    make_meta(k="v"),
)
point = RoutePoint("X", "Y", "t")

N = 100_000
t_mut = timeit.timeit(lambda: mutable["route"].append(point), number=N)
t_imm = timeit.timeit(lambda: add_route_point(immutable, point), number=N)
print(f"mutable append:   {t_mut:.4f}s")
print(f"immutable update: {t_imm:.4f}s")

t_mut = timeit.timeit(lambda: mutable["labels"].add("vip"), number=N)
t_imm = timeit.timeit(lambda: add_label(immutable, "vip"), number=N)
print(f"mutable add label:   {t_mut:.4f}s")
print(f"immutable add label: {t_imm:.4f}s")
