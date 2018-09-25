import utils
import nflgame
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn import preprocessing
import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.options.display.max_rows = 999

data_path = r'./training_data/'

# Evaluation set
# Training set
years = ['2010', '2011', '2012', '2013', '2014', '2015']
all_files = [data_path + str(year) + '_database.csv' for year in years]
train_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

# Testing set
years = ['2016', '2017']
all_files = [data_path + str(year) + '_database.csv' for year in years]
test_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

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
    'div_flag',
    'matchup_weight',
    'home_season_pt_dif',
    'home_3game_pt_dif',
    'home_5game_pt_dif',
    'home_prev_season_pt_dif',
    'away_season_pt_dif',
    'away_3game_pt_dif',
    'away_5game_pt_dif',
    'away_prev_season_pt_dif'
                 ]

X_train = train_df[feature_names]
Y_train = train_df['result']

X_test = test_df[feature_names]
Y_test = test_df['result']


def svc_param_selection(X, y, nfolds):
    from sklearn import svm

    GridSearchCV = sklearn.model_selection.GridSearchCV
    Cs = [0.001, 0.01, 0.1, 1, 10]
    gammas = [0.001, 0.01, 0.1, 1]
    param_grid = {'C': Cs, 'gamma': gammas}
    grid_search = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=nfolds)
    grid_search.fit(X, y)
    return grid_search.best_params_


print '---------'
params = svc_param_selection(X_train, Y_train, 3)
svm = SVC(C=params['C'], gamma=params['gamma'])
svm.fit(X_train, Y_train)
print('Accuracy of SVM classifier on training set: {:.2f}'
      .format(svm.score(X_train, Y_train)))
print('Accuracy of SVM classifier on test set: {:.2f}'
      .format(svm.score(X_test, Y_test)))

# Making predictions

# Prediction set
# Training set
# years = ['2014', '2015', '2016']
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
all_files = [data_path + str(year) + '_database.csv' for year in years]
train_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)

X_train = train_df[feature_names]
Y_train = train_df['result']

params = svc_param_selection(X_train, Y_train, 3)
model = SVC(probability=True, C=params['C'], gamma=params['gamma'])
model.fit(X_train, Y_train)

print 'Predictions'
print('Accuracy of SVM classifier on training set: {:.2f}'
      .format(svm.score(X_train, Y_train)))

year, week = 2018, 2
games = utils.get_week_schedule(year, week)

data_display_list = []

correct_counter = 0
for game in games:
    data_dictionary = {}
    home, away = game['home'], game['away']

    data_dictionary['week'] = week
    data_dictionary['home'], data_dictionary['away'] = home, away

    data_dictionary['home_wpct'], data_dictionary['away_wpct'] = \
        [utils.team_season_win_pct(team, year, week - 1) for team in [home, away]]
    data_dictionary['home_h_wpct'] = utils.team_season_win_pct(home, year, week - 1, type='home')
    data_dictionary['away_a_wpct'] = utils.team_season_win_pct(away, year, week - 1, type='away')
    data_dictionary['div_flag'] = utils.divisional_flag(home, away)

    data_dictionary['home_prev_wpct'] = utils.team_prev_season_win_pct(home, year, prev_seasons=1)
    data_dictionary['away_prev_wpct'] = utils.team_prev_season_win_pct(away, year, prev_seasons=1)

    data_dictionary['home_prev_h_wpct'] = \
        utils.team_prev_season_win_pct(home, year, prev_seasons=1, type='home')
    data_dictionary['away_prev_a_wpct'] = \
        utils.team_prev_season_win_pct(away, year, prev_seasons=1, type='away')

    data_dictionary['matchup_weight'] = utils.matchup_weight(game)

    home_season_pt_dif, home_3game_pt_dif, home_5game_pt_dif = \
        utils.team_pt_dif_per_n_games(home, year, week)
    data_dictionary['home_season_pt_dif'] = home_season_pt_dif
    data_dictionary['home_3game_pt_dif'] = home_3game_pt_dif
    data_dictionary['home_5game_pt_dif'] = home_5game_pt_dif
    data_dictionary['home_prev_season_pt_dif'] = utils.team_pt_dif_per_game_season(home, year - 1)

    away_season_pt_dif, away_3game_pt_dif, away_5game_pt_dif = \
        utils.team_pt_dif_per_n_games(away, year, week)
    data_dictionary['away_season_pt_dif'] = away_season_pt_dif
    data_dictionary['away_3game_pt_dif'] = away_3game_pt_dif
    data_dictionary['away_5game_pt_dif'] = away_5game_pt_dif
    data_dictionary['away_prev_season_pt_dif'] = utils.team_pt_dif_per_game_season(away, year - 1)

    features = []
    for f in feature_names:
        features.append(data_dictionary[f])

    features = [data_dictionary[f] for f in feature_names]

    data_display_list.append(['{} AT {}'.format(away, home)] + features)

    prediction = model.predict([features])[0]
    prediction_prob = model.predict_proba([features])[0]

    prediction_outcome_dict = {'win': home, 'tie': 'tie', 'loss': away}
    predicted_winner = prediction_outcome_dict[prediction]
    prediction_pct = '(' + str(round(max(prediction_prob)*100, 2)) + '%)'

    try:
        actual_game = nflgame.one(year, week, home, away)
        actual_winner = actual_game.winner
        if actual_winner is None:
            actual_winner = 'UNKNOWN'
    except AttributeError:
        actual_winner = 'UNKNOWN'

    if predicted_winner == actual_winner:
        prediction_success = 'CORRECT'
        correct_counter += 1
    else:
        prediction_success = 'WRONG'

    print '{} AT {}   pred winner: {} {}    actual winner: {}    {}'.format(
        away, home, predicted_winner, prediction_pct, actual_winner, prediction_success)

print str(correct_counter) + '/' + str(len(games)), '({0:.1f})%'.format(float(correct_counter)/len(games)*100)

df = pd.DataFrame(data_display_list, columns=['teams'] + feature_names)
print df
