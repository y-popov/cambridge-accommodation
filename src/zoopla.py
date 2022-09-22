import requests
from bs4 import BeautifulSoup


class ZooplaApi:
    base_url = 'https://www.zoopla.co.uk'

    def get_flats(self):
        furnished_states = ('furnished', 'part_furnished')
        for furnished_state in furnished_states:
            r = requests.get(
                url=f'{self.base_url}/to-rent/property/cambridge-city-centre/',
                params={
                    'price_frequency': 'per_month',
                    'beds_min': 1,
                    'price_max': 1500,
                    'available_from': '1months',
                    'include_shared_accommodation': False,
                    'furnished_state': furnished_state,
                    'radius': 1
                }
            )
            s = BeautifulSoup(r.text, 'html.parser')

            for res in s.find_all("div", attrs={'data-testid': "search-result"}):
                link_block = res.find("a", attrs={'data-testid': "listing-details-link"})
                price_block = res.find("div", attrs={'data-testid': "listing-price"})
                date_block = res.find("span", attrs={'data-testid': "available-from-date"})
                property_block = res.find("h2", attrs={'data-testid': "listing-title"})
                link = link_block["href"].split('?')[0]

                flat = {
                    'id': int(link.split('/')[-2]),
                    'url': f'{self.base_url}{link}',
                    'price': price_block.findChild().get_text(),
                    'available': date_block.get_text().lstrip(),
                    'property': property_block.get_text(),
                }
                flat['label'] = f'{flat["property"]} for {flat["price"]} available from {flat["available"]}'

                yield flat

