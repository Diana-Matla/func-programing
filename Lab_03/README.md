# Лабораторна робота 3. Незмінні структури даних (immutability) у Python

**Варіант 9:** система доставки (`Parcel`, `RoutePoint`, `labels`, `meta`).

## Структура проєкту

```
Lab_03/
├── README.md
├── model.py                 # frozen dataclasses (RoutePoint, Parcel), Status, make_meta
├── core.py                  # pure-оновлення та чисті запити
├── mutable_baseline.py      # мутабельна версія для порівняння часу
├── tests/
│   ├── test_immutability.py
│   └── test_performance.py
├── requirements.txt
├── pyproject.toml
└── mypy.ini
```

## Модель

| Сутність / поле | Реалізація | Чому |
|-----------------|-----------|------|
| `RoutePoint` | `@dataclass(frozen=True, slots=True)` | незмінна точка маршруту |
| `Parcel` | `@dataclass(frozen=True, slots=True)` | незмінна посилка |
| `Parcel.route` | `tuple[RoutePoint, ...]` | маршрут не змінюється на місці |
| `Parcel.labels` | `frozenset[str]` | мітки: порядок неважливий, хешованість |
| `Parcel.meta` | `MappingProxyType[str, str]` | read-only мапа, джерело копіюється в `make_meta` |
| `Status` | `Enum` | допустимі статуси посилки |

### Pure-оновлення (`core.py`)

- `add_route_point(parcel, point)`: конкатенація tuple + `dataclasses.replace`
- `add_label(parcel, label)` / `remove_label(parcel, label)`: операції `frozenset`
- `set_status(parcel, new_status)`: перевірка допустимих переходів (`ALLOWED_TRANSITIONS`) + `replace`
- `update_meta(parcel, **changes)`: нова read-only мапа через `make_meta`

Усі функції повертають **нову** копію `Parcel` і не змінюють вхідний об'єкт.

### Хешованість

`Parcel` хешований: `route` (tuple), `labels` (frozenset) та інші поля хешовані. Єдине поле, яке заважає хешуванню, це `meta`, оскільки `MappingProxyType` не є хешованим. Тому воно позначене `field(hash=False)`: у `__hash__` не бере участі, але в `__eq__` лишається. Завдяки цьому `Parcel` можна класти в `set` і використовувати як ключ у `dict`.

## Запуск

Команди виконуються з папки `Lab_03`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q --durations=5
python -m pytest --benchmark-min-rounds=10
python -m mypy .
python -m black --check .
python -m ruff check .
python mutable_baseline.py
```

## Результати

### Тести

```
15 passed in 1.05s
```

`mypy`: `Success: no issues found in 5 source files`. `black` і `ruff`: без зауважень (`All checks passed!`).

### Найповільніші тести (`pytest --durations=5`)

| Тест | Час |
|------|-----|
| `test_add_label_benchmark` | 0.41 s |
| `test_add_point_benchmark` | 0.36 s |
| `test_large_route_pipeline` | 0.01 s |

### pytest-benchmark (immutable, маршрут із 100 точок)

| Операція | Mean | Median | OPS (Kops/s) |
|----------|------|--------|--------------|
| `add_label` | 2.90 мкс | 2.90 мкс | 345.00 |
| `add_route_point` | 3.64 мкс | 2.80 мкс | 274.96 |

### Порівняння з мутабельною версією (`mutable_baseline.py`, 100 000 ітерацій, маршрут із 100 точок)

| Операція | Мутабельна версія | Immutable версія | Різниця |
|----------|------------------|------------------|---------|
| Додати точку маршруту | 0.0056 s | 0.4459 s | ≈ 80× |
| Додати мітку | 0.0047 s | 0.2987 s | ≈ 64× |

Примітка: у мутабельному варіанті список накопичує елементи між викликами, а в immutable кожен виклик працює з тим самим початковим `Parcel`, тому порівняння не повністю симетричне. Для оцінки порядку накладних витрат цього достатньо. Абсолютні значення трохи змінюються від запуску до запуску.

## Висновок

**Переваги.** Перехід на незмінну модель (`frozen` dataclass, `tuple`, `frozenset`, `MappingProxyType`) прибрав приховані побічні ефекти: тести стали простішими (достатньо порівняти значення, не потрібно стежити за станом), `Parcel` став хешованим і придатним як ключ у `dict`/`set`, а читання даних безпечне при роботі з кількох потоків. Стара версія посилки лишається коректною після будь-якого оновлення, що зручно для історії змін і відлагодження.

**Накладні витрати.** Окрема операція оновлення приблизно в 60-80 разів повільніша за мутабельну, бо щоразу створюється новий об'єкт, а додавання до `tuple` копіює всю послідовність (O(n) від довжини маршруту). В абсолютних числах це близько 3-4 мкс на операцію, що для типових задач обліку посилок несуттєво, а весь набір із 15 тестів виконується за ≈1.05 с. Для дуже довгих маршрутів або гарячих циклів варто групувати оновлення або використовувати персистентні структури даних.

**Обмеження.** `MappingProxyType` забезпечує лише поверхневу (shallow) незмінність і не хешується, тому `meta` виключено з `__hash__` через `field(hash=False)`. Копіювання вхідного словника в `make_meta` захищає від зовнішніх змін оригінального `dict`.