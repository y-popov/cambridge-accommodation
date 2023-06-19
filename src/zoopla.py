import json
import requests
from typing import Iterable
from bs4 import BeautifulSoup
from src.api import BaseApi, Flat


class ZooplaApi(BaseApi):
    base_url = 'https://www.zoopla.co.uk'
    config_filename = 'zoopla_query.json'

    def get_flats(self) -> Iterable[Flat]:
        for furnished_state in self.config['furnished_state']:
            r = requests.get(
                url=f'{self.base_url}/to-rent/property/{self.config["location"]}/',
                params={
                    'price_frequency': self.config['price_frequency'],
                    'beds_min': self.config['beds_min'],
                    'price_max': self.config['price_max'],
                    'available_from': self.config['available_from'],
                    'is_shared_accommodation': json.dumps(self.config['is_shared_accommodation']),
                    'is_retirement_home': json.dumps(self.config['is_retirement_home']),
                    'furnished_state': furnished_state,
                    'radius': self.config['radius']
                }
            )
            s = BeautifulSoup(r.text, 'html.parser')

            for res in s.find_all("div", attrs={'data-testid': "search-result"}):
                link_block = res.find("a", attrs={'data-testid': "listing-details-link"})
                price_block = res.find("div", attrs={'data-testid': "listing-price"})
                date_block = res.find("span", attrs={'data-testid': "available-from-date"})
                property_block = res.find("h2", attrs={'data-testid': "listing-title"})
                link = link_block["href"].split('?')[0]

                flat = Flat(
                    id=int(link.split('/')[-2]),
                    url=f'{self.base_url}{link}',
                    price=price_block.findChild().get_text(),
                    available=date_block.get_text().lstrip(),
                    type=property_block.get_text()
                )

                yield flat
