from dataclasses import dataclass


@dataclass
class Quote:
    price: float
    currency: str
