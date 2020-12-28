#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 02:50:24 2020

@author: chaffee
"""

from card_to_path import get_img_path
import new_deck

hands = {}
draw_card_idxs = {}
card_back = new_deck.card_back
card_plc_holder_imgs = ['card_pics/card_place_holder_img.png',
                        'card_pics/card_place_holder_img2_sm2.png',
                        'card_pics/card_place_holder_img3.jpg',
                        'card_pics/card_place_holder_img4_test4.png']
cd_plc_holder_img = card_plc_holder_imgs[3]
stage = []

def new_game(players, community_game = False):
    global deck 
    # generate a new, shuffled deck    
    deck = new_deck.make_deck()
    
    # convert the raw strings in deck to image file paths
    for i in range(len(deck)):
        card = deck[i]
        deck[i] = get_img_path(card)
    
    players_current_hand = players.copy()
    hands.clear()
    draw_card_idxs.clear()
    stage.clear()
    for p in players_current_hand:
        hands[p] = []    

def deal(players):
    stage_len = len(stage)
    if stage_len == 0:
        new_game(players)
        for key in players:
            for i in range(5):
                hands[key].append(deck.pop())
        stage.append(2)
        return hands 
    else:
        for key in players:
            if key in draw_card_idxs.keys():
                for i in range(5):
                    if draw_card_idxs[key][i] == False:
                        hands[key][i] = deck.pop()        
        stage.clear()
        return hands 


def get_display(hands, whose_pg):
    display_hands = {}
    # player is not 'whose_pg'
    for key in hands.keys():
        cards = hands[key]
        if key != whose_pg:
            cards = [card_back] * 5
        display_hands[key] = cards
    return display_hands
