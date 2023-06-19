import json
import os.path
from typing import Iterable, Dict, Any
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
    def __init__(self):
        self.config = self.load_config()

    @property
    @abstractmethod
    def base_url(self) -> str:
        return 'https://www.example.co.uk'

    @property
    @abstractmethod
    def config_filename(self) -> str:
        return 'config.json'

    @abstractmethod
    def get_flats(self) -> Iterable[Flat]:
        pass

    def load_config(self) -> Dict[str, Any]:
        with open(os.path.join('assets', self.config_filename)) as f:
            return json.load(f)
