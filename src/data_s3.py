import argparse
import logging
import re

import boto3
import botocore
import os

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("s3transfer").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("boto3").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("aiobotocore").setLevel(logging.ERROR)
logging.getLogger("s3fs").setLevel(logging.ERROR)


logger = logging.getLogger('s3')


def parse_s3(s3path):
    """Parse the S3 path that is passed in
       Args:
           s3path : Enter the s3 path as input
       Returns:
           str: name of S3 bucket
           str: path of S3 bucket
       """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path

def upload_file_to_s3(local_path, s3path):
    """Upload raw data from local to S3 bucket.
        Args:
            local_path: Local path for data file being uploaded
            s3path: S3 path for data file being stored
        Returns:
            None
        """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--upload', action='store_true',
                        help="If used, will load data via pandas")
    parser.add_argument('--multiple', action='store_true',
                        help="If used, will load multiple data files in a directory")
    parser.add_argument('s3path', default='s3://2021-msia423-xu-congda/data/', action='store',
                        help="Where to load data in S3")
    parser.add_argument('local_path', default='data/NCAA/', action='store',
                        help="Where to load data to in S3")
    args = parser.parse_args()

    # The case when the user want to upload a file
    if args.upload:
        # The case when the user want to upload multiple files in a directory
        if args.multiple:
            local_folder = args.local_path
            s3_folder = args.s3path
            # Local each file in the specified directory and upload them individually
            for file in os.listdir(local_folder):
                local = local_folder + file
                s3 = s3_folder + file
                upload_file_to_s3(local, s3)
        # The case when the user want to upload a single file
        else:
            upload_file_to_s3(args.local_path, args.s3path)
