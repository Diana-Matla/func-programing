
import pytest

from core import (
    Rental,
    base_price,
    duration_discount_rate,
    insurance_amount,
    is_confirmed,
    calc_total,
    with_total,
    make_processor,
)


@pytest.fixture
def sample_rentals() -> list[Rental]:
    return [
        {
            "id": 1,
            "car_class": "economy",
            "daily_rate": 1000.0,
            "days": 7,
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
            "daily_rate": 800.0,
            "days": 3,
            "status": "pending",
        },
    ]


def test_referential_transparency(sample_rentals):
    processor = make_processor(
        accept=is_confirmed,
        discount_rate=duration_discount_rate,
        insurance=insurance_amount,
    )

    result1 = processor(sample_rentals)
    result2 = processor(sample_rentals)

    assert result1 == result2


def test_no_mutation(sample_rentals):
    from copy import deepcopy

    original = deepcopy(sample_rentals)

    processor = make_processor(
        accept=is_confirmed,
        discount_rate=duration_discount_rate,
        insurance=insurance_amount,
    )

    processor(sample_rentals)

    assert sample_rentals == original


def test_callable_policies(sample_rentals):
    def accept(rental: Rental) -> bool:
        return rental["daily_rate"] >= 1000

    def discount_rate(rental: Rental) -> float:
        return 0.0

    def insurance(rental: Rental) -> float:
        return 200.0

    processor = make_processor(
        accept=accept,
        discount_rate=discount_rate,
        insurance=insurance,
    )

    result = processor(sample_rentals)

    assert result["count"] == 2
    assert result["revenue"] == 7 * 1000 + 200 + 14 * 3000 + 200


def test_base_price():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 7,
        "status": "confirmed",
    }

    assert base_price(rental) == 7000.0


def test_duration_discount_rate():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 7,
        "status": "confirmed",
    }

    assert duration_discount_rate(rental) == 0.1

    rental["days"] = 14
    assert duration_discount_rate(rental) == 0.15


def test_insurance_amount():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 2,
        "status": "confirmed",
    }

    assert insurance_amount(rental) == 200.0

    rental["car_class"] = "basic"
    assert insurance_amount(rental) == 400.0

    rental["car_class"] = "premium"
    assert insurance_amount(rental) == 600.0


def test_is_confirmed():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 2,
        "status": "confirmed",
    }

    assert is_confirmed(rental) is True

    rental["status"] = "cancelled"
    assert is_confirmed(rental) is False


def test_calc_total():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 7,
        "status": "confirmed",
    }

    assert calc_total(rental, 0.1, 100.0) == 6400.0


def test_with_total():
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "daily_rate": 1000.0,
        "days": 2,
        "status": "confirmed",
    }

    updated = with_total(rental, 2100.0)

    assert updated["total"] == 2100.0
    assert "total" not in rental