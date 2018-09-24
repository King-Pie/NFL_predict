import nflgame
import utils

data_keys = ['gamekey', 'year', 'week',
             'home', 'home_w_pct', 'home_h_w_pct', 'home_prev_w_pct',
             'away', 'away_w_pct', 'away_a_w_pct', 'away_prev_w_pct',
             'div_flag', 'result']


def training_data_row(game):

    # for convenience
    year, week = game['year'], game['week']
    home, away = game['home'], game['away']

    game['home_w_pct'] = utils.team_season_win_pct(home, year, week - 1)
    try:
        game['home_h_w_pct'] = utils.team_season_win_pct(home, year, week - 1, type='home')
    except TypeError:
        game['home_h_w_pct'] = 0
    game['away_w_pct'] = utils.team_season_win_pct(away, year, week - 1)
    try:
        game['away_a_w_pct'] = utils.team_season_win_pct(away, year, week - 1, type='away')
    except TypeError:
        game['away_a_w_pct'] = 0

    game['home_prev_w_pct'] = utils.team_prev_season_win_pct(home, year, prev_seasons=1)
    game['away_prev_w_pct'] = utils.team_prev_season_win_pct(away, year, prev_seasons=1)

    game['div_flag'] = utils.divisional_flag(home, away)

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


def generate_training_data(years, verbose=False):
    import csv

    if type(years) is int:
        years = [years]

    header_line = data_keys
    if verbose:
        print header_line

    # Write to file
    for year in years:
        path = './training_data/' + str(year) + '.csv'
        with open(path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_line)
            print 'Generating training training_data for', year
            for week in range(1, 18):
                games = utils.get_week_schedule(year, week)
                for g in games:

                    row = training_data_row(g)
                    if row[-1] == 'UNK':
                        pass
                    else:
                        writer.writerow(training_data_row(g))
                    if verbose:
                        print training_data_row(g)

    print 'Finished.'


generate_training_data([2014, 2015, 2016, 2017], verbose=False)
# generate_training_data([2017], verbose=False)
