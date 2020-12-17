#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 23:08:13 2020

@author: chaffee
"""

from card_to_path import get_img_path
import new_deck
"""
Note: we don\'t use a stage for Monty, because no matter where you
are in the game, dealing just means dealing another round of cards 
exactly the same way each time, or ending the game.

Normally in Monty you leave Monty\'s cards set after dealing the 
first round, but that doesn\'t matter--here we just deal Monty a new
hand along with everybody else. In order to not run out of cards, the
deal() function just calls new_game() every time.  

The complications in Monty (what to do when various numbers of people
stay in) are all handled by the players themselves in the game. There
is always either a choice to deal again or end, depending on who
stays in and what happens in the showdown. Dealing again is just the same 
as starting over, except for the money in the pot, but that too is handled 
by the players in the betting app.
"""

monty_match = 0
monty_winner = ''
match_amt = 0
players_staying = []
hands = {}
drop_dict = {}
card_back = new_deck.card_back
card_plc_holder_imgs = ['card_pics/card_place_holder_img.png',
                        'card_pics/card_place_holder_img2_sm2.png',
                        'card_pics/card_place_holder_img3.jpg',
                        'card_pics/card_place_holder_img4_test4.png']
cd_plc_holder_img = card_plc_holder_imgs[3]
stage = []
reveal_cards = False

def new_game(players):
    global deck 
    global reveal_cards
    global monty_match
    global monty_winner
    global match_amt
    global players_staying
    monty_match = 0
    monty_winner = ''
    match_amt = 0
    players_staying.clear()
    # generate a new, shuffled deck    
    deck = new_deck.make_deck()
    
    # convert the raw strings in deck to image file paths
    for i in range(len(deck)):
        card = deck [i]
        deck[i] = get_img_path(card)
    
    players_current_hand = players.copy()
    hands.clear()
    stage.clear()
    reveal_cards = False
    for p in players_current_hand:
        hands[p] = []
        drop_dict[p] = ''
    hands['monty'] = []


def deal(players):
    global reveal_cards
    if len(stage)==0:
        new_game(players)
        for key in players:
            for i in range(3):
                hands[key].append(deck.pop())            
        for i in range(3): # get monty's cards
            hands['monty'].append(deck.pop())
        stage.append(1)
        return hands
    else:
        reveal_cards = True
        stage.clear()
        return hands
  

def get_display(hands, whose_pg):
    display_hands = {}
    for key in hands.keys():
        cards = hands[key]
        if key != whose_pg:
            cards = [card_back] * 3
        display_hands[key] = cards
        if whose_pg in hands.keys() and drop_dict[whose_pg] != 'hold': # display the player's own hand
            display_hands[whose_pg] = hands[whose_pg]
    if reveal_cards == True:
        for key in drop_dict.keys():
            if drop_dict[key] != 'drop':
                display_hands[key] = hands[key]
            else:
                display_hands[key] = [card_back] *3
    return display_hands 
    