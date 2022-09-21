import os
import boto3
import logging

from src.s3_tools import load_flats, write_flats, check_s3
from src.accommodation import AccommodationApi
from src.telegram import send_tg_message
from src.zoopla import ZooplaApi

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    endpoint_url='https://storage.yandexcloud.net',
    region_name='ru-central1'
)


def main():
    check_s3(s3=s3)

    apis = {
        'accommodation': AccommodationApi(),
        'zoopla': ZooplaApi()
    }

    apis['accommodation'].login(login=os.getenv('ACCOMMODATION_LOGIN'), password=os.getenv('ACCOMMODATION_PASSWORD'))

    old_flats = load_flats(s3=s3)

    for api_key in apis:
        for flat in apis[api_key].get_flats():
            if flat['id'] not in old_flats[api_key]:
                message = f'{flat["label"]} [View]({flat["url"]})'
                send_tg_message(message)
                old_flats[api_key].append(flat['id'])

    write_flats(s3=s3, flats=old_flats)


def handler(event, context):
    main()


if __name__ == '__main__':
    from dotenv import load_dotenv
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    main()
