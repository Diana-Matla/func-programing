from typing import TypedDict, Literal, Callable

Status = Literal["confirmed", "cancelled", "pending"]
CarClass = Literal["premium", "economy", "basic"]

class Rental(TypedDict, total=False):
    id: int 
    car_class: CarClass
    daily_rate: float
    days: int
    status: Status
    total: float

AcceptFn = Callable[[Rental], bool] 
DiscountFn = Callable[[Rental], float]  
InsuranceFn = Callable[[Rental], float]

def base_price(rental: Rental) -> float:
    return rental["daily_rate"] * rental["days"]

def duration_discount_rate(rental: Rental) -> float:
    if rental["days"] >= 14: 
        return 0.15
    elif rental["days"] >= 7:
        return 0.1
    elif rental["days"] >= 3:
        return 0.05
    else: 
        return 0.0

def insurance_amount(rental: Rental) -> float:
    if rental["car_class"] == "economy":
        return 200.0
    elif rental["car_class"] == "basic":
        return 400.0
    else:
        return 600.0
    
def is_confirmed(rental: Rental) -> bool:
    return rental["status"] == "confirmed"

def calc_total(rental: Rental, rate: float, fee: float) -> float:
    return base_price(rental) * (1 - rate) + fee

def with_total(rental: Rental, total: float) -> Rental:
    return {**rental, "total": total}

def make_processor(*, accept: AcceptFn, discount_rate: DiscountFn, insurance: InsuranceFn,) -> Callable[[list[Rental]], dict[str, object]]:
    def process(rentals: list[Rental]) -> dict[str, object]:
        result = []
        for r in rentals:
            if accept(r):
                result.append(with_total(r, calc_total(r, discount_rate(r), insurance(r))))

        revenue = 0.0
        for r in result:
            revenue += r["total"]

        return {
            "count": len(result),
            "revenue": revenue,
            "rentals": result,
        }

    return process
    
    