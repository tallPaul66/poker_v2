#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 15:46:57 2021
Algorithm for how to settle up when the poker session is over. The approach taken
here is that each person either makes or receives one payment, and some players do 
both, but no player pays more than one other player or  receives payment from more 
than one other player.
@author: Paul chaffee
"""
import pandas as pd
#buy_in = 80

#player_stash_map = {'player1': 96, 'player2': 58, 'player3': 92, 'player4': 82, 'player5':72,
#                 'player6':0}
#player_name_map = {'player1': 'Bobster', 'player2': 'Laszlo', 'player3': 'Chafe', 
#                   'player4': 'Dr. B', 'player5': 'Jeff', 'player6': 'Steve'}

def settle_up(player_stash_map, player_name_map, buy_in):
    # create a dataframe containing players' names and their stashes and surpluses or debits
    df_settle =  pd.DataFrame({'player': list(player_stash_map.keys()), 
                    'stash': list(player_stash_map.values())})
    df_settle['d'] = df_settle['stash']  - buy_in
    df_settle = df_settle[df_settle.d != -buy_in]
    if len(df_settle==0): 
        return []
    ### 1st consolidate the losers and their payments
    df_losers = df_settle[df_settle.d < 0].copy()
    df_losers.sort_values(by = 'd', ascending=False, inplace=True)
    payments = []
    # Losers pay off first...
    while len(df_losers) > 1:
        payments.append(player_name_map[df_losers.player.iloc[0]] + ' pays ' + 
                        player_name_map[df_losers.player.iloc[1]] +' $' + str(-df_losers.d.iloc[0]))
        df_losers.loc[df_losers['player'] == df_losers.player.iloc[1], 'd'] = df_losers.d.iloc[0] + df_losers.d.iloc[1]
        df_losers.drop([df_losers.index[0]], inplace=True)
    # now the final loser to receive a payment pays the first person in the 
    # winner group
    df_winners = df_settle.copy()[df_settle.d > 0]
    df_winners.sort_values(by = 'd', inplace=True)
    payments.append(player_name_map[df_losers.player.iloc[0]] + ' pays ' + 
                player_name_map[df_winners.player.iloc[0]] +' $' + str(-df_losers.d.iloc[0]))
    df_winners.loc[df_winners['player'] == df_winners.player.iloc[0], 'd'] = df_winners.d.iloc[0] + df_losers.d.iloc[0]
    
    # that player then pays the next winner from his stash
    while len(df_winners) > 1:
        payments.append(player_name_map[df_winners.player.iloc[0]] + ' pays ' + 
                        player_name_map[df_winners.player.iloc[1]] + ' $' + str(-df_winners.d.iloc[0]))
        df_winners.loc[df_winners['player'] == df_winners.player.iloc[1], 'd'] = df_winners.d.iloc[0] + df_winners.d.iloc[1]
        df_winners.drop([df_winners.index[0]], inplace=True)

    return(payments)