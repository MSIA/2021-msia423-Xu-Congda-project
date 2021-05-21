# NCAA March Madness Bracket Predictor

Developer: Congda Xu \
QA: Xingyun Gu


# Project Charter



## Vision
Each year when the NCAA Tournament comes, people get super excited about this feast of basketball. In addition to the games, an important part of March Madness is the bracket challenge, which is an activity to make predictions of the game results. Friends set up groups and compete against each other by trying to fill up a bracket with the highest accuracy. When filling up the brackets, people always find it hard to make a choice: they might be unfamiliar with the teams, or the two teams in a matchup are so close in terms of competitiveness. Therefore, I would like to develop an app that can predict the how far a team can proceed in the tournament (e.g., Sweet Sixteen, Elite Eight, Final Four), and the game result of a certain matchup. I hope this app can provide great assistance to people that are suffering from tough choices when filling the brackets, and provide some insights to audiences that are unfamiliar with the teams before the tournament begins.


## Mission
The app will offer two options to the users:
Option #1: The user selects a team, and the app returns the predicted performance of the team in this year's NCAA Tournament (e.g., Sweet Sixteen, Elite Eight, Final Four).
Option #2: The user select the two teams of a certain matchup, and the app will predict the winner of the matchup.

Regarding the data source, I would use the March Machine Learning Mania 2021 - NCAAM dataset on Kaggle. The link to the dataset is [here](https://www.kaggle.com/c/ncaam-march-mania-2021/data). 

The current data source provides a variety and sufficient amount of data, including statistics of regular season and tournament for all teams in NCAA Division I for men, ranging from 2003 to 2020. There are some data cleaning needs to be done. The dataset is separated into multiple files, and I need to link them together, filter out the data I need, and make necessary aggregations. In addition, I need to transform certain data for feature engineering.

To enable the first option, I plan to train a multi-class classification model such as KNN. To enable the second option, I plan to train a binary classification model such as logistic regression or SVM or Neural Network. The specific model that I would used for the final app will depend on the performance of the model.


## Success Criteria
**Machine Learning Performance Metric:**

 - Accuracy: Since I am implemeting two classification models, accuracy is going to be an appropriate metric to judge the predicive power of the models. The most basic benchmark accuracy should be 50% (random guess probability), which is a bottom line that my model should surpass, and the model accuracy is definitely the higher the better.

**Business Metric**

 - % Increase of app user for each NCAA season
 - Ranking of the app-generated full-bracket score when compared with the real brackets that people fill for each NCAA tournament

# Directory Structure
```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│   ├── NCAA/                         <- Directory for raw data files.
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│   ├── ncaa_db.py                    <- Python file used to create local/RDS databse.
│   ├── data_s3.py                    <- Python file used to upload dataset to S3 bucket.
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
├── Dockerfile                        <- Dockerfile for building image in docker
├── .mysqlconfig                      <- Configuration file for mysql database
```

# How to Run Code For Mid-Project

### 1. Acquire dataset
The dataset is acquired from Kaggle. Please go to the website(https://www.kaggle.com/c/ncaam-march-mania-2021/data), and 
download all the files in the folder 'MDataFiles_Stage2' to your local directory. Here, my downloaded data files are in the 
/data/NCAA directory.

### 2. Build Docker image
In command line terminal type the following command (you can change 'ncaa' to whatever Docker image name you want)
```bash
docker build -t ncaa .
```

### 3. Upload raw data to S3 bucket

#### 3.1 Set up configurations for S3 bucket
In command line, add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to environment variables:
```bash
export AWS_ACCESS_KEY_ID=<Your AWS Access Key ID>
export AWS_SECRET_ACCESS_KEY=<Your Secret Key ID>
```

#### 3.2 Upload data from local to S3
If you would like to upload all the files in a directory:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY ncaa run.py upload --multiple <s3 directory path> <local data directory path>
```
For example:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY ncaa run.py upload --multiple s3://2021-msia423-xu-congda/data/ data/NCAA/
```
Please be aware that for both paths, they should end with '/'.


If you would like to upload only one file:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY ncaa run.py upload <s3 file path> <local data file path>
```
For example:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY ncaa run.py upload s3://2021-msia423-xu-congda/data/Cities.csv data/NCAA/Cities.csv
```

### 4. Create database scheme(i.e. tables) in MySQL database
#### Option 1: Create database schema in RDS
You should first connect to NU's VPN. 
To set environment variables, ou can EITHER
```bash
export MYSQL_USER=<your username>
export MYSQL_PASSWORD=<your password>
export MYSQL_HOST="nw-msia423-congda.cadhjionyisi.us-east-1.rds.amazonaws.com"
export MYSQL_PORT="3306"
export DATABASE_NAME="msia423_db"
```
OR set up the environment variables through editing the `.mysqlconfig` file:
```bash
vi .mysqlconfig
```
And then set the environment variables through:
```bash
source .mysqlconfig
```
After setting up the environment variables, you can create schema in RDS by:
```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME ncaa run.py create_db
```

#### Option 2: Create database and set schema locally in sqlite
By default a local database will be set up at `data/ncaa.db` by :
```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME ncaa run.py create_db 
```
If you want to specify the location where the local database will be set up:
```bash
docker run -e MYSQL_USER -e MYSQL_PASSWORD -e MYSQL_HOST -e MYSQL_PORT -e DATABASE_NAME ncaa run.py create_db --engine_string=<your database URI>
```
Be aware that the local database URI should be in the format of `sqlite:///<directory>/<table_name>.db`.




