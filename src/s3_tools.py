import json
import os
import logging
from botocore import client
from typing import List, Dict


def check_s3(s3: client.BaseClient):
    bucket = os.getenv('BUCKET')
    if bucket is None or len(bucket) == 0:
        raise ValueError('System variable `BUCKET` is empty!')
    bucket_names = {x['Name'] for x in s3.list_buckets(Bucket=bucket)['Buckets']}
    if bucket not in bucket_names:
        raise ValueError(f'Bucket {bucket} does not exist!')
    logging.info('s3 configuration is OK')


def load_flats(s3: client.BaseClient) -> Dict[str, List[str]]:
    resp = s3.get_object(Bucket=os.getenv('BUCKET'), Key='accommodations.json')
    flat_ids = json.loads(resp['Body'].read())
    logging.info(f'Successfully read flat ids from s3')
    return flat_ids


def write_flats(s3: client.BaseClient, flats: Dict[str, List[str]]):
    body = json.dumps(flats)
    s3.put_object(Bucket=os.getenv('BUCKET'), Key='accommodations.json', Body=body)
    logging.info(f'Successfully wrote flat ids to s3')
