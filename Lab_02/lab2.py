"""Лабораторна робота №2, варіант 9: працівники компанії.
 
Усі функції тут "чисті": вони не змінюють вхідні дані й не роблять I/O.
"""
 
from __future__ import annotations
 
from collections.abc import Callable, Iterable
from functools import reduce
from itertools import islice
from typing import Any, TypedDict
 
 
class Employee(TypedDict):
    id: int
    name: str
    department: str
    monthly_hours: list[float]
 
 
class ProcessedEmployee(Employee):
    total_hours: float
 
 
Step = Callable[[Iterable[ProcessedEmployee]], list[ProcessedEmployee]]
 
 
def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """compose(f, g, h)(x) == f(g(h(x))): функції застосовуються справа наліво."""
 
    def _composed(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x
 
    return _composed
 
 
def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """pipe(f, g, h)(x) == h(g(f(x))): функції застосовуються зліва направо."""
    return compose(*reversed(funcs))
 
 
def juxt(*funcs: Callable[[Any], Any]) -> Callable[[Any], tuple[Any, ...]]:
    """juxt(f, g)(x) == (f(x), g(x))."""
    return lambda x: tuple(map(lambda f: f(x), funcs))
 
 
def calculate_hours(employee: Employee) -> ProcessedEmployee:
    return {**employee, "total_hours": float(sum(employee["monthly_hours"]))}
 
 
def with_total_hours(employees: Iterable[Employee]) -> list[ProcessedEmployee]:
    return list(map(calculate_hours, employees))
 
 
def apply_department_factor(department: str, factor: float) -> Step:
    return lambda employees: [
        (
            {**e, "total_hours": e["total_hours"] * factor}
            if e["department"] == department
            else e
        )
        for e in employees
    ]
 
 
def min_hours(threshold: float) -> Step:
    return lambda employees: list(
        filter(lambda e: e["total_hours"] >= threshold, employees)
    )
 
 
def sort_by_hours_desc(
    employees: Iterable[ProcessedEmployee],
) -> list[ProcessedEmployee]:
    return sorted(employees, key=lambda e: (-e["total_hours"], e["id"]))
 
 
def take(n: int) -> Step:
    if n < 0:
        raise ValueError("n must be non-negative")
    return lambda employees: list(islice(employees, n))
 
 
def reduce_stats(employees: Iterable[ProcessedEmployee]) -> dict[str, float]:
    initial = {"count": 0.0, "total_hours": 0.0}
    acc = reduce(
        lambda a, e: {
            "count": a["count"] + 1,
            "total_hours": a["total_hours"] + e["total_hours"],
        },
        employees,
        initial,
    )
    if acc["count"]:
        avg = acc["total_hours"] / acc["count"]
    else:
        avg = 0.0
 
    return {
        "count": acc["count"],
        "total_hours": acc["total_hours"],
        "avg_hours": avg,
    }
 
 
def build_pipeline(
    department: str = "IT",
    factor: float = 1.1,
    minimum: float = 100.0,
    top_n: int = 3,
) -> Callable[[Iterable[Employee]], list[ProcessedEmployee]]:
    return pipe(
        with_total_hours,
        apply_department_factor(department, factor),
        min_hours(minimum),
        sort_by_hours_desc,
        take(top_n),
    )