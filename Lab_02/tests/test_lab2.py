from __future__ import annotations

import copy

import pytest

from lab2 import (
    Employee,
    build_pipeline,
    calculate_hours,
    compose,
    juxt,
    min_hours,
    pipe,
    reduce_stats,
    sort_by_hours_desc,
    take,
    with_total_hours,
)


@pytest.fixture
def employees() -> list[Employee]:
    return [
        {"id": 1, "name": "Ann", "department": "IT", "monthly_hours": [160, 150, 170]},
        {"id": 2, "name": "Bob", "department": "HR", "monthly_hours": [120, 130, 125]},
        {"id": 3, "name": "Olha", "department": "IT", "monthly_hours": [140, 145, 150]},
        {"id": 4, "name": "Taras", "department": "Sales", "monthly_hours": [160] * 3},
        {"id": 5, "name": "Iryna", "department": "HR", "monthly_hours": [30, 40, 20]},
        {"id": 6, "name": "Petro", "department": "Sales", "monthly_hours": [150] * 3},
        {"id": 7, "name": "Maria", "department": "IT", "monthly_hours": [100, 90, 80]},
    ]


def test_calculate_hours() -> None:
    e: Employee = {"id": 1, "name": "A", "department": "IT", "monthly_hours": [1, 2.5]}
    assert calculate_hours(e)["total_hours"] == 3.5


def test_top_n_order_and_values(employees: list[Employee]) -> None:
    result = build_pipeline("IT", 1.1, 100.0, 3)(employees)
    assert [e["id"] for e in result] == [1, 4, 3]
    assert result[0]["total_hours"] == pytest.approx(528.0)
    assert result[2]["total_hours"] == pytest.approx(478.5)


def test_top_n_larger_than_data(employees: list[Employee]) -> None:
    result = build_pipeline("IT", 1.1, 100.0, 100)(employees)
    assert [e["id"] for e in result] == [1, 4, 3, 6, 2, 7]


def test_top_zero(employees: list[Employee]) -> None:
    assert build_pipeline(top_n=0)(employees) == []


def test_take_negative_raises() -> None:
    with pytest.raises(ValueError):
        take(-1)


def test_min_hours_filters_out_low(employees: list[Employee]) -> None:
    result = build_pipeline("IT", 1.1, 100.0, 100)(employees)
    assert 5 not in [e["id"] for e in result]


def test_min_hours_threshold_is_inclusive() -> None:
    e: Employee = {"id": 1, "name": "A", "department": "X", "monthly_hours": [100]}
    assert len(min_hours(100.0)(with_total_hours([e]))) == 1


def test_factor_applies_only_to_department(employees: list[Employee]) -> None:
    result = build_pipeline("IT", 2.0, 0.0, 100)(employees)
    by_id = {e["id"]: e["total_hours"] for e in result}
    assert by_id[1] == pytest.approx(960.0)
    assert by_id[4] == pytest.approx(480.0)
    assert by_id[2] == pytest.approx(375.0)


def test_sort_tie_breaker_by_id() -> None:
    items = with_total_hours(
        [
            {"id": 5, "name": "E", "department": "X", "monthly_hours": [10]},
            {"id": 2, "name": "B", "department": "X", "monthly_hours": [10]},
            {"id": 9, "name": "I", "department": "X", "monthly_hours": [20]},
        ]
    )
    assert [e["id"] for e in sort_by_hours_desc(items)] == [9, 2, 5]


def test_no_mutation(employees: list[Employee]) -> None:
    snapshot = copy.deepcopy(employees)
    result = build_pipeline("IT", 1.1, 100.0, 3)(employees)
    assert employees == snapshot
    assert all("total_hours" not in e for e in employees)
    assert all(r is not e for r in result for e in employees)


def test_steps_do_not_mutate(employees: list[Employee]) -> None:
    snapshot = copy.deepcopy(employees)
    processed = with_total_hours(employees)
    processed_snapshot = copy.deepcopy(processed)
    sort_by_hours_desc(processed)
    min_hours(200.0)(processed)
    take(2)(processed)
    assert employees == snapshot
    assert processed == processed_snapshot


def test_reduce_stats(employees: list[Employee]) -> None:
    result = build_pipeline("IT", 1.1, 100.0, 3)(employees)
    stats = reduce_stats(result)
    assert stats["count"] == 3
    assert stats["total_hours"] == pytest.approx(528.0 + 480.0 + 478.5)
    assert stats["avg_hours"] == pytest.approx((528.0 + 480.0 + 478.5) / 3)


def test_reduce_stats_empty() -> None:
    assert reduce_stats([]) == {"count": 0.0, "total_hours": 0.0, "avg_hours": 0.0}


def test_compose_applies_right_to_left() -> None:
    def add_one(x: int) -> int:
        return x + 1

    def double(x: int) -> int:
        return x * 2

    assert compose(add_one, double)(5) == 11  # add_one(double(5))
    assert compose()(5) == 5


def test_pipe_applies_left_to_right() -> None:
    def add_one(x: int) -> int:
        return x + 1

    def double(x: int) -> int:
        return x * 2

    assert pipe(add_one, double)(5) == 12  # double(add_one(5))


def test_pipe_equals_reversed_compose() -> None:
    def f(x: int) -> int:
        return x - 3

    def g(x: int) -> int:
        return x * x

    assert pipe(f, g)(7) == compose(g, f)(7)


def test_juxt() -> None:
    assert juxt(lambda x: x + 1, lambda x: x * 2)(4) == (5, 8)