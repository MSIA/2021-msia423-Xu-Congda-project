python3 run.py model acquire
python3 run.py model load --output 'data/model_data.csv'
python3 run.py model featurize --input 'data/model_data.csv' --output 'data/features.csv'
python3 run.py model target --input 'data/model_data.csv' --output 'data/target.pkl'
python3 run.py model split --input 'data/features.csv' 'data/target.pkl' --output 'data/X_train.csv' 'data/X_test.csv' 'data/y_train.pkl' 'data/y_test.pkl'
python3 run.py model train --input 'data/X_train.csv' 'data/y_train.pkl' --output 'data/clf.sav'
python3 run.py model predict --input 'data/clf.sav' 'data/X_test.csv' --output 'data/y_pred.npy'
python3 run.py model evaluate --input 'data/y_test.pkl' 'data/y_pred.npy'