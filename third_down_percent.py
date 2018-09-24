import nflgame

year, week, season_type = 2018, 1, 'REG'


def third_down(teamname, play_gen):
    attempts = 0
    conversions = 0
    for p in play_gen.filter(team=teamname, third_down_att=1):
        attempts += 1
        conversions += p.third_down_conv
    percentage = float(conversions)/float(attempts)*100
    return '%s: %s of %s (%.2f%%)' % (
        teamname, conversions, attempts, percentage)


games = nflgame.games(year, week, kind=season_type)
for game in games:
    print third_down(game.home, game.drives.plays()) + ' - ' \
          + third_down(game.away, game.drives.plays()) + ' W:' + game.winner

