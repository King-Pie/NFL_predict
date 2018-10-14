import nflgame
import utils
import pandas as pd
import csv

pd.set_option('display.expand_frame_repr', False)
pd.options.display.max_rows = 999


training_year_list = range(2010, 2018)
stat_function_names = [
    'schedule_stats',
    'current_record_stats',
    'matchup_stats',
    'point_differential_stats',
    'turnover_stats',
    'third_down_pct_stats']


def stat_function_list():
    return [globals()[k] for k in stat_function_names]


def year_data_generator(stat_func, year):

    games = []
    for week in range(1, 18):
        for g in utils.get_week_schedule(year, week):
            games.append(g)

    data, set_name = stat_func(games)
    path = './data/training_data/{}/{}.csv'.format(year, set_name)

    with open(path, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for line in data:
            writer.writerow(line)


def week_data_generator(stat_func, year, week):
    import os

    games = utils.get_week_schedule(year, week)

    data, set_name = stat_func(games)
    directory = './data/prediction_data/{}/{}/'.format(year, week)
    file_name = '{}.csv'.format(set_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = directory + file_name

    with open(path, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for line in data:
            writer.writerow(line)


def schedule_stats(games):
    """
    Generates basic stats about the game which don't change throughout the season
    :param games:
    :return:
    """
    header = ['gamekey', 'year', 'week',
              'away', 'away_prev_wpct', 'away_prev_a_wpct',
              'home', 'home_prev_wpct', 'home_prev_h_wpct',
              'div_flag']

    data = []
    data.append(header)

    print 'Generating schedule stats:'

    week_dummy = 0  # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
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

    return data, '1_schedule_stats'


def current_record_stats(games):

    header = ['away_record', 'away_wpct', 'away_a_wpct',
              'home_record', 'home_wpct', 'home_h_wpct', 'result']

    data = []
    data.append(header)

    print 'Generating current record stats:'

    week_dummy = 0      # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
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

    return data, '2_current_record_stats'


def matchup_stats(games):

    header = ['matchup_weight']

    data_dict = {}
    data = []
    data.append(header)

    print 'Generating matchup stats:'

    week_dummy = 0  # for reporting progress
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
        week_dummy = week

        data_dict['matchup_weight'] = utils.matchup_weight(game)
        row = [data_dict[h] for h in header]
        data.append(row)

    return data, '3_matchup_stats'


def point_differential_stats(games):

    data_dict = {}
    data = []
    header = ['home_season_pt_dif', 'home_3game_pt_dif', 'home_5game_pt_dif', 'home_prev_season_pt_dif',
              'away_season_pt_dif', 'away_3game_pt_dif', 'away_5game_pt_dif', 'away_prev_season_pt_dif']
    data.append(header)

    print 'Generating point differential stats:'

    week_dummy = 0
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print home, away

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
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

    return data, '4_point_differential_stats'


def turnover_stats(games):

    data_dictionary = {}
    data = []
    header = [
        'home_season_turnovers',
        'home_3game_turnovers',
        'home_5game_turnovers',
        'home_prev_season_turnovers',
        'away_season_turnovers',
        'away_3game_turnovers',
        'away_5game_turnovers',
        'away_prev_season_turnovers',
        'home_season_turnover_dif',
        'home_3game_turnover_dif',
        'home_5game_turnover_dif',
        'home_prev_season_turnover_dif',
        'away_season_turnover_dif',
        'away_3game_turnover_dif',
        'away_5game_turnover_dif',
        'away_prev_season_turnover_dif',
    ]
    data.append(header)

    print 'Generating turnover stats:'

    week_dummy = 0
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
        week_dummy = week

        # Previous season stats
        home_prev_season_turnover_dict = utils.turnovers_per_game_season(home, year-1)
        away_prev_season_turnover_dict = utils.turnovers_per_game_season(away, year-1)
        data_dictionary['home_prev_season_turnovers'] = home_prev_season_turnover_dict['turnovers_per_game']
        data_dictionary['home_prev_season_turnover_dif'] = home_prev_season_turnover_dict['turnover_dif_per_game']
        data_dictionary['away_prev_season_turnovers'] = away_prev_season_turnover_dict['turnovers_per_game']
        data_dictionary['away_prev_season_turnover_dif'] = away_prev_season_turnover_dict['turnover_dif_per_game']

        for team, label in zip([home, away], ['home', 'away']):
            turnover_dict = utils.turnovers_per_game(team, year, week)
            data_dictionary[label + '_season_turnovers'] = turnover_dict['season_turnovers_per_game']
            data_dictionary[label + '_3game_turnovers'] = turnover_dict['3game_turnovers_per_game']
            data_dictionary[label + '_5game_turnovers'] = turnover_dict['5game_turnovers_per_game']
            data_dictionary[label + '_season_turnover_dif'] = turnover_dict['season_turnover_dif_per_game']
            data_dictionary[label + '_3game_turnover_dif'] = turnover_dict['3game_turnover_dif_per_game']
            data_dictionary[label + '_5game_turnover_dif'] = turnover_dict['5game_turnover_dif_per_game']

        row = [data_dictionary[h] for h in header]
        data.append(row)

    return data, '5_turnover_stats'


def third_down_pct_stats(games):

    data_dictionary = {}
    headers = [
        'home_season_3down_pct',
        'home_3game_3down_pct',
        'home_5game_3down_pct',
        'away_season_3down_pct',
        'away_3game_3down_pct',
        'away_5game_3down_pct'
    ]
    data = []
    data.append(headers)

    print 'Generating third down stats:'

    week_dummy = 0
    for game in games:
        # for convenience
        year, week = game['year'], game['week']
        home, away = game['home'], game['away']

        # print progress generating each week
        if week_dummy != week:
            if week % 4 == 0:
                print '{} week {}'.format(year, week)
        week_dummy = week

        for team, label in zip([home, away], ['home', 'away']):
            tdp_dict = utils.third_down_pct_per_game(team, year, week)
            data_dictionary[label + '_season_3down_pct'] = tdp_dict['season_3down_pct_per_game']
            data_dictionary[label + '_3game_3down_pct'] = tdp_dict['3game_3down_pct_per_game']
            data_dictionary[label + '_5game_3down_pct'] = tdp_dict['5game_3down_pct_per_game']

        row = [data_dictionary[h] for h in headers]
        data.append(row)

    return data, '6_third_down_stats'


def combine_yearly_training_data(year):
    import glob

    print 'Combing data for {}'.format(year)

    directory_path = './data/training_data/{}/'.format(year)

    all_files = glob.glob(directory_path + '*.csv')
    df = pd.concat((pd.read_csv(f) for f in all_files),
                   axis=1, sort=False)
    df.to_csv('./data/training_data/{}_database.csv'.format(year), index=False)


def generate_and_combine_week_data(year, week, update_only=True):
    import glob

    print 'Generating and combining weekly data for {} week {}'.format(year, week)

    directory_path = './data/prediction_data/{}/{}/'.format(year, week)
    all_files = glob.glob(directory_path + '*.csv')

    for func in stat_function_list():
        week_data_generator(func, year, week)

    all_files = glob.glob(directory_path + '*.csv')
    df = pd.concat((pd.read_csv(f) for f in all_files),
                   axis=1, sort=False)
    df.to_csv('./data/prediction_data/{}/week_{}_database.csv'.format(year, week), index=False)


if __name__ == "__main__":

    week_list = [4, 5]
    for week in week_list:
        generate_and_combine_week_data(2018, week)

    # years = training_year_list
    # years = [2017]
    # print years
    # for year in years:
    #     print 'Data generation for {}'.format(year)
    #     year_data_generator(schedule_stats, year)
    #     year_data_generator(current_record_stats, year)
    #     year_data_generator(matchup_stats, year)
    #     year_data_generator(point_differential_stats, year)
    #     year_data_generator(turnover_stats, year)
    #     year_data_generator(third_down_pct_stats, year)
    #     combine_yearly_training_data(year)
