#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 2022

@author: chaffee
"""

from card_to_path import get_img_path
import new_deck

hands = {}
draw_card_idxs = {}
card_back = new_deck.card_back
card_plc_holder_imgs = ['static/card_pics/blank_img.png',
                        'static/card_pics/card_place_holder_img.png']
card_plc_holder_img = card_plc_holder_imgs[0]
stage = []
cards_played = {}
trick_counter = 0
tricks = {}
who_just_played = ['']
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# it's nice to have cards sorted by suit and
# denomination in Smear...
def sort_generic(suited_list, suit):
    """" will return a sorted version of a list of the form
    ['AH', 'TH', '4H'...] where the sorting is the way cards
    are sorted in poker from high to low with 'A' as highest 
    and '2' as lowest. 
    
    Also returns the highest rank in the passed list
    """
    suited_sorted = []
    max_in_suit = 0  # this keeps track of the max ranked card in the suit
    rank_order = ['A', 'K', 'Q', 'J', 'T']
    for rank in rank_order: # this way A gets added first, K second and so on
        if rank+suit in suited_list:
            suited_sorted.append(rank+suit)
            suited_list.remove(rank+suit)
            if rank == 'A':
                max_in_suit = 14
            elif max_in_suit < 14 and rank == 'K':
                max_in_suit = 13
            elif max_in_suit < 13 and rank == 'Q':
                max_in_suit = 12
            elif max_in_suit < 12 and rank == 'J':
                max_in_suit = 11
            else:
                if max_in_suit < 11:
                    max_in_suit = 10
     # Now the sort method for list can handle the remaining card denominations
    suited_list = sorted(suited_list, reverse=True)
    if max_in_suit < 10 and len(suited_list) > 0:
        max_in_suit = int(suited_list[0][0])
    suited_sorted.extend(suited_list)
    return suited_sorted, max_in_suit

def sort_cards(card_list):
    if len(card_list) > 0:
        c = card_list[0]
        error_msg = ('Path to card  pics is no longer' +
            '"static/card_pics/" or extentions are no longer ".jpg"')
        assert c[:17] == 'static/card_pics/' and c[-4:] == '.jpg', error_msg
    card_list_no_path = [c[-6:-4] for c in card_list]
    hrt = [c for c in card_list_no_path if 'H' in c]
    dia = [c for c in card_list_no_path if 'D' in c]
    spd = [c for c in card_list_no_path if 'S' in c]
    clb = [c for c in card_list_no_path if 'C' in c]
    
    hrt_sorted, max_hrt = sort_generic(hrt, 'H')
    hrt_sorted_with_rank = []
    hrt_sorted_with_rank.append(max_hrt)
    hrt_sorted_with_rank.extend(hrt_sorted)
    dia_sorted, max_dia = sort_generic(dia, 'D')
    dia_sorted_with_rank = []
    dia_sorted_with_rank.append(max_dia)
    dia_sorted_with_rank.extend(dia_sorted)
    spd_sorted, max_spd = sort_generic(spd, 'S')
    spd_sorted_with_rank = []
    spd_sorted_with_rank.append(max_spd)
    spd_sorted_with_rank.extend(spd_sorted)
    clb_sorted, max_clb = sort_generic(clb, 'C')
    clb_sorted_with_rank = []
    clb_sorted_with_rank.append(max_clb)
    clb_sorted_with_rank.extend(clb_sorted)
    
    cards_by_suit = [hrt_sorted_with_rank, dia_sorted_with_rank, spd_sorted_with_rank, 
                   clb_sorted_with_rank]
    cards_by_suit.sort(reverse = True)
    
    all_sorted = []
    for suit_set in cards_by_suit:
        if len(suit_set) > 1:
            all_sorted.extend(suit_set[1:])
    sorted_with_path = ['static/card_pics/' + a + '.jpg' for a in all_sorted]
    
    return sorted_with_path

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def new_game(players):
    global deck 
    # generate a new, shuffled deck    
    deck = new_deck.make_deck()
    
    # convert the raw strings in deck to image file paths
    for i in range(len(deck)):
        card = deck[i]
        deck[i] = get_img_path(card)
    
    hands.clear()
    cards_played.clear()
    draw_card_idxs.clear()
    stage.clear()
    tricks.clear()
    trick_counter = 0
    who_just_played.clear()
    who_just_played.append('')
    
    for p in players:
        hands[p] = []
    

def deal(players):
    new_game(players)        
    for player in players:
        tricks[player] = []
        cards_played[player] = ''
        for i in range(6):
            hands[player].append(deck.pop())
    return hands


def get_display(hands, whose_pg):
    display_hands = {}
    # player is not 'whose_pg'
    for key in hands.keys():
        cards = hands[key]
        if key != whose_pg:
            cards = [card_back] * 6
            # cards.append('')  # add a card place holder at the end
        else:
             cards = sort_cards(cards)
             # cards.append('')
        display_hands[key] = cards
    return display_hands

def get_trump_hi_and_low(trump_suit):
    trump_cards = []
    for player in tricks.keys():
        card_list = tricks[player]
        if len(card_list) > 0:
            c = card_list[0]
            error_msg = ('Path to card  pics is no longer' +
                            '"static/card_pics/" or extentions are no longer ".jpg"')
            assert c[:17] == 'static/card_pics/' and c[-4:] == '.jpg', error_msg
        card_list_no_path = [c[-6:-4] for c in card_list]
        trump_list = []  # in case player has no cards of trump suit
        if trump_suit == 'HEARTS':
            trump_abbrev = 'H'
            trump_list = [c for c in card_list_no_path  if 'H' in c]
        elif trump_suit == 'DIAMONDS':
            trump_abbrev = 'D'
            trump_list = [c for c in card_list_no_path  if 'D' in c]
        elif trump_suit == 'SPADES':
            trump_abbrev = 'S'
            trump_list = [c for c in card_list_no_path  if 'S' in c]
        elif trump_suit == 'CLUBS':
            trump_abbrev = 'C'
            trump_list = [c for c in card_list_no_path  if 'C' in c]
        
        trump_cards.extend(trump_list)
        
    sorted_trump_cards, hi_card = sort_generic(trump_cards, trump_abbrev)

    return {'high': sorted_trump_cards[0], 'low': sorted_trump_cards.pop()}
            
        
