import utils
import nflgame
import sklearn
import numpy as np
from sklearn.svm import SVC

import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.options.display.max_rows = 999

data_path = r'./data/training_data/'

feature_names = [
    'week',
    'home_wpct',
    'home_h_wpct',
    'home_prev_wpct',
    'home_prev_h_wpct',
    'away_wpct',
    'away_a_wpct',
    'away_prev_wpct',
    'away_prev_a_wpct',
    # 'div_flag',
    'matchup_weight',
    'home_season_pt_dif',
    'home_3game_pt_dif',
    'home_5game_pt_dif',
    'home_prev_season_pt_dif',
    'away_season_pt_dif',
    'away_3game_pt_dif',
    'away_5game_pt_dif',
    'away_prev_season_pt_dif',
    'home_season_turnovers',
    'home_3game_turnovers',
    'home_5game_turnovers',
    'home_prev_season_turnovers',
    'home_season_turnover_dif',
    'home_3game_turnover_dif',
    'home_5game_turnover_dif',
    'home_prev_season_turnover_dif',
    'away_season_turnovers',
    'away_3game_turnovers',
    'away_5game_turnovers',
    'away_prev_season_turnovers',
    'away_season_turnover_dif',
    'away_3game_turnover_dif',
    'away_5game_turnover_dif',
    'away_prev_season_turnover_dif',
    'home_season_3down_pct',
    'home_3game_3down_pct',
    'home_5game_3down_pct',
    'away_season_3down_pct',
    'away_3game_3down_pct',
    'away_5game_3down_pct'
                 ]


def svc_param_selection(X, y, nfolds):
    from sklearn import svm

    GridSearchCV = sklearn.model_selection.GridSearchCV
    Cs = [0.001, 0.01, 0.1, 1, 10]
    gammas = [0.001, 0.01, 0.1, 1]
    param_grid = {'C': Cs, 'gamma': gammas}
    grid_search = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=nfolds)
    grid_search.fit(X, y)
    return grid_search.best_params_


# Training model
print 'Training model'
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
all_files = [data_path + str(year) + '_database.csv' for year in years]
train_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
train_df = utils.scrub_data(train_df)

X_train = train_df[feature_names]
Y_train = train_df['result']

params = svc_param_selection(X_train, Y_train, 2)
model = SVC(probability=True, C=params['C'], gamma=params['gamma'])
# model = SVC(probability=True)
model.fit(X_train, Y_train)

print('Accuracy of SVM classifier on training set: {:.2f}'
      .format(model.score(X_train, Y_train)*100))

year, week = 2018, 5

prediction_data_path = r'./data/prediction_data/{}/week_{}_database.csv'.format(year, week)
prediction_df = pd.read_csv(prediction_data_path)
prediction_data = prediction_df[feature_names]
predictions = model.predict(prediction_data)
prediction_prob = model.predict_proba(prediction_data)

game_array = np.array(prediction_df[['away', 'home', 'result']])

success_counter = 0
game_count = len(prediction_df.index)
for g in range(game_count):
    away, home, result = game_array[g]
    pred = predictions[g]
    prob = round(max(prediction_prob[g])*100, 2)

    if pred == 'win':
        pred_winner = home
    else:
        pred_winner = away

    if result == 'win':
        actual_winner = home
    elif result == 'tie':
        actual_winner = 'tie'
    else:
        actual_winner = away

    if pred_winner == actual_winner:
        success = 'Correct'
        success_counter += 1
    else:
        success = 'Wrong'

    print '{} @ {}   Predicted winner: {} ({}%)   Winner: {}   {}'\
        .format(away, home, pred_winner, prob, actual_winner, success)

correct_percentage = round((float(success_counter)/game_count)*100, 2)
print '{}/{} {}%'.format(success_counter, game_count, correct_percentage)
