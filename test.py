import nflgame
import utils
import pandas as pd

pd.set_option('display.expand_frame_repr', False)

data_keys = ['gamekey', 'year', 'week', 'home', 'home_w_pct', 'home_h_win_pct',
             'away', 'away_w_pct', 'away_a_win_pct', 'div_flag', 'result']


def training_data_row(game):

    # for convenience
    year, week = game['year'], game['week']
    home, away = game['home'], game['away']

    game['home_w_pct'] = utils.team_season_win_pct(home, year, week - 1)
    try:
        game['home_h_win_pct'] = utils.team_season_win_pct(home, year, week - 1, type='home')
    except TypeError:
        game['home_h_win_pct'] = 0
    game['away_w_pct'] = utils.team_season_win_pct(away, year, week - 1)
    try:
        game['away_a_win_pct'] = utils.team_season_win_pct(away, year, week - 1, type='away')
    except TypeError:
        game['away_a_win_pct'] = 0
    game['div_flag'] = utils.divisional_flag(home, away)

    game['home_prev_3_win_pct'] = utils.team_prev_season_win_pct(home, year, prev_seasons=1)
    game['away_prev_3_win_pct'] = utils.team_prev_season_win_pct(away, year, prev_seasons=1)

    try:
        winner = nflgame.one(year, week, home, away).winner
        if winner == home:
            result = 'win'
        elif winner == home + '/' + away:
            result = 'tie'
        else:
            result = 'loss'
    except AttributeError:
        winner = 'NA'
        result = 'UNK'

    game['result'] = result
    return [game[x] for x in data_keys]


year, week = 2015, 17
games = utils.get_week_schedule(year, week)
data = [data_keys]
for g in games:
    data.append(training_data_row(g))

df = pd.DataFrame(data)
print df
