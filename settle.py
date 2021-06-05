#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 15:46:57 2021
Algorithm for how to settle up after the poker session is over. The approach taken
here is that each person either makes or receives one payment, and some players do 
both, but no player pays more than one other player or  receives payment from more 
than one other player.
@author: admin
"""
#import numpy as np
import pandas as pd
#buy_in = 80

#player_stash_map = {'player1': 62, 'player2': 98, 'player3': 71, 'player4': 89, 'player5':114,
#                  'player6':46}
#player_name_map = {'player1': 'Bobster', 'player2': 'Laszlo', 'player3': 'Chafe', 
#                   'player4': 'Dr. B', 'player5': 'Jeff', 'player6': 'Steve'}

def settle_up(player_stash_map, player_name_map, buy_in):
    df_settle = pd.DataFrame(data = player_stash_map, index = player_stash_map.keys()).T
    df_settle.rename(columns={'player1': 'stash', 'player2': 'd'}, inplace = True)
    df_settle = df_settle[['stash', 'd']].copy()
    #df_settle['d'] = df_settle['stash'].apply(lambda x: x - buy_in if isinstance(x, int) else 0)
    df_settle['d'] = df_settle['stash'].apply(lambda x: x - buy_in)
    df_settle = df_settle[df_settle.d != -buy_in].copy()
    ### 1st consolidate the losers and their payments
    df_losers = df_settle[df_settle.d < 0].copy()
    df_losers.sort_values(by = 'd', ascending=False, inplace=True)

    payments = []
    while len(df_losers) > 1:
        payments.append(player_name_map[df_losers.index[0]] + ' pays ' + 
                        player_name_map[df_losers.index[1]] +' $' + str(-df_losers.d.iloc[0]))
        df_losers.d.iloc[1] = df_losers.d.iloc[0] + df_losers.d.iloc[1]
        df_losers.drop([df_losers.index[0]], inplace=True)

    # now the final loser to receive a payment pays the first person in the 
    # winner group
    df_winners = df_settle[df_settle.d > 0].copy()
    df_winners.sort_values(by = 'd', inplace=True)
    payments.append(player_name_map[df_losers.index[0]] + ' pays ' + 
                player_name_map[df_winners.index[0]] +' $' + str(-df_losers.d.iloc[0]))
    df_winners.d.iloc[0] =  df_winners.d.iloc[0] + df_losers.d.iloc[0]

    while len(df_winners) > 1:
        payments.append(player_name_map[df_winners.index[0]] + ' pays ' + 
                        player_name_map[df_winners.index[1]] + ' $' + str(-df_winners.d.iloc[0]))
        df_winners.d.iloc[1] = df_winners.d.iloc[0] + df_winners.d.iloc[1]
        df_winners.drop([df_winners.index[0]], inplace=True)

    return(payments)