#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 20:29:01 2020

@author: chaffee
"""
from card_to_path import get_img_path
import new_deck

hands = {}
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
    stage.clear()
    for p in players_current_hand:
        hands[p] = []
    

# very annoying: you can't pass lists of things to the url, you have
# to use tuples. But python tuples are immutable, so have to create
# a new one with every new card dealt.       

def deal(players):
    stage_len = len(stage)
    if stage_len == 0:
        new_game(players)
        for key in players:
            for i in range(3):
                hands[key].append(deck.pop())
        stage.append(2)      
        # now have to turn the lists into tuples for sending to url
        # hands_tuple = hands.copy()
        # for key in hands_tuple.keys():
        #    hands_tuple[key] = tuple(hands[key])
        return hands #hands_tuple
    elif stage[stage_len - 1] < 5:
        for key in players:
            hands[key].append(deck.pop())
        stage.append(stage[stage_len -1] + 1)
        # hands_tuple = hands.copy()
        # for key in hands_tuple.keys():
        #     hands_tuple[key] = tuple(hands[key])
        return hands # hands_tuple
    else:
        for key in players:
            hands[key].append(deck.pop())
        #hands_tuple = hands.copy()
        #for key in hands_tuple.keys():
        #    hands_tuple[key] = tuple(hands[key])
        stage.clear()
        return hands #hands_tuple

def get_display(hands_list, whose_pg, whos_folded):
    display_hands = {}
    
    # convert 1st, 2nd and 7th card pics to card back pic if 
    # player is not 'whose_pg'
    for key in hands_list.keys():
        cards = hands_list[key].copy() # without this, global hands gets modified somehow
        num_cards = len(cards)
        if key != whose_pg:
            cards[0] = card_back
            cards[1] = card_back
            if num_cards ==7:
                cards[6] = card_back
        if num_cards < 7: # add fancy card place holder graphics 
            cards.extend([cd_plc_holder_img]*(7-num_cards))
        display_hands[key] = cards
    # need additional code to show the special card
    # backs for players who've folded
    for p in whos_folded:
        num_cards = len(hands[p])
        display_hands[p] = [new_deck.card_back_fold]*num_cards
    return display_hands
            
            
    
    

    