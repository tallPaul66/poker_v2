#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 01:23:55 2020

@author: chaffee
"""

from card_to_path import get_img_path
import new_deck

hands = {}
card_back = new_deck.card_back
card_plc_holder_imgs = ['static/card_pics/card_place_holder_img.png',
                        'static/card_pics/card_place_holder_img2_sm2.png',
                        'static/card_pics/card_place_holder_img3.jpg',
                        'static/card_pics/card_place_holder_img4_test4.png']
cd_plc_holder_img = card_plc_holder_imgs[3]
stage = []

def new_game(players):
    global deck 
    # generate a new, shuffled deck    
    deck = new_deck.make_deck()
    
    # convert the raw strings in deck to image file paths
    for i in range(len(deck)):
        card = deck[i]
        deck[i] = get_img_path(card)
    players_current_hand = players.copy()
    hands.clear()
    stage.clear()
    for p in players_current_hand:
        hands[p] = [] 
    hands['comm'] = []

def deal(players):
    if len(stage) == 0:
        new_game(players)
        for key in players:
            for i in range(4):
                hands[key].append(deck.pop())
        # sending dict to html requires values be tuples, not lists...
        stage.append('flop')
        return hands
    elif stage[0] == 'flop':
        for card in range(3):
            hands['comm'].append(deck.pop())
        stage.pop()
        stage.append('turn')
        return hands
    elif stage[0] == 'turn':
        hands['comm'].append(deck.pop())
        stage.pop()
        stage.append('river')
        return hands
    else:
        hands['comm'].append(deck.pop())
        stage.clear()
        return hands
        
def get_display(hands, whose_pg, whos_folded):
    display_hands = {}  
    
    # convert card pics to card back pics if 
    # player is not 'whose_pg'
    for key in hands.keys():
        cards = hands[key].copy()
        if key not in ['comm', whose_pg]:
            cards = [card_back] * 4
        display_hands[key] = cards
    # need additional code to show the special card
    # backs for players who've folded
    for p in whos_folded:
        num_cards = len(hands[p])
        display_hands[p] = [new_deck.card_back_fold]*num_cards
    num_comm_cards = len(hands['comm'])
    if num_comm_cards < 5:
        display_hands['comm'].extend([cd_plc_holder_img]*(5-num_comm_cards))
    return display_hands
