import logging

import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn import svm

import src.data_s3 as s3
import src.data_cleaning as cleaning

logger = logging.getLogger(__name__)


def acquire_data(s3_paths, local_paths):
    """Acquire raw data from S3 bucket
       Args:
           s3_paths(list): list of file names that should be downloaded from S3
           local_paths(list): list of file paths that the acquired data should be stored locally
       Returns:
           None
    """
    for i in range(len(s3_paths)):
        s3_path = s3_paths[i]
        local_path = local_paths[i]
        s3.download_file_from_s3(local_path, s3_path)
    logger.debug('Acquired raw data')


def load_data(input_paths, output_paths):
    """Load raw data and make necessary cleaning
       Args:
           input_paths(list): list of file names that should be loaded
           output_paths(list): list of file paths that the loaded and cleaned data should be stored locally
       Returns:
           tourney_delta(pd.Dataframe): loaded and cleaned data that is suitable for machine learning model
    """
    regular_avg = cleaning.get_regular_season_average(input_paths[0], output_paths[0])
    tourney_result = cleaning.get_tourney_result(input_paths[1], output_paths[1])
    tourney_seeds = cleaning.get_tourney_seeds(input_paths[2], output_paths[2])
    tourney_delta = cleaning.get_tourney_delta(regular_avg, tourney_result, tourney_seeds, output_paths[3])
    logger.debug('Loaded data')
    return tourney_delta


def featurize(data, columns):
    """Extract features from model data
       Args:
           data(pd.Dataframe): model data
           columns(list): list of feature column names
       Returns:
           features(pd.Dataframe): model features
    """
    features = data[columns]
    logger.debug('Got features')
    return features


def get_target(data, column):
    """Extract target from model data
       Args:
           data(pd.Dataframe): model data
           column(str): target column name
       Returns:
           target(pd.Series): model target
    """
    target = data[column]
    logger.debug('Got target')
    return target


def split_data(features, target, ratio, random_state):
    """Split train and test data
       Args:
           features(pd.Dataframe): model features
           target(pd.Series): model target
           ratio(float): test size ratio
           random_state(int): random seed
       Returns:
           X_train(pd.Dataframe): x variables of train data
           X_test(pd.Dataframe): x variables of test data
           y_train(pd.Series): y variables of test data
           y_test(pd.Series): y variables of test data
    """
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=ratio, random_state=random_state)
    logger.debug('Splitted data')
    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train, kernel):
    """Split train and test data
       Args:
           X_train(pd.Dataframe): x variables of train data
           y_train(pd.Series): y variables of test data
           kernel(str): kernel type of svm
       Returns:
           clf(sklearn.svm.SVC): trained svm model
    """
    clf = svm.SVC(kernel=kernel)
    clf.fit(X_train, y_train)
    logger.debug('Trained model')
    return clf


def make_predict(clf, X_test):
    """Make predictions on test data
       Args:
           clf(sklearn.svm.SVC): trained svm model
           X_test(pd.Dataframe): x variables of test data
       Returns:
           y_pred(np.ndarray): predicted values
    """
    y_pred = clf.predict(X_test)
    logger.debug('Made predictions')
    return y_pred


def evaluation(y_test, y_pred):
    """Evaluate model performance
       Args:
           y_test(pd.Series): y variables of test data
           y_pred(np.ndarray): predicted values
       Returns:
           result(pd.Dataframe): result of evaluation
    """
    accuracy = metrics.accuracy_score(y_test, y_pred)
    confusion = metrics.confusion_matrix(y_test, y_pred)
    result = pd.DataFrame(confusion,
                       index=['Actual negative', 'Actual positive'],
                       columns=['Predicted negative', 'Predicted positive'])
    print('Accuracy on test: %0.3f' % accuracy)
    print()
    print(result)
    return result