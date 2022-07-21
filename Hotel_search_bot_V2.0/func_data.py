from dataclasses import dataclass


@dataclass
class Hotel:
    id: str
    name: str
    address: dict
    landmarks: list
    price: str
    coordinate: str


@dataclass
class QueryString:
    destinationId: str = None
    pageNumber: str = '1'
    pageSize: str = None
    checkIn: str = None
    checkOut: str = None
    adults1: str = '1'
    sortOrder: str = None
    locale: str = None
    currency: str = None
    priceMin: int = None
    priceMax: int = None


