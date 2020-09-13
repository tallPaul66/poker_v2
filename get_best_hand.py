#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 22:02:27 2020

@author: admin
"""
import numpy as np
from itertools import combinations 
# this is for picking the best combo of five cards from more than five cards.
# case 1: a game like 7-card stud where there is one list of cards, > length 7, from which
#   five cards must be drawn.
# case 2: games like Omaha or Hold 'em or Fiery Cross where combos from different sets
#   must be evaluated
def get_best_hand(hands):
    scores = [(i, score(hand)) for i, hand in enumerate(hands)]
    last_ranked = sorted(scores , key=lambda x:x[1])[-1][0]
    second_ranked = sorted(scores , key=lambda x:x[1])[-2][0]
    third_ranked = sorted(scores , key=lambda x:x[1])[-3][0]
    
    # Check for ties
    last_ranked_tuple = sorted(scores , key=lambda x:x[1])[-1][1:3]
    second_ranked_tuple = sorted(scores , key=lambda x:x[1])[-2][1:3]
    third_ranked_tuple = sorted(scores , key=lambda x:x[1])[-3][1:3]
    if last_ranked_tuple == third_ranked_tuple:
        print('THree-way tie!')
        return [hands[last_ranked], hands[second_ranked], hands[third_ranked]]
    elif last_ranked_tuple == second_ranked_tuple:
        print('Tie!')
        return [hands[last_ranked], hands[second_ranked]]    
    else:
        return [hands[last_ranked]]

def score(hand): 
    ranks = '23456789TJQKA'
    rcounts = {ranks.find(r): ''.join(hand).count(r) for r, _ in hand}.items()
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts)[::-1])
    if len(score) == 5: # kicks in if all cards are different values
        if ranks[0:2] == (12, 3): #adjust if 5 high straight
            ranks = (3, 2, 1, 0, -1)
        straight = ranks[0] - ranks[4] == 4
        flush = len({suit for _, suit in hand}) == 1
        '''no pair, straight, flush, or straight flush'''
        score = ([(1,), (3,1,1,1)], [(3,1,1,2), (5,)])[flush][straight]
    if score[0] == 5 and len(ranks) == 1: # 5-of-a-kind goes at the top
        score = (6,)
    return score, ranks

def get_best_comb(dict, holdem = False):
    '''' Finds the best hand among all the allowed combos of the player\'s hand
    and community cards. Hold em is a special case because allowable combos 
    include 0, 1 or 2 cards from the player\'s hand, plus comm cards.'''
    lists = dict['lists']
    if len(lists) == 1: # We'll find the best combo of cards from the list
        indexes = [x for x in range(len(lists[0]))]
        ind_combs = list(combinations(indexes, dict['choose'][0]))
        ind_combs = [list(x) for x in ind_combs]
        print(ind_combs)
        combos = [list(np.array(lists[0])[x]) for x in ind_combs]
        return get_best_hand(combos)
    elif len(lists) == 2: 
        list_1 = lists[0]
        list_2 = lists[1] 
        indexes_1 = [x for x in range(len(list_1))]
        indexes_2 = [x for x in range(len(list_2))]
        ind_combs_1 = list(combinations(indexes_1, dict['choose'][0]))
        ind_combs_1 = [list(x) for x in ind_combs_1]
        ind_combs_2 = list(combinations(indexes_2, dict['choose'][1]))
        ind_combs_2 = [list(x) for x in ind_combs_2]
        combos_1 = [list(np.array(list_1)[x]) for x in ind_combs_1]
        combos_2 = [list(np.array(list_2)[x]) for x in ind_combs_2]
        combos = []
        if holdem: # Hold em allows 1 or 0 cards from player hand as well as 2
            # combos for 1 from hand, 4 from community
            ind_combs_1_14 = list(combinations(indexes_1, 1))
            ind_combs_1_14 = [list(x) for x in ind_combs_1_14]
            ind_combs_2_14 = list(combinations(indexes_2, 4))
            ind_combs_2_14 = [list(x) for x in ind_combs_2_14]
            combos_1_14 = [list(np.array(list_1)[x]) for x in ind_combs_1_14]
            combos_2_14 = [list(np.array(list_2)[x]) for x in ind_combs_2_14]
            for i in combos_1_14:
                i_tmp = i.copy()
                for j in combos_2_14:
                    i = i_tmp.copy()
                    i.extend(j)
                    combos.append(i)
            # combos for 0 from hand, 5 from community
            combos.append(list_2)
            
        for x in combos_1:
            x_tmp = x.copy()
            for y in combos_2:
                x = x_tmp.copy()
                x.extend(y)
                combos.append(x)
        return get_best_hand(combos)
    elif len(lists) == 3: # looks like Fiery Cross?
        # have to include info on how to do the combos
        # gets complimacated...
        print('wtf')
    else:
        print('Something went wrong. Too many lists passed in.')