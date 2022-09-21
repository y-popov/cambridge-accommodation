import os
import logging
from typing import List
from botocore import client


def check_s3(s3: client.BaseClient):
    bucket = os.getenv('BUCKET')
    if bucket is None or len(bucket) == 0:
        raise ValueError('System variable `BUCKET` is empty!')
    bucket_names = {x['Name'] for x in s3.list_buckets(Bucket=bucket)['Buckets']}
    if bucket not in bucket_names:
        raise ValueError(f'Bucket {bucket} does not exist!')
    logging.info('s3 configuration is OK')


def load_flats(s3: client.BaseClient) -> List[str]:
    resp = s3.get_object(Bucket=os.getenv('BUCKET'), Key='accommodations.txt')
    flat_ids = resp['Body'].read().decode().split()
    logging.info(f'Successfully read {len(flat_ids)} flat ids from s3')
    return flat_ids


def write_flats(s3: client.BaseClient, flats: List[str]):
    body = '\n'.join(flats)
    s3.put_object(Bucket=os.getenv('BUCKET'), Key='accommodations.txt', Body=body)
    logging.info(f'Successfully wrote {len(flats)} flat ids to s3')
