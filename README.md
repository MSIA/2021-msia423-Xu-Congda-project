# NCAA March Madness Bracket Predictor

Developer: Congda Xu \
QA: Xingyun Gu


# Project Charter



## Vision
Each year when the NCAA Tournament comes, people get super excited about this feast of basketball. In addition to the games, an important part of March Madness is the bracket challenge, which is an activity to make predictions of the game results. Friends set up groups and compete against each other by trying to fill up a bracket with the highest accuracy. When filling up the brackets, people always find it hard to make a choice: they might be unfamiliar with the teams, or the two teams in a matchup are so close in terms of competitiveness. Therefore, I would like to develop an app that can predict the game result of a certain matchup. I hope this app can provide great assistance to people that are suffering from tough choices when filling the brackets, and provide some insights to audiences that are unfamiliar with the teams before the tournament begins.


## Mission
The app will provide the following function to the users:
The user select the two teams of a certain matchup, and the app will predict the winner of the matchup.

Regarding the data source, I would use the March Machine Learning Mania 2021 - NCAAM dataset on Kaggle. The link to the dataset is [here](https://www.kaggle.com/c/ncaam-march-mania-2021/data). 

The current data source provides a variety and sufficient amount of data, including statistics of regular season and tournament for all teams in NCAA Division I for men, ranging from 2003 to 2020. There are some data cleaning needs to be done. The dataset is separated into multiple files, and I need to link them together, filter out the data I need, and make necessary aggregations. In addition, I need to transform certain data for feature engineering.

I plan to train a binary classification model such as logistic regression or SVM. The specific model that I would used for the final app will depend on the performance of the model.


## Success Criteria
**Machine Learning Performance Metric:**

 - Accuracy: Since I am implemeting a classification model, accuracy is going to be an appropriate metric to judge the predicive power of the models. The most basic benchmark accuracy should be 50% (random guess probability), which is a bottom line that my model should surpass, and the model accuracy is definitely the higher the better.

**Business Metric**

 - % Increase of app user for each NCAA season
 - Ranking of the app-generated full-bracket score when compared with the real brackets that people fill for each NCAA tournament

# Directory Structure
```
????????? README.md                         <- You are here
????????? app
???   ????????? static/                       <- png files that remain static
???   ????????? templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
???   ????????? boot.sh                       <- Start up script for launching app in Docker container.
???   ????????? Dockerfile_app                <- Dockerfile for building image to run app  
???
????????? config                            <- Directory for configuration files 
???   ????????? logging/                      <- Configuration of python loggers
???   ????????? flaskconfig.py                <- Configurations for Flask API 
???   ????????? config.yaml                   <- Configurations for model pipeline 
???
????????? data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
???   ????????? external/                     <- External data sources, usually reference data,  will be synced with git
???   ????????? sample/                       <- Sample data used for code development and testing, will be synced with git
???   ????????? NCAA/                         <- Directory for raw data files.
???
????????? deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
???
????????? docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
???
????????? figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
???
????????? models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
???
????????? notebooks/
???   ????????? archive/                      <- Develop notebooks no longer being used.
???   ????????? deliver/                      <- Notebooks shared with others / in final state
???   ????????? develop/                      <- Current notebooks being used in development.
???
????????? references/                        <- Any reference material relevant to the project
???
????????? src/                              <- Source data for the project 
???   ????????? ncaa_db.py                    <- Python file used to create local/RDS databse.
???   ????????? data_s3.py                    <- Python file used to upload dataset to S3 bucket.
???   ????????? data_cleaning.py              <- Python file used to clean raw data.
???   ????????? model.py                      <- Python file used to run a model pipeline.
???
????????? test/                             <- Files necessary for running model tests (see documentation below) 
???   ????????? test_get_regular_season_average.py               <- Unit test code for get_regular_season_averege function
???
????????? app.py                            <- Flask wrapper for running the model 
????????? run.py                            <- Simplifies the execution of one or more of the src scripts  
????????? requirements.txt                  <- Python package dependencies 
????????? Dockerfile_db                     <- Dockerfile for creating database and ingesting data
????????? Dockerfile_model                  <- Dockerfile for running model pipeline
????????? run-db.sh                         <- Bash script for creating database and ingesting data
????????? run-model.sh                      <- Bash script for running mode pipeline
????????? .mysqlconfig                      <- Configuration file for mysql database
```

# Instructions for Running the Project
## Preparations
### 1. Acquire Dataset
The dataset is acquired from Kaggle. Please go to the website(https://www.kaggle.com/c/ncaam-march-mania-2021/data), and 
download all the files in the folder 'MDataFiles_Stage2' to your local directory. Here, my downloaded data files are in the 
/data/NCAA directory. 

### 2. Connect to NU VPN
Please connect to NU VPN first, since your IP address is important for successfully running the project.

### 3. Set Environment Variables and Credentials
You first need to add AWS credentials to environment variables. In command line type:
```bash
export AWS_ACCESS_KEY_ID=<Your AWS Access Key ID>
export AWS_SECRET_ACCESS_KEY=<Your Secret Key ID>
```
Then you need to add RDS credentials to environment variables.
If you have a complete SQLALCHEMY_DATABASE_URI, in command line type:
```bash
export SQLALCHEMY_DATABASE_URI=<YOUR_DATABASE_URL>
```
Another option is to set each database credential separately. In command line type:
```bash
export MYSQL_USER=<your username>
export MYSQL_PASSWORD=<your password>
export MYSQL_HOST="nw-msia423-congda.cadhjionyisi.us-east-1.rds.amazonaws.com"
export MYSQL_PORT="3306"
export DATABASE_NAME="msia423_db"
```
You can also set up the environment variables through editing the `.mysqlconfig` file:
```bash
vi .mysqlconfig
```
And then set the environment variables through:
```bash
source .mysqlconfig
```

## Run the Project
### 1. Upload data to S3, and create tables in RDS
First you should build a docker image. In command line terminal type the following command (you can change 'ncaa' to whatever Docker image name you want)
```bash
docker build -f Dockerfile_db -t ncaa .
```
Then you can run the docker by typing:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME --mount type=bind,source="$(pwd)",target=/app/ ncaa run-db.sh
```
Please be aware that ingesting data takes some time. 

### 2. Run model pipeline
First you should build a docker image. In command line terminal type the following command (you can change 'ncaa' to whatever Docker image name you want)
```bash
docker build -f Dockerfile_model -t ncaa .
```
Then you can run the docker by typing:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)",target=/app/ ncaa run-model.sh
```
### 3. Run app
First you should build a docker image. In command line terminal type the following command (you can change 'ncaa' to whatever Docker image name you want)
```bash
docker build -f app/Dockerfile_app -t ncaa .
```
Then you can run the docker by typing:
```bash
docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 ncaa
```
### 4. Run test
First you should build a docker image. In command line terminal type the following command (you can change 'ncaa' to whatever Docker image name you want)
```bash
docker build -f Dockerfile_python -t ncaa .
```
To run unit test, just type:
```bash
docker run ncaa -m pytest
```