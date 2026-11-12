from __future__ import annotations
 
import argparse
import json
from pathlib import Path
 
from lab2 import Employee, build_pipeline, reduce_stats
 
 
def load_employees(path: Path) -> list[Employee]:
    with path.open(encoding="utf-8") as f:
        data: list[Employee] = json.load(f)
    return data
 
 
def main() -> None:
    parser = argparse.ArgumentParser(description="Лабораторна №2, варіант 9")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).parent / "sample_data.json",
    )
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--department", default="IT")
    parser.add_argument("--factor", type=float, default=1.1)
    parser.add_argument("--min-hours", type=float, default=100.0)
    args = parser.parse_args()
 
    employees = load_employees(args.data)
    pipeline = build_pipeline(
        department=args.department,
        factor=args.factor,
        minimum=args.min_hours,
        top_n=args.top,
    )
    result = pipeline(employees)
    stats = reduce_stats(result)
 
    print(f"Top-{args.top}:")
    for e in result:
        print(
            f"  {e['id']:>2}  {e['name']:<8} "
            f"{e['department']:<6} {e['total_hours']:.1f}"
        )
    print(
        "Статистика:",
        f"count={int(stats['count'])}",
        f"total_hours={stats['total_hours']:.1f}",
        f"avg_hours={stats['avg_hours']:.1f}",
    )
 
 
if __name__ == "__main__":
    main()