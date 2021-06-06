import logging
import re

import boto3
import botocore

logger = logging.getLogger(__name__)


def parse_s3(s3path):
    """Parse the S3 path that is passed in
       Args:
           s3path(str): Enter the s3 path as input
       Returns:
           s3bucket(str): name of S3 bucket
           s3path(str): path of S3 bucket
    """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path, s3path):
    """Upload raw data from local to S3 bucket
        Args:
            local_path(str): Local path for data file being uploaded
            s3path(str): S3 path for data file being stored
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


def download_file_from_s3(local_path, s3path):
    """Download data from S3 bucket to local
        Args:
            local_path(str): Local path for downloaded data to be stored
            s3path(str): S3 path for data file to be downloaded
        Returns:
            None
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.download_file(s3_just_path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3path, local_path)