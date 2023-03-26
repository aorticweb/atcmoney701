from dataclasses import dataclass


@dataclass
class Quote:
    """Data model for a quote.

    Data model for a quote usually provided from a data provider Client.

    Args:
        price: quote price
        currency: quote currency
    """

    price: float
    currency: str
