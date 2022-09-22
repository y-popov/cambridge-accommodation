import os
import flask
import logging
import functions_framework

from src.s3_tools import load_flats, write_flats, check_s3
from src.accommodation import AccommodationApi
from src.telegram import send_tg_message
from src.rightmove import RightmoveApi
from src.zoopla import ZooplaApi
from google.cloud import storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)

gs = storage.Client()


def main():
    bucket = check_s3(gs=gs)

    apis = {
        'accommodation': AccommodationApi(),
        'rightmove': RightmoveApi(),
        'zoopla': ZooplaApi()
    }

    apis['accommodation'].login(login=os.getenv('ACCOMMODATION_LOGIN'), password=os.getenv('ACCOMMODATION_PASSWORD'))

    old_flats = load_flats(gs=bucket)

    for api_key, api in apis.items():
        if api_key not in old_flats:
            old_flats[api_key] = []

        for flat in api.get_flats():
            if flat['id'] not in old_flats[api_key]:
                message = f'{flat["label"]} [View]({flat["url"]})'
                send_tg_message(message)
                old_flats[api_key].append(flat['id'])

    write_flats(gs=bucket, flats=old_flats)


@functions_framework.http
def handler(request: flask.Request):
    main()
    return 'ok'


if __name__ == '__main__':
    from dotenv import load_dotenv
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    main()
