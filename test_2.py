import utils
import numpy as np
import nflgame
import itertools


mylist = ['1', '2']
#[1, 2, 12]

mylist = ['1', '2', '3']
#[1, 2, 3, 12, 13, 23, 123]

mylist = ['1', '2', '3', '4']
#[1, 2, 3, 4, 12, 13, 14, 23, 24, 34, 123, 124, 134, 234, 1234]


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
                 ]
for r in range(4, len(feature_names)+1):
    print list(itertools.combinations(feature_names, r))



