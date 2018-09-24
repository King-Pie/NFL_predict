import nflgame
import numpy as np

division_dictionary = {
    'ARI': 'NFC_west',
    'ATL': 'NFC_south',
    'BAL': 'AFC_north',
    'BUF': 'AFC_east',
    'CAR': 'NFC_south',
    'CHI': 'NFC_north',
    'CIN': 'AFC_north',
    'CLE': 'AFC_north',
    'DAL': 'NFC_east',
    'DEN': 'AFC_west',
    'DET': 'NFC_north',
    'GB':  'NFC_north',
    'HOU': 'AFC_south',
    'IND': 'AFC_south',
    'JAC': 'AFC_south',
    'JAX': 'AFC_south',
    'KC':  'AFC_west',
    'STL': 'NFC_west',
    'LA':  'NFC_west',
    'SD':  'AFC_west',
    'LAC': 'AFC_west',
    'MIA': 'AFC_east',
    'MIN': 'NFC_north',
    'NE':  'AFC_east',
    'NO':  'NFC_south',
    'NYG': 'NFC_east',
    'NYJ': 'AFC_east',
    'OAK': 'AFC_west',
    'PHI': 'NFC_east',
    'PIT': 'AFC_north',
    'SEA': 'NFC_west',
    'SF':  'NFC_west',
    'TB':  'NFC_south',
    'TEN': 'AFC_south',
    'WAS': 'NFC_east'
}

alternate_team_names = {
    'JAC': 'JAX', 'JAX': 'JAC',
    'LAC': 'SD', 'SD': 'LAC',
    'LA': 'STL', 'STL': 'LA'
}


def get_week_schedule(year, week, season_type='REG'):

    week_schedule = []

    schedule = nflgame.sched.games
    x = [schedule[game] for game in schedule]
    for g in x:
        if g['year'] == year and \
                g['week'] == week and \
                g['season_type'] == season_type:

            week_schedule.append(g)

    return week_schedule


def team_record(team, year, week=17, type='total'):

    if week == 0:
        return [0, 0, 0]

    if type == 'total':
        games = nflgame.games_gen(year, week=range(1, week + 1), home=team, away=team)
    elif type == 'home':
        games = nflgame.games_gen(year, week=range(1, week + 1), home=team)
    elif type == 'away':
        games = nflgame.games_gen(year, week=range(1, week + 1), away=team)

    if games is None:
        try:
            team = alternate_team_names[team]
            if type == 'total':
                games = nflgame.games_gen(year, week=range(1, week + 1), home=team, away=team)
            elif type == 'home':
                games = nflgame.games_gen(year, week=range(1, week + 1), home=team)
            elif type == 'away':
                games = nflgame.games_gen(year, week=range(1, week + 1), away=team)
        except KeyError:
            return [0, 0, 0]

    wins, losses, ties = 0, 0, 0

    try:
        for g in games:
            if g.winner == g.home + '/' + g.away:
                ties += 1
            elif g.winner == team:
                wins += 1
            else:
                losses += 1

        return [wins, losses, ties]

    except TypeError:
        return [0, 0, 0]


def team_season_win_pct(team, year, week=17, type='total'):

    if week == 0:
        return 0

    record = team_record(team, year, week, type=type)
    win, loss, tie = record
    total = sum(record)
    try:
        win_percentage = round((win + tie/2.0)/total, 3)
    except ZeroDivisionError:
        win_percentage = 0

    return win_percentage


def team_prev_season_win_pct(team, year, prev_seasons=1, type='total'):

    total_record = np.array([0, 0, 0])
    for year in range(year-1, year-prev_seasons-1, -1):
        total_record += team_record(team, year, type=type)

    win, loss, tie = total_record
    total = sum(total_record)
    try:
        win_percentage = round((win + tie*0.5)/total, 3)
    except ZeroDivisionError:
        win_percentage = 0

    return win_percentage


def divisional_flag(home, away):

    if division_dictionary[home] == division_dictionary[away]:
        return 1
    else:
        return 0


def matchup_weight(game, prev_seasons=2, verbose=False):

    # for convenience
    year, week = game['year'], game['week']
    home, away = game['home'], game['away']
    gamekey = game['gamekey']

    h_team = [home, away, home, away]
    a_team = [away, home, away, home]
    kinds = ['REG', 'REG', 'POST', 'POST']

    if verbose:
        print home, ' AT ', away, year, week
        print '---------'

    matchups = []
    for h, a, k in zip(h_team, a_team, kinds):
        try:
            game_matches = nflgame.games(year=range(year, year - (prev_seasons + 1), -1),
                                         home=h, away=a, kind=k)
            for g in game_matches:
                if g.schedule['gamekey'] != gamekey:
                    matchups.append(g)
        except (TypeError, AttributeError) as e:
            pass

    home_matchup_wins, away_matchup_wins = 0, 0
    for m in matchups:
        if verbose:
            print m, m.schedule['season_type'], m.schedule['year'], m.schedule['week']

        if m.winner == home:
            home_matchup_wins += 1
        elif m.winner == away:
            away_matchup_wins += 1
        else:
            home_matchup_wins += 0.5
            away_matchup_wins += 0.5

    total = sum([home_matchup_wins, away_matchup_wins])
    if total == 0:
        home_matchup_wpct, away_matchup_wpct = 0, 0
    else:
        home_matchup_wpct = round(home_matchup_wins / float(total), 3)
        away_matchup_wpct = round(away_matchup_wins / float(total), 3)

    if verbose:
        print '---------'
        print '({}) {} - {} ({})'.format(home_matchup_wins, home,
                                         away, away_matchup_wins)
        print '{} - {}'.format(home_matchup_wpct, away_matchup_wpct)

        print '\n'

    # return home_matchup_wpct, away_matchup_wpct
    # return (home_matchup_wpct - away_matchup_wpct)*0.5 + 0.5
    return home_matchup_wpct - away_matchup_wpct



if __name__ == "__main__":

    team = 'TB'
    print team, division_dictionary[team]

    print team_record(team, 2017)
    print team_season_win_pct(team, 2017)
