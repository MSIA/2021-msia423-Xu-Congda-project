import traceback
import logging.config

import pandas as pd
import pickle
from flask import Flask
from flask import render_template, request, redirect, url_for

from src.ncaa_db import query_to_dict
from src.model import make_predict

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
from src.ncaa_db import Regular, Tourney, Teams, NCAAManager
ncaa_manager = NCAAManager(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/', methods=['POST'])
def index():
    # get user inputs
    if request.method == 'POST':
        team1 = request.form.to_dict()['TeamA']
        team2 = request.form.to_dict()['TeamB']
        season = request.form.to_dict()['Season']
        try:
            # both teams' name are given
            if team1 != '' and team2 != '':
                id1_result = ncaa_manager.session.query(Teams.TeamID).filter(Teams.TeamName == team1).all()
                id2_result = ncaa_manager.session.query(Teams.TeamID).filter(Teams.TeamName == team2).all()
                # both team name are valid
                if len(id1_result) != 0 and len(id2_result) != 0:
                    id1 = id1_result[0][0]
                    id2 = id2_result[0][0]
                    regular1_result = ncaa_manager.session.query(Regular).filter(Regular.Team == id1, Regular.Season == season).all()
                    regular2_result = ncaa_manager.session.query(Regular).filter(Regular.Team == id2, Regular.Season == season).all()
                    # both teams played in a given season
                    if len(regular1_result) != 0 and len(regular2_result) != 0:
                        regular1_df = pd.DataFrame(query_to_dict(regular1_result))
                        regular2_df = pd.DataFrame(query_to_dict(regular2_result))
                        seed1_result = ncaa_manager.session.query(Tourney.Seed).filter(Tourney.TeamID == id1, Tourney.Season == season).all()
                        seed2_result = ncaa_manager.session.query(Tourney.Seed).filter(Tourney.TeamID == id2, Tourney.Season == season).all()
                        # both teams played in the tourney
                        if len(seed1_result) != 0 and len(seed2_result) != 0:
                            seed1 = seed1_result[0][0]
                            seed2 = seed2_result[0][0]
                            delta = pd.concat([regular1_df, regular2_df])
                            delta['Seed'] = [seed1, seed2]
                            delta = delta.drop(['index', 'Season', 'Team', 'GP'], axis=1)
                            delta = delta.diff(periods=-1, axis=0).head(1)
                            with open('data/clf.sav', 'rb') as f:
                                clf = pickle.load(f)
                            predicted = make_predict(clf, delta)[0]
                            if predicted == 0:
                                winner = team2
                            else:
                                winner = team1
                            return render_template('prediction.html', predicted_winner=winner)
                        # have team not entered the tourney
                        else:
                            no_tourney = []
                            if len(seed1_result) == 0:
                                no_tourney.append(team1)
                            if len(seed2_result) == 0:
                                no_tourney.append(team2)
                            return render_template('no_tourney.html', no_tourney=no_tourney)
                    # have team not played during a given season
                    else:
                        no_season = []
                        if len(regular1_result) == 0:
                            no_season.append(team1)
                        if len(regular2_result) == 0:
                            no_season.append(team2)
                        return render_template('no_season.html', no_season=no_season)
                # have invalid team names
                else:
                    no_team = []
                    if len(id1_result) == 0:
                        no_team.append(team1)
                    if len(id2_result) == 0:
                        no_team.append(team2)
                    return render_template('no_team.html', no_team=no_team)
            # missing team name inputs
            else:
                return render_template('no_input.html')
        except:
            traceback.print_exc()
            logger.warning("Not able to show webpage, error page returned")
            return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])