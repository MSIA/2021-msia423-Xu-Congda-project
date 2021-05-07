import os
import logging
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData



def get_engine_string(string):

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
    engine_string = get_engine_string(string)

    engine = sql.create_engine(engine_string)

    Base = declarative_base()

    class Regular(Base):
        __tablename__ = 'regular_season'
        id = Column(Integer, primary_key=True)
        team_id = Column(Integer, unique=False, nullable=False)
        team = Column(String(100), unique=False, nullable=False)
        season = Column(Integer, unique=False, nullable=False)
        date = Column(Integer, unique=False, nullable=False)
        score = Column(Integer, unique=False, nullable=False)
        offensive_rebound = Column(Integer, unique=False, nullable=False)
        defensive_rebound = Column(Integer, unique=False, nullable=False)
        assist = Column(Integer, unique=False, nullable=False)
        fg_made = Column(Integer, unique=False, nullable=False)
        fg_attempted = Column(Integer, unique=False, nullable=False)
        three_made = Column(Integer, unique=False, nullable=False)
        three_attempted = Column(Integer, unique=False, nullable=False)
        ft_made = Column(Integer, unique=False, nullable=False)
        ft_attempted = Column(Integer, unique=False, nullable=False)
        turnover = Column(Integer, unique=False, nullable=False)
        steal = Column(Integer, unique=False, nullable=False)
        block = Column(Integer, unique=False, nullable=False)
        win = Column(Integer, unique=False, nullable=False)

        def __repr__(self):
            return '<Regular %r>' % self.team_id

    class Tournament(Base):
        __tablename__ = 'tournament'
        id = Column(Integer, primary_key=True)
        team_id = Column(Integer, unique=False, nullable=False)
        team = Column(String(100), unique=False, nullable=False)
        season = Column(Integer, unique=False, nullable=False)
        date = Column(Integer, unique=False, nullable=False)
        score = Column(Integer, unique=False, nullable=False)
        offensive_rebound = Column(Integer, unique=False, nullable=False)
        defensive_rebound = Column(Integer, unique=False, nullable=False)
        assist = Column(Integer, unique=False, nullable=False)
        fg_made = Column(Integer, unique=False, nullable=False)
        fg_attempted = Column(Integer, unique=False, nullable=False)
        three_made = Column(Integer, unique=False, nullable=False)
        three_attempted = Column(Integer, unique=False, nullable=False)
        ft_made = Column(Integer, unique=False, nullable=False)
        ft_attempted = Column(Integer, unique=False, nullable=False)
        turnover = Column(Integer, unique=False, nullable=False)
        steal = Column(Integer, unique=False, nullable=False)
        block = Column(Integer, unique=False, nullable=False)
        win = Column(Integer, unique=False, nullable=False)

        def __repr__(self):
            return '<Tournament %r>' % self.team_id

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()
    session.close()
