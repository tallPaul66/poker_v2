#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 31 14:10:22 2020

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
show_spit = False

def new_game(players, community_game = True):
    global deck 
    global show_spit
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
    show_spit = False
    for p in players_current_hand:
        hands[p] = []
    hands['spit'] = []

def deal(players):
    global show_spit
    stage_len = len(stage)
    if stage_len == 0:
        new_game(players)
        for key in players:
            if key != 'spit':
                for i in range(5):
                    hands[key].append(deck.pop())
        hands['spit'].append(deck.pop())                
        stage.append('draw')
        return hands
    elif stage[0]=='draw':
        for key in players:
            if key in draw_card_idxs.keys():
                for i in range(5):
                    if draw_card_idxs[key][i] == False:
                        hands[key][i] = deck.pop()      
        stage.clear()
        stage.append('reveal_spit')
        return hands
    else:
        stage.clear()
        show_spit = True
        return hands
        

def get_display(hands, whose_pg):
    global show_spit
    display_hands = {}
    for key in hands.keys():
        cards = hands[key]
        if key != whose_pg:
            if key != 'spit':
                cards = [card_back] * 5
            else:
                cards = [card_back]
        display_hands[key] = cards    
    if show_spit:        
        display_hands['spit'] = hands['spit']
    return display_hands
