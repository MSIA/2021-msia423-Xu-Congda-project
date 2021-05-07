import os
import argparse

import logging.config
logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('ncaa-pipeline')

import src.data_s3 as ds3
import src.ncaa_db as db

if __name__ == '__main__':

    # Add parsers for both uploading data to S3 bucket and creating table in database
    parser = argparse.ArgumentParser(description="Upload data to S3 bucket/Create table in dataBase")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for uploading data to S3 bucker
    sb_s3 = subparsers.add_parser("upload", description="Upload data to s3 bucket")
    sb_s3.add_argument('--multiple', action='store_true',
                        help="If used, will load multiple data files in a directory")
    sb_s3.add_argument('s3path', default='s3://2021-msia423-xu-congda/data/', action='store',
                        help="Where to load data in S3")
    sb_s3.add_argument('local_path', default='data/NCAA/', action='store',
                        help="Where to load data to in S3")

    # Sub-parser for creating table in database
    sb_create = subparsers.add_parser("create_db", description="Create table in database")
    sb_create.add_argument("--engine_string", default=None,
                              help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'upload':
        if args.multiple:
            local_folder = args.local_path
            s3_folder = args.s3path
            for file in os.listdir(local_folder):
                local = local_folder + file
                s3 = s3_folder + file
                ds3.upload_file_to_s3(local, s3)
        else:
            ds3.upload_file_to_s3(args.local_path, args.s3path)
    elif sp_used == 'create_db':
        db.create_db(args.engine_string)
    else:
        parser.print_help()



