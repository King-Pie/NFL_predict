import nflgame
import utils
import pandas as pd
import csv

pd.set_option('display.expand_frame_repr', False)
pd.options.display.max_rows = 999


training_year_list = range(2010, 2018)


def data_generator(stat_func, year, set_name, weeks=None):

    if weeks is None:
        week_list = range(1, 18)
    else:
        week_list = weeks

    path = './data/training_data/' + str(year) + '/' + str(set_name) + '.csv'
    games = []
    for week in week_list:
        for g in utils.get_week_schedule(year, week):
            games.append(g)

    data = stat_func(games)

    with open(path, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for line in data:
            writer.writerow(line)


def current_record_stats(games):

    header = ['away_record', 'away_wpct', 'away_a_wpct',
              'home_record', 'home_wpct', 'home_h_wpct', 'result']

    data = []
    data.append(header)

    week_dummy = 0      # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            print 'Generating current record stats {} week {}'.format(year, week)
        week_dummy = week

        # home record
        hw, hl, ht = utils.team_record(home, year, week - 1)
        game['home_record'] = '{}-{}-{}'.format(hw, hl, ht)

        # away record
        aw, al, at = utils.team_record(away, year, week - 1)
        game['away_record'] = '{}-{}-{}'.format(aw, al, at)

        game['home_wpct'] = utils.team_season_win_pct(home, year, week - 1)
        game['home_h_wpct'] = utils.team_season_win_pct(home, year, week - 1, type='home')

        game['away_wpct'] = utils.team_season_win_pct(away, year, week - 1)
        game['away_a_wpct'] = utils.team_season_win_pct(away, year, week - 1, type='away')

        result_dictionary = {home: 'win', home + '/' + away: 'tie', away: 'loss'}

        try:
            winner = nflgame.one(year, week, home, away).winner
            result = result_dictionary[winner]
        except AttributeError:
            result = 'UNK'

        game['result'] = result

        row = [game[h] for h in header]
        data.append(row)

    return data


def schedule_stats(games):
    """
    Generates basic stats about the game which don't change throughout the season
    :param game:
    :return:
    """
    header = ['gamekey', 'year', 'week',
              'away', 'away_prev_wpct', 'away_prev_a_wpct',
              'home', 'home_prev_wpct', 'home_prev_h_wpct',
              'div_flag']

    data = []
    data.append(header)

    week_dummy = 0  # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            print 'Generating schedule stats for {} week {}'.format(year, week)
        week_dummy = week

        game['home_prev_wpct'] = utils.team_prev_season_win_pct(home, year, prev_seasons=1)
        game['home_prev_h_wpct'] = utils.team_prev_season_win_pct(home, year, prev_seasons=1,
                                                                  type='home')
        game['away_prev_wpct'] = utils.team_prev_season_win_pct(away, year, prev_seasons=1)
        game['away_prev_a_wpct'] = utils.team_prev_season_win_pct(away, year, prev_seasons=1,
                                                                  type='away')

        game['div_flag'] = utils.divisional_flag(home, away)

        row = [game[h] for h in header]
        data.append(row)

    return data


def matchup_stats(games):

    header = ['matchup_weight']

    data_dict = {}
    data = []
    data.append(header)

    week_dummy = 0  # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print 'Generating matchup stats for {} week {}'.format(year, week)
        week_dummy = week

        data_dict['matchup_weight'] = utils.matchup_weight(game)
        row = [data_dict[h] for h in header]
        data.append(row)

    return data


def point_differential_stats(games):

    data_dict = {}
    data = []
    header = ['home_season_pt_dif', 'home_3game_pt_dif', 'home_5game_pt_dif', 'home_prev_season_pt_dif',
              'away_season_pt_dif', 'away_3game_pt_dif', 'away_5game_pt_dif', 'away_prev_season_pt_dif']
    data.append(header)

    week_dummy = 0
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print home, away

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print 'Generating matchup stats for {} week {}'.format(year, week)
        week_dummy = week

        home_season_pt_dif, home_3game_pt_dif, home_5game_pt_dif = \
            utils.team_pt_dif_per_n_games(home, year, week)
        data_dict['home_season_pt_dif'] = home_season_pt_dif
        data_dict['home_3game_pt_dif'] = home_3game_pt_dif
        data_dict['home_5game_pt_dif'] = home_5game_pt_dif
        data_dict['home_prev_season_pt_dif'] = utils.team_pt_dif_per_game_season(home, year-1)

        away_season_pt_dif, away_3game_pt_dif, away_5game_pt_dif = \
            utils.team_pt_dif_per_n_games(away, year, week)
        data_dict['away_season_pt_dif'] = away_season_pt_dif
        data_dict['away_3game_pt_dif'] = away_3game_pt_dif
        data_dict['away_5game_pt_dif'] = away_5game_pt_dif
        data_dict['away_prev_season_pt_dif'] = utils.team_pt_dif_per_game_season(away, year-1)

        row = [data_dict[h] for h in header]
        data.append(row)

    return data


def combine_data(year):
    import glob

    print 'Combing data for {}'.format(year)

    directory_path = './training_data/' + str(year) + '/'

    all_files = glob.glob(directory_path + '*.csv')
    df = pd.concat((pd.read_csv(file) for file in all_files),
                   axis=1, sort=False)
    df.to_csv('./data/training_data/' + str(year) + '_database.csv', index=False)


if __name__ == "__main__":

    years = training_year_list
    print years
    for year in years:
        print 'Data generation for {}'.format(year)
        # data_generator(schedule_stats, year, '1_schedule_stats')
        # data_generator(current_record_stats, year, '2_current_record_stats')
        # data_generator(matchup_stats, year, '3_matchup_stats')
        data_generator(point_differential_stats, year, '4_point_differential_stats')
        combine_data(year)
