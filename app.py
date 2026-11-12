from core import (Rental, duration_discount_rate, insurance_amount, is_confirmed, make_processor,)

rentals: list[Rental] = [
    {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 2,
        "status": "confirmed",
    },
    {
        "id": 2,
        "car_class": "premium",
        "daily_rate": 3000.0,
        "days": 14,
        "status": "confirmed",
    },
    {
        "id": 3,
        "car_class": "basic",
        "daily_rate": 1500.0,
        "days": 7,
        "status": "pending",
    },
    {
        "id": 4,
        "car_class": "economy",
        "daily_rate": 1200.0,
        "days": 5,
        "status": "cancelled",
    },
]

processor = make_processor(
    accept=is_confirmed,
    discount_rate=duration_discount_rate,
    insurance=insurance_amount,
)

result = processor(rentals)

print("=" * 45)
print("       CAR RENTAL — ЗВІТ ПРО ОРЕНДУ")
print("=" * 45)

print(f"Кількість підтверджених оренд: {result['count']}")
print("-" * 45)

for rental in result["rentals"]:
    print(f"Оренда №{rental['id']}")
    print(f"  Клас автомобіля: {rental['car_class']}")
    print(f"  Ціна за день:    {rental['daily_rate']:.2f} грн")
    print(f"  Кількість днів:  {rental['days']}")
    print(f"  Страховка:       {insurance_amount(rental):.2f} грн")
    print(f"  Загальна вартість: {rental['total']:.2f} грн")
    print("-" * 45)

print(f"ЗАГАЛЬНИЙ ДОХІД: {result['revenue']:.2f} грн")
print("=" * 45)

