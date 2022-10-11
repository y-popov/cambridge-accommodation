from typing import Iterable
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class Flat:
    id: int
    url: str
    price: str
    available: str
    type: str
    
    @property
    def label(self) -> str:
        return f'{self.type} for {self.price} available from {self.available}'

    def get_date(self):
        pass


class BaseApi:

    @property
    @abstractmethod
    def base_url(self) -> str:
        return 'https://www.example.co.uk'

    @abstractmethod
    def get_flats(self) -> Iterable[Flat]:
        pass
