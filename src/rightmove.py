import requests
from bs4 import BeautifulSoup


class RightmoveApi:
    base_url = 'https://www.rightmove.co.uk'

    def get_flats(self):
        resp = requests.get(
            url=f'{self.base_url}/property-to-rent/find.html',
            params={
                'minBedrooms': 1,
                'maxPrice': 1500,
                'dontShow': 'houseShare,student',
                'furnishTypes': 'partFurnished,furnished',
                'locationIdentifier': 'REGION^274'
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

            r = requests.get(f"{self.base_url}{link}")
            s = BeautifulSoup(r.text, 'html.parser')
            date_block = s.find("dt", text='Let available date: ')
            date = date_block.nextSibling.get_text()

            flat = {
                'id': int(link.split('/')[-2]),
                'url': f"{self.base_url}{link}",
                'label': f"{title} for {price} available from {date}",
                'price': price
            }

            yield flat
