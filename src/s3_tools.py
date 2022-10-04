import json
import os
import logging
from typing import List, Dict
from google.cloud.storage.client import Client, Bucket


def check_s3(gs: Client) -> Bucket:
    bucket = os.getenv('BUCKET')
    if bucket is None or len(bucket) == 0:
        raise ValueError('System variable `BUCKET` is empty!')
    bucket_names = {x.name for x in gs.list_buckets()}
    if bucket not in bucket_names:
        raise ValueError(f'Bucket {bucket} does not exist!')
    logging.info('GS configuration is OK')
    return gs.bucket(bucket)


def load_flats(gs: Bucket) -> Dict[str, List[int]]:
    blob = gs.blob('accommodations.json')
    body = blob.download_as_string()
    flat_ids = json.loads(body)
    logging.info(f'Successfully read flat ids from storage')
    return flat_ids


def write_flats(gs: Bucket, flats: Dict[str, List[int]]):
    body = json.dumps(flats)
    blob = gs.blob('accommodations.json')
    blob.upload_from_string(data=body)
    logging.info(f'Successfully wrote flat ids to storage')
