import os
import logging

import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from collections import defaultdict

logger = logging.getLogger(__name__)

Base = declarative_base()


class Regular(Base):
    __tablename__ = 'regular_season'
    index = Column(Integer, primary_key=True, autoincrement=True)
    Season = Column(Integer, unique=False, nullable=False)
    Team = Column(Integer, unique=False, nullable=False)
    Score = Column(Float, unique=False, nullable=False)
    FGM = Column(Float, unique=False, nullable=False)
    FGA = Column(Float, unique=False, nullable=False)
    FGM3 = Column(Float, unique=False, nullable=False)
    FGA3 = Column(Float, unique=False, nullable=False)
    FTM = Column(Float, unique=False, nullable=False)
    FTA = Column(Float, unique=False, nullable=False)
    OR = Column(Float, unique=False, nullable=False)
    DR = Column(Float, unique=False, nullable=False)
    Ast = Column(Float, unique=False, nullable=False)
    TO = Column(Float, unique=False, nullable=False)
    Stl = Column(Float, unique=False, nullable=False)
    Blk = Column(Float, unique=False, nullable=False)
    PF = Column(Float, unique=False, nullable=False)
    GP = Column(Integer, unique=False, nullable=False)
    FGP = Column(Float, unique=False, nullable=False)
    FG3P = Column(Float, unique=False, nullable=False)
    FTP = Column(Float, unique=False, nullable=False)

    def __repr__(self):
        return '<Regular %d>' % self.Team


class Tourney(Base):
    __tablename__ = 'tourney_seeds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Season = Column(Integer, unique=False, nullable=False)
    Seed = Column(Integer, unique=False, nullable=False)
    TeamID = Column(Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Tourney %d>' % self.TeamID


class Teams(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, autoincrement=True)
    TeamID = Column(Integer, unique=False, nullable=False)
    TeamName = Column(String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<Team_id %d>' % self.TeamID


def get_engine_string(string):
    """Transform user-typed engine string to actual engine string
        Args:
            string(str): parsed argument from run.py to specify the database path (local/RDS)
        Returns:
            string(str): actual engine string to be passed to function create_db()
    """

    DB_HOST = os.environ.get('MYSQL_HOST')
    DB_PORT = os.environ.get('MYSQL_PORT')
    DB_USER = os.environ.get('MYSQL_USER')
    DB_PW = os.environ.get('MYSQL_PASSWORD')
    DATABASE = os.environ.get('DATABASE_NAME')
    DB_DIALECT = 'mysql+pymysql'

    if string is not None:
        pass
    elif DB_HOST is None:
        string = 'sqlite:///data/ncaa.db'
    else:
        string = '{dialect}://{user}:{pw}@{host}:{port}/{db}'.format(dialect=DB_DIALECT, user=DB_USER,
                                                                                      pw=DB_PW, host=DB_HOST,
                                                                                      port=DB_PORT,
                                                                                      db=DATABASE)
    return string


def create_db(string):
    """Create the database schema(i.e.tables)
       Args:
           string(str): engine string to specify whether to create database locally or at RDS
       Returns:
           engine(sqlalchemy.engine.Engine): engine that is created
    """
    engine_string = get_engine_string(string)
    engine = sql.create_engine(engine_string)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine


def create_session(engine):
    """Create the sql session
       Args:
           engine(sqlalchemy.engine.Engine): engine that is created when creating the database
       Returns:
           session(sqlalchemy.orm.Session): session that is created based on the engine
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def ingest_regular_avg(session, regular_avg):
    """ingest the regular season average dataframe into the sql database
       Args:
           session(sqlalchemy.orm.Session): sql session
           regular_avg(pd.Dataframe): regular season average dataframe
       Returns:
           None
    """
    session.execute('''DELETE FROM regular_season''')
    lines = regular_avg.to_dict('records')
    records = []
    for line in lines:
        records.append(Regular(Season=line['Season'], Team=line['Team'], Score=line['Score'], FGM=line['FGM'],
                               FGA=line['FGA'], FGM3=line['FGM3'], FGA3=line['FGA3'], FTM=line['FTM'],
                               FTA=line['FTA'], OR=line['OR'], DR=line['DR'], Ast=line['Ast'], TO=line['TO'], Stl=line['Stl'],
                               Blk=line['Blk'], PF=line['PF'], GP=line['GP'], FGP=line['FGP'], FG3P=line['FG3P'], FTP=line['FTP']))
    session.add_all(records)
    session.commit()
    logger.info(f'{len(records)} records were added to the table')


def ingest_tourney_seeds(session, seeds):
    """ingest the tourney seeds dataframe into the sql database
       Args:
           session(sqlalchemy.orm.Session): sql session
           seeds(pd.Dataframe): tourney seeds dataframe
       Returns:
           None
    """
    session.execute('''DELETE FROM tourney_seeds''')
    lines = seeds.to_dict('records')
    records = []
    for line in lines:
        records.append(Tourney(Season=line['Season'], Seed=line['Seed'], TeamID=line['TeamID']))
    session.add_all(records)
    session.commit()
    logger.info(f'{len(records)} records were added to the table')


def ingest_teams(session, teams):
    """ingest the teams dataframe into the sql database
       Args:
           session(sqlalchemy.orm.Session): sql session
           teams(pd.Dataframe): teams dataframe
       Returns:
           None
    """
    session.execute('''DELETE FROM teams''')
    lines = teams.to_dict('records')
    records = []
    for line in lines:
        records.append(Teams(TeamID=line['TeamID'], TeamName=line['TeamName']))
    session.add_all(records)
    session.commit()
    logger.info(f'{len(records)} records were added to the table')


def query_to_dict(rset):
    """Transform the sql query result into a dictionary
       Args:
           rset(list): sql query result
       Returns:
           result(dict): transformed dictionary type sql query result
    """
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


class NCAAManager:

    def __init__(self, app=None, engine_string=None):
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sql.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Please provide an engine string or a Flask app to initialize")

        def close(self):
            self.session.close()