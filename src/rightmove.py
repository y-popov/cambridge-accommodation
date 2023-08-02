import requests
from typing import Iterable
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from src.api import BaseApi, Flat

user_agent = UserAgent()


class SmartFlat(Flat):
    ua = user_agent
    _data = None

    @property
    def data(self):
        if self._data is None:
            r = requests.get(self.url, headers={'User-Agent': self.ua.random})
            self._data = BeautifulSoup(r.text, 'html.parser')
        return self._data

    def get_date(self):
        date_block = self.data.find("dt", text='Let available date: ')
        self.available = date_block.nextSibling.get_text()

    @property
    def furnished(self):
        if self._furnished is None:
            block = self.data.find("dt", text='Furnish type: ')
            self._furnished = block.nextSibling.get_text()
        return self._furnished


class RightmoveApi(BaseApi):
    base_url = 'https://www.rightmove.co.uk'
    config_filename = 'rightmove_query.json'

    def get_flats(self) -> Iterable[SmartFlat]:
        for furnish_type in self.config['furnish_types']:
            resp = requests.get(
                url=f'{self.base_url}/property-to-rent/find.html',
                params={
                    'minBedrooms': self.config['minBedrooms'],
                    'maxPrice': self.config['maxPrice'],
                    'dontShow': self.config['dontShow'],
                    'furnishTypes': furnish_type,
                    'locationIdentifier': self.config['locationIdentifier'],
                    'radius': self.config['radius']
                }
            )

            if resp.status_code != 200:
                raise requests.HTTPError(resp.text)

            soup = BeautifulSoup(resp.text, 'html.parser')

            for e in soup.find_all("div", class_="propertyCard-wrapper"):
                link_block = e.find('a', class_='propertyCard-link')
                title_block = e.find('h2', class_='propertyCard-title')
                price_block = e.find('span', class_='propertyCard-priceValue')
                link = link_block['href'].split('?')[0].replace('#', '')
                title = title_block.get_text().strip()
                price = price_block.get_text()

                if link == '':
                    continue

                flat = SmartFlat(
                    id=int(link.split('/')[-2]),
                    url=f"{self.base_url}{link}",
                    price=price,
                    available=None,
                    _furnished=None,
                    title=title,
                    _type=None
                )

                yield flat
