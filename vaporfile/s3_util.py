from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError

import config
import credentials

__conn = None

def get_connection():
    c = config.load_config()
    global __conn
    if not __conn:
        __conn = S3Connection(c["credentials"]["access_key"],
                              c["credentials"]["secret_key"])
    return __conn

def get_bucket_names(conn):
    l=[]
    for bucket in conn.get_all_buckets():
        l.append(bucket.name)
    return l

def get_paths_from_keys(bucket):
    paths = {} #path -> key
    for key in bucket.get_all_keys():
        paths[key.name] = key
    return paths

exc = None

def test_bucket_exists(conn, bucket_name):
    try:
        bucket = conn.get_bucket(bucket_name)
        return True
    except S3ResponseError as e:
        if e.status == 404:
            return False
        elif e.status == 403:
            return True
        else:
            raise e
