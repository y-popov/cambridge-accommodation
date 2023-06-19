import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Iterable
from datetime import date, timedelta
from src.api import BaseApi, Flat


class AccommodationApi(BaseApi):
    base_url = "https://www.accommodation.cam.ac.uk"
    config_filename = 'accommodation_query.json'

    def __init__(self):
        self.session = requests.Session()
        self.soup = None
        super().__init__()

    def send_post(self, url: str, data: Dict = None) -> requests.Response:
        r = self.session.post(url, data=data)
        self.soup = BeautifulSoup(r.text, "html.parser")
        return r

    def get_viewstate(self) -> Dict[str, str]:
        data = {
            e['id']: e['value']
            for e in self.soup.find_all("input", type="hidden")
            if e['id'].startswith('__')
        }
        return data

    def get_form_data(self) -> Dict[str, str]:
        data = {}
        for e in self.soup.find_all("input"):
            if e.get('name', '').startswith('_ctl0'):
                if e.get('type') == 'submit':
                    continue
                elif 'value' in e.attrs.keys():
                    data[e['name']] = e['value']
                elif e.get('type') == 'checkbox':
                    if e.get('checked') == 'checked':
                        data[e['name']] = 'on'
                else:
                    logging.warning(f'Unknown input element: {e}')
        for e in self.soup.find_all("select"):
            for o in e.find_all('option'):
                if o.get('selected') == 'selected':
                    data[e['name']] = o['value']
                    break
        return data

    def get_form_buttons(self) -> Dict[str, str]:
        data = {}
        for e in self.soup.find_all("input"):
            if e.get('name', '').startswith('_ctl0'):
                if e.get('type') == 'submit':
                    data[e['name']] = e['value']
        return data

    def login(self, login: str, password: str) -> None:
        login_url = f'{self.base_url}/Login.aspx'
        self.send_post(login_url)

        viewstate = self.get_viewstate()
        form = self.get_form_data()
        buttons = self.get_form_buttons()

        form['_ctl0:_ctl0:cpFull:cpFull:ctlLoginBox:tbLoginName'] = login
        form['_ctl0:_ctl0:cpFull:cpFull:ctlLoginBox:tbPassword'] = password

        r = self.send_post(login_url, data={**viewstate, **form, **buttons})
        if r.status_code != 200:
            raise requests.HTTPError()
        if not self.soup.find("a", text='Log Out'):
            raise ValueError('Authorisation error occurred')
        logging.info(f'Successfully authenticated at {self.base_url}')

    def get_flats(self) -> Iterable[Flat]:
        search_url = f'{self.base_url}/Client/Adverts/Search.aspx'
        self.send_post(search_url)

        viewstate = self.get_viewstate()
        form = self.get_form_data()
        buttons = self.get_form_buttons()
        search_button = {k: v for k, v in buttons.items() if k.endswith('btnSearch')}

        for key, value in self.config.items():
            form[f'_ctl0:_ctl0:cpFull:cpFull:{key}'] = value

        self.send_post(search_url, data={**viewstate, **form, **search_button})

        search_list = self.soup.find("ul", class_="search__results-list")
        for el in search_list.find_all("li"):
            if 'results-header' in el.get('class', []):
                continue

            prop_uri = el.find("div", class_="prop-link").find("a")['href']
            prop_type = el.find(class_='prop-type').get_text().strip()
            rent_price = el.find(class_='rent-price').get_text().strip()
            prop_available = el.find(class_="available-from").get_text().strip()

            flat = Flat(
                id=int(el['id']),
                url=f'{self.base_url}{prop_uri}',
                price=rent_price[1:],
                available=prop_available,
                type=prop_type
            )
            logging.debug(f'Found {flat}')
            yield flat
