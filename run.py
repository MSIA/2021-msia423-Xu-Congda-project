import os
import argparse
import logging.config

import yaml
import pickle
import pandas as pd
import numpy as np

import src.data_s3 as ds3
import src.ncaa_db as db
import src.data_cleaning as cleaning
import src.model as model

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('ncaa-pipeline')

if __name__ == '__main__':

    # Add parsers for both uploading data to S3 bucket and creating table in database
    parser = argparse.ArgumentParser(description="Upload data to S3 bucket/Create table in dataBase")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for uploading data to S3 bucket
    sb_s3_upload = subparsers.add_parser("upload", description="Upload data to s3 bucket")
    sb_s3_upload.add_argument('--multiple', action='store_true', help="If used, will load multiple data files in a directory")
    sb_s3_upload.add_argument('s3path', default='s3://2021-msia423-xu-congda/data/', action='store', help="Where to load data in S3")
    sb_s3_upload.add_argument('local_path', default='data/NCAA/', action='store', help="Where to upload data locally")

    # Sub-parser for downloading data from S3 bucket
    sb_s3_download = subparsers.add_parser("download", description="Download data from s3 bucket")
    sb_s3_download.add_argument('s3path', default=None, action='store', help="Where to download data in S3")
    sb_s3_download.add_argument('local_path', default=None, action='store', help="Where to store data locally")

    # Sub-parser for creating table in database
    sb_create = subparsers.add_parser("create_db", description="Create table in database")
    sb_create.add_argument("--engine_string", default=None, help="SQLAlchemy connection URI for database")

    # Sub-parser for running model pipeline
    sb_model = subparsers.add_parser("model", description="Run the model pipeline")
    sb_model.add_argument('step', help='Which step to run', choices=['acquire', 'load', 'featurize', 'target', 'split', 'train', 'predict', 'evaluate'])
    sb_model.add_argument('--input', '-i', nargs='+', default=None, help='Path to input data')
    sb_model.add_argument('--output', '-o', nargs='+', default=None, help='Path to save output CSV (optional, default = None)')

    args = parser.parse_args()
    sp_used = args.subparser_name

    # load configuration file
    with open('config/config.yaml', "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Configuration file loaded")

    # The option of uploading raw data to S3
    if sp_used == 'upload':
        # User chooses to upload multiple files in a directory
        if args.multiple:
            local_folder = args.local_path
            s3_folder = args.s3path
            for file in os.listdir(local_folder):
                local = local_folder + file
                s3 = s3_folder + file
                ds3.upload_file_to_s3(local, s3)
        # User chooses to upload a single file
        else:
            ds3.upload_file_to_s3(args.local_path, args.s3path)
    elif sp_used == 'download':
        ds3.download_file_from_s3(args.local_path, args.s3path)
    # The option of creating database
    elif sp_used == 'create_db':
        engine = db.create_db(args.engine_string)
        session = db.create_session(engine)
        logger.debug('Database created')
        regular_avg = cleaning.get_regular_season_average('data/MRegularSeasonDetailedResults.csv',
                                                          'data/regular_avg.csv')
        db.ingest_regular_avg(session, regular_avg)
        logger.debug('Table regular_season ingested with data')
        seeds = cleaning.get_tourney_seeds('data/MNCAATourneySeeds.csv',
                                           'data/tourney_seeds.csv')
        db.ingest_tourney_seeds(session, seeds)
        logger.debug('Table tourney_seeds ingested with data')
        teams = cleaning.get_teams('data/MTeams.csv', 'data/teams.csv')
        db.ingest_teams(session, teams)
        logger.debug('Table teams ingested with data')
        session.close()
    # The option of running model pipeline
    elif sp_used == 'model':
        # Deal with input
        if args.input is not None:
            # case when there is only one input path
            if len(args.input) == 1:
                # load a csv file into a pandas dataframe
                input = pd.read_csv(args.input[0])
                logger.info('Input data loaded from %s', args.input)
            # case when there are multiple input paths
            else:
                inputs = []
                for i in args.input:
                    # load a csv file into a pandas dataframe
                    if i.endswith('.csv'):
                        input = pd.read_csv(i)
                    # load a sav file into a ML model
                    elif i.endswith('.sav'):
                        with open(i, 'rb') as f:
                            input = pickle.load(f)
                    # load a pkl file into a pandas series
                    elif i.endswith('.pkl'):
                        input = pd.read_pickle(i)
                    # load a npy file into a numpy ndarray
                    elif i.endswith('.npy'):
                        with open(i, 'rb') as f:
                            input = np.load(f)
                    logger.info('Input data loaded from %s', i)
                    inputs.append(input)
        if args.step == 'acquire':
            model.acquire_data(**config['model']['acquire_data'])
        elif args.step == 'load':
            output = model.load_data(**config['model']['load_data'])
        elif args.step == 'featurize':
            output = model.featurize(input, **config['model']['featurize'])
        elif args.step == 'target':
            output = model.get_target(input, **config['model']['get_target'])
        elif args.step == 'split':
            output1, output2, output3, output4 = model.split_data(inputs[0], inputs[1], **config['model']['split_data'])
            output = [output1, output2, output3, output4]
        elif args.step == 'train':
            output = model.train_model(inputs[0], inputs[1], **config['model']['train_model'])
        elif args.step == 'predict':
            output = model.make_predict(inputs[0], inputs[1])
        elif args.step == 'evaluate':
            model.evaluation(inputs[0], inputs[1])
        # save artifacts to specified output path
        if args.output is not None:
            # case when there is only one output path
            if len(args.output) == 1:
                # save a pandas dataframe to a csv file
                if type(output) == pd.core.frame.DataFrame:
                    output.to_csv(args.output[0], index=False)
                # save a pandas series to a pkl file
                elif type(output) == pd.core.series.Series:
                    output.to_pickle(args.output[0])
                # save a ML model to a sav file
                else:
                    with open(args.output[0], 'wb') as f:
                        pickle.dump(output, f)
                logger.info("Output saved to %s" % args.output[0])
            # case where there are multiple output paths
            else:
                for i in range(len(output)):
                    # save a pandas dataframe to a csv file
                    if type(output[i]) == pd.core.frame.DataFrame:
                        output[i].to_csv(args.output[i], index=False)
                    # save a pandas series to a pkl file
                    elif type(output[i]) == pd.core.series.Series:
                        output[i].to_pickle(args.output[i])
                    # save a numpy ndarray to a npy file
                    else:
                        with open(args.output[i], 'wb') as f:
                            np.save(f, output[i])
                    logger.info("Output saved to %s" % args.output[i])
    # The situation where user typed incorrect option
    else:
        parser.print_help()