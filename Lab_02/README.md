# Лабораторна робота №2, варіант 9: працівники компанії

## Варіант 9.Працівники компанії 

### Мета: функції вищого порядку, lambda, map/filter/reduce, композиція функцій.

Конвеєр без мутацій над списком працівників: сумарні години (map) -> коефіцієнт відділу -> фільтр за мінімумом (filter) -> сортування (години спадно, id зростаюче) -> Top-N (islice). Агрегація через reduce: count, total_hours, avg_hours.

### Структура
* lab2/lab2.py - чисті функції (типи, compose, pipe, juxt, кроки, reduce_stats)
* lab2/main.py - CLI (лише ввід/вивід)
* lab2/sample_data.json - приклад даних
* lab2/tests/test_lab2.py - тести pytest
* ASSIGNMENT.md - завдання та критерії оцінювання

### Запуск
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python -m lab2.main --data lab2/sample_data.json --top 3 --department IT --factor 1.1 --min-hours 100
black --check . && ruff check . && mypy lab2