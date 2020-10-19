#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 15:11:35 2020

@author: Paul Chaffee
"""

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
# import gevent
import get_best_hand

# Import games. Be sure to clear game stage in claim_pot(), add line in fold(), and in new_game()
import draw
import five_card_stud
import seven_card_stud
import omaha 
import monty 
import spit 
import holdem
    

#~~~~~~~~~~~~~~~~~~~ Config Stuff ~~~~~~~~~~~~~~~~~
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


# throws error
#eventlet.server(eventlet.listen(('', 5000)), app, log_output=False)


### and these do nothing
#import logging
#logging.getLogger('socketio').setLevel(logging.ERROR)
#logging.getLogger('engineio').setLevel(logging.ERROR)
#logging.getLogger('geventwebsocket.handler').setLevel(logging.ERROR)
###
socketio = SocketIO(app, async_mode=async_mode, ping_interval=10000, ping_timeout=25000) #,ping_interval=10, ping_timeout=60)

thread = None
thread_lock = Lock()

#~~~~~~~~~~~~~~~~~~~ Global Variables ~~~~~~~~~~~~~~~~~

pot_claimed = True
players_tonight = []
players_active = []
possible_players = ['player1', 'player2', 'player3', 'player4', 'player5', 'player6']
player_name_map = {}
player_stash_map = {'player1':'', 'player2':'', 'player3':'', 'player4':'', 
             'player5':'', 'player6':''}
round_bets = {'player1':0, 'player2':0, 'player3':0, 'player4':0, 
             'player5':0, 'player6':0} # keep track of players' bets in a single round
has_bet_this_round = [] # keep track of who has bet in the current round

# declaring these global variables here so they're available 
# in case someone clicks the New Game button before any hands 
# are dealt for the evening.
cards_player1_pg = {}
cards_player2_pg = {}
cards_player3_pg = {}
cards_player4_pg = {}
cards_player5_pg = {}
cards_player6_pg = {}

room_map = {'player1':'', 'player2':'', 'player3':'', 'player4':'', 
             'player5':'', 'player6':''}
pot_amount = 0
max_bet = 0
buy_in = 100

# games that require choices on the player's part beyond folding or staying in
choice_games = ['draw', 'monty', 'spit']

def pot_update(amt):
    amt = int(amt)
    global pot_amount
    global max_bet    
    if amt > max_bet: # increase call amt
        max_bet = amt
    pot_amount = pot_amount + amt


def update_room_map(player, client_sid):
    room_map[player] = client_sid
    
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(500)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated msg', 'count': count},
                      namespace='/test')

print('what the fuck')
@app.route('/', methods=['GET', 'POST'])
def home():
    global players_active
    # This method gets called any time someone clicks the submit
    # button on the home pg.    
    
    if request.method == 'POST':
        players_tonight.clear()

        player_name_map['player1'] = request.form.get('player1') 
        player_name_map['player2'] = request.form.get('player2')
        player_name_map['player3'] = request.form.get('player3')
        player_name_map['player4'] = request.form.get('player4')
        player_name_map['player5'] = request.form.get('player5')
        player_name_map['player6'] = request.form.get('player6')
        for key in player_name_map.keys():
            if player_name_map[key] != '':
                players_tonight.append(key)
                player_stash_map[key] = buy_in
        
        players_active = players_tonight.copy()
        print(f'from home(), form submitted, players set for tonight: {players_tonight}')
        print(player_name_map)
        print(player_stash_map)
        
        ''' we do the below regardless of who is playing tonight. That way, if someone
        is later removed from the night's lineup, when someone calls get_img()
        that someone's cards will be blank, no matter what is going on in the
        game or what stage things are at. I.e., this resets the now-missing
        player's cards to null, which would not have happened if you simply
        remove the player from the lineup (unless everyone clicks New Game).'''


    return render_template('home.html', async_mode=socketio.async_mode)

##########################################################################
### GAMES
##########################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    Draw   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/draw', methods = ['GET', 'POST'])
def draw_play():
    # makes sure that the game starts from scratch if it was 
    # left in a state stage != []
    draw.stage.clear()
    return render_template('draw.html', names = player_name_map)

@app.route('/link_to_draw')
def redirect_to_draw():
    # start_new_game() # this causes error
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]    
    return redirect(url_for('draw_play', player=requesting_player))

# special function draw poker and spit to register discards for each
# player
@socketio.on('draw_cards_draw', namespace='/test')
def draw_cards_draw(message):
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print('hold statuses: ', message['data'])
    hold_statuses = [message['data']['card1'], message['data']['card2'], 
                     message['data']['card3'], message['data']['card4'], 
                     message['data']['card5']]
    if requesting_player == 'player1':        
        # 1. Show card backs to player for cards selected to discard
        # as he/she waits for the dealer to deal the draw
        for i in range(len(cards_player1_pg['player1'])):
            if hold_statuses[i] == False:                
                cards_player1_pg['player1'][i] = None
        emit('get_cards',  {'cards': cards_player1_pg}, room=room_map['player1'])
        
        # 2. register the cards s/he wants drawn in draw.py
        draw.draw_card_idxs['player1'] = hold_statuses
    elif requesting_player == 'player2':
        for i in range(len(cards_player2_pg['player2'])):
            if hold_statuses[i] == False:                
                cards_player2_pg['player2'][i] = None
        emit('get_cards',  {'cards': cards_player2_pg}, room=room_map['player2'])
        draw.draw_card_idxs['player2'] = hold_statuses
    elif requesting_player == 'player3':
        for i in range(len(cards_player3_pg['player3'])):
            if hold_statuses[i] == False:                
                cards_player3_pg['player3'][i] = None
        emit('get_cards',  {'cards': cards_player3_pg}, room=room_map['player3'])
        draw.draw_card_idxs['player3'] = hold_statuses
    elif requesting_player == 'player4':
        for i in range(len(cards_player4_pg['player4'])):
            if hold_statuses[i] == False:                
                cards_player4_pg['player4'][i] = None
        emit('get_cards',  {'cards': cards_player4_pg}, room=room_map['player4'])
        draw.draw_card_idxs['player4'] = hold_statuses
    elif requesting_player == 'player5':
        for i in range(len(cards_player5_pg['player5'])):
            if hold_statuses[i] == False:                
                cards_player5_pg['player5'][i] = None
        emit('get_cards',  {'cards': cards_player5_pg}, room=room_map['player5'])
        draw.draw_card_idxs['player5'] = hold_statuses
    elif requesting_player == 'player6':
        for i in range(len(cards_player6_pg['player6'])):
            if hold_statuses[i] == False:                
                cards_player6_pg['player6'][i] = None
        emit('get_cards',  {'cards': cards_player6_pg}, room=room_map['player6'])
        draw.draw_card_idxs['player6'] = hold_statuses
    # this broadcasts the message to everybody how many cards the requesting player took
    emit('who_drew_what',
                      {'data': 5-sum(hold_statuses), 
                       'player': player_name_map[requesting_player] + ' takes '},
                       broadcast=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    Spit   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
@app.route('/spit', methods = ['GET', 'POST'])
def spit_play():
    # makes sure that the game starts from scratch if it was 
    # left in a state stage != []
    spit.stage.clear()
    return render_template('spit_in_the_ocean.html', names = player_name_map)

@app.route('/link_to_spit')
def redirect_to_spit():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]  
    return redirect(url_for('spit_play', player=requesting_player))

@socketio.on('draw_cards_spit', namespace='/test')
def draw_cards_spit(message):
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print('hold statuses: ', message['data'])
    hold_statuses = [message['data']['card1'], message['data']['card2'], 
                     message['data']['card3'], message['data']['card4'], 
                     message['data']['card5']]
    if requesting_player == 'player1':
        # 1. Show card backs to player for cards selected to discard
        # as he/she waits for the dealer to deal the draw
        for i in range(len(cards_player1_pg['player1'])):
            if hold_statuses[i] == False:                
                cards_player1_pg['player1'][i] = None
        emit('get_cards',  {'cards': cards_player1_pg}, room=room_map['player1'])
        
        # 2. register the cards s/he wants drawn in draw.py
        spit.draw_card_idxs['player1'] = hold_statuses
    elif requesting_player == 'player2':
        for i in range(len(cards_player2_pg['player2'])):
            if hold_statuses[i] == False:                
                cards_player2_pg['player2'][i] = None
        emit('get_cards',  {'cards': cards_player2_pg}, room=room_map['player2'])
        spit.draw_card_idxs['player2'] = hold_statuses
    elif requesting_player == 'player3':
        for i in range(len(cards_player3_pg['player3'])):
            if hold_statuses[i] == False:                
                cards_player3_pg['player3'][i] = None
        emit('get_cards',  {'cards': cards_player3_pg}, room=room_map['player3'])
        spit.draw_card_idxs['player3'] = hold_statuses
    elif requesting_player == 'player4':
        for i in range(len(cards_player4_pg['player4'])):
            if hold_statuses[i] == False:                
                cards_player4_pg['player4'][i] = None
        emit('get_cards',  {'cards': cards_player4_pg}, room=room_map['player4'])
        spit.draw_card_idxs['player4'] = hold_statuses
    elif requesting_player == 'player5':
        for i in range(len(cards_player5_pg['player5'])):
            if hold_statuses[i] == False:                
                cards_player5_pg['player5'][i] = None
        emit('get_cards',  {'cards': cards_player5_pg}, room=room_map['player5'])
        spit.draw_card_idxs['player5'] = hold_statuses
    elif requesting_player == 'player6':
        for i in range(len(cards_player6_pg['player6'])):
            if hold_statuses[i] == False:                
                cards_player6_pg['player6'][i] = None
        emit('get_cards',  {'cards': cards_player6_pg}, room=room_map['player6'])
        spit.draw_card_idxs['player6'] = hold_statuses
    # this broadcasts the message to everybody how many cards the requesting player took
    emit('who_drew_what',
                      {'data': 5-sum(hold_statuses), 
                       'player': player_name_map[requesting_player] + ' takes '},
                       broadcast=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    5-card stud   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/five_card_stud', methods = ['GET', 'POST'])
def five_card_play():
    # makes sure that the game starts from scratch if it was 
    # left in a state stage != []
    five_card_stud.stage.clear()    
    return render_template('five_card_stud.html', names = player_name_map)

@app.route('/link_to_five_card_stud')
def redirect_to_five_card_stud():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'msg from link_to_five_card_stud(): requesting_player is {requesting_player}')
    return redirect(url_for('five_card_play', player=requesting_player))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     omaha     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/omaha', methods = ['GET', 'POST'])
def omaha_play():
    # makes sure that the game starts from scratch if it was 
    # left in a state stage != []
    omaha.stage.clear()
    return render_template('omaha.html', names = player_name_map)

@app.route('/link_to_omaha')
def redirect_to_omaha():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'msg from link_to_omaha(): requesting_player is {requesting_player}')
    return redirect(url_for('omaha_play', player=requesting_player))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     7-card stud     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/seven_card_stud', methods = ['GET', 'POST'])
def seven_card_play():
    seven_card_stud.stage.clear()
    return render_template('seven_card_stud.html', names = player_name_map)

@app.route('/link_to_seven_card')
def redirect_to_seven_card_stud():
     http_ref = request.environ['HTTP_REFERER']
     requesting_player = http_ref[http_ref.find('player=')+7:]
     print(f'msg from redirect_to_seven_card(): requesting_player is {requesting_player}')
     return redirect(url_for('seven_card_play', player=requesting_player))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    Monty   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/monty', methods = ['GET', 'POST'])
def monty_play():   
    monty.stage.clear()
    return render_template('monty.html', names = player_name_map)

@app.route('/link_to_monty')
def redirect_to_monty():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    return redirect(url_for('monty_play', player=requesting_player))

@socketio.on('reveal_monty', namespace='/test')
def reveal_monty():
    emit('show_monty',  {'cards': hands['monty']}, broadcast=True)

@socketio.on('monty_drop', namespace='/test')
def monty_drop():
    print('\nfrom monty_drop() fn:')
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'{requesting_player} wants to drop.')
    monty.drop_dict[requesting_player] = 'drop'
    monty_fold_hand = [monty.card_back] * 3
    emit('monty_drop', {'cards': monty_fold_hand}, room=room_map[requesting_player])
    
@socketio.on('monty_stay', namespace='/test')
def monty_stay():
    global hands
    print('\nfrom monty_stay() fn:')
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'{requesting_player} wants to stay.')
    monty.drop_dict[requesting_player] = ''
    monty_keep_hand = hands[requesting_player]
    emit('monty_drop', {'cards': monty_keep_hand}, room=room_map[requesting_player])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     omaha     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/holdem', methods = ['GET', 'POST'])
def holdem_play():
    # makes sure that the game starts from scratch if it was 
    # left in a state stage != []
    holdem.stage.clear()
    return render_template('holdem.html', names = player_name_map)

@app.route('/link_to_holdem')
def redirect_to_holdem():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'msg from redirect_to_holdem(): requesting_player is {requesting_player}')
    return redirect(url_for('holdem_play', player=requesting_player))


##########################################################################
### DEAL
##########################################################################

@socketio.on('deal', namespace='/test')
def deal_click():  
    global hands
    global players_active
    global max_bet    
    global round_bets
    global pot_claimed
    global has_bet_this_round
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print('\ndeal_click() got called!')
    
    # logic for making sure everyone bet in previous round before continuing
    has_bet_set = set(has_bet_this_round)
    players_active_set = set(players_active)
    
    # before allowing a deal event, we'll to check that all active players' 
    # accounts are up to date. If not, dealer will get an alert message.
    # Monty is more complicated once the game gets going, so skipping for now
    # Hold 'em is also more complicated, so needs a clause to omit first round in
    # this validation.
    def enforce_call_equity():
        if 'monty' in http_ref: # no call validation
            return 'continue_deal'
        if 'holdem' in http_ref and len(holdem.stage) == 0: # no call validation bec of blinds
            print('from validate_call_equity, holdem.stage = 0, pot_claimed = ', pot_claimed)
            return 'continue_deal'   
        if has_bet_set == players_active_set:
            # create a new dict of bets of just the active players
            active_player_round_bets = {}
            for p in players_active:
                active_player_round_bets[p] = round_bets[p]
            print('here are the current active player bets:', active_player_round_bets)
            if list(active_player_round_bets.values()) != [max(active_player_round_bets.values())] *len(players_active):                        
                players_no_call = []
                for p in active_player_round_bets.keys():
                    if active_player_round_bets[p] < max(active_player_round_bets.values()):
                        players_no_call.append(p)
                for i in range(len(players_no_call)):
                    # get the players actual names.
                    players_no_call[i] = player_name_map[players_no_call[i]]
                # emit a message that someone is under call amt
                emit('bets_needed_alert', {'negligent_bettors': players_no_call, 'fault_type': 'no_call'}, 
                     room=room_map[requesting_player])            
                return 'no_deal'
            else:
                return 'continue_deal'
        else: # emit a message that triggers an alert to the dealer that someone hasn't bet
            if len(players_active_set) == 0:
                return 'continue_deal'
            if len(has_bet_set) > 0:
                players_no_bet = list(players_active_set - has_bet_set)
                for i in range(len(players_no_bet)):
                    # get the players actual names.
                    players_no_bet[i] = player_name_map[players_no_bet[i]]
                emit('bets_needed_alert', {'negligent_bettors': players_no_bet, 'fault_type': 'no_bet'}, 
                     room=room_map[requesting_player])
                return 'no_deal'
    vce = enforce_call_equity()
    if vce == 'no_deal':
        return

    # if all is well so far, reset everybody's round bet value to 0
    round_bets_tmp = round_bets.copy()
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    has_bet_this_round_tmp = has_bet_this_round.copy() # for holdem, can't reset this after first round
    has_bet_this_round.clear()
    max_bet = 0  # reset the call amount
    if 'holdem' in http_ref:        
        print(f'Game is Hold \'em, boys. stage = {holdem.stage}; max_bet is {max_bet}')
        if len(holdem.stage) == 0: # re-activate all tonight's players
            if pot_claimed == False:
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            # we disable the validation in this if clause to allow deal to start even
            # if pot_claimed == False. We just don't want to allow a new game to start.
            #if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
            #    emit('money_left_alert', {}, room=room_map[requesting_player]) 
            #    return None            
            players_active = players_tonight.copy()
            emit('clear_log',{}, broadcast = True)  # clear the msg area
        hands = holdem.deal(players_active)
        pg1_tmp = holdem.get_display(hands, 'player1')
        pg2_tmp = holdem.get_display(hands, 'player2')
        pg3_tmp = holdem.get_display(hands, 'player3')
        pg4_tmp = holdem.get_display(hands, 'player4')
        pg5_tmp = holdem.get_display(hands, 'player5')
        pg6_tmp = holdem.get_display(hands, 'player6') 
        pot_claimed = False
    if 'monty' in http_ref:
        print(f'Game is Monty, boys. stage = {monty.stage}')
        if len(draw.stage) == 0:
            # this is for the case when all players in monty drop. If that's the case
            # you'll see at the end of the deal_click() function we'll send a message.
            drops = 0
            for player in monty.drop_dict.keys():
                if monty.drop_dict[player] == 'drop':
                    drops += 1
            # the three lines below prevent players from accidentally starting a new game
            # without someone's claiming the previous pot. 
            
            # but for Monty, this won't work. Here we just enforce taking of the pot
            # when either new game is clicked or when trying to link to another game,
            # but do not enforce pot claiming before deal() is clicked even if len(stage)==0
            # since it always is for Monty.
            
            #if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
            #    emit('money_left_alert', {}, room=room_map[requesting_player]) 
            #    return None
            pot_claimed = False
            players_active = players_tonight.copy() # re-activate all tonight's players
            emit('clear_log',{}, broadcast = True)  # clear the msg area
            # pot_update(-pot_amount) # if beginning of game, clear pot amount. Nope--removes antes also
        hands = monty.deal(players_active)
        pg1_tmp = monty.get_display(hands, 'player1')              
        pg2_tmp = monty.get_display(hands, 'player2')
        pg3_tmp = monty.get_display(hands, 'player3')
        pg4_tmp = monty.get_display(hands, 'player4')
        pg5_tmp = monty.get_display(hands, 'player5')
        pg6_tmp = monty.get_display(hands, 'player6')
        
    if 'draw' in http_ref:
        print(f'Game is draw poker, boys. stage = {draw.stage}')
        if len(draw.stage) == 0:             
            # the three lines below prevent players from accidentally starting a new game
            # without someone's claiming the previous pot. 
            if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            pot_claimed = False
            players_active = players_tonight.copy() # re-activate all tonight's players
            emit('clear_log',{}, broadcast = True)  # clear the msg area
            # pot_update(-pot_amount) # if beginning of game, clear pot amount. Nope--removes antes also
        hands = draw.deal(players_active)
        pg1_tmp = draw.get_display(hands, 'player1')              
        pg2_tmp = draw.get_display(hands, 'player2')
        pg3_tmp = draw.get_display(hands, 'player3')
        pg4_tmp = draw.get_display(hands, 'player4')
        pg5_tmp = draw.get_display(hands, 'player5')
        pg6_tmp = draw.get_display(hands, 'player6')
    
    if 'spit' in http_ref:
        print(f'Game is spit in the ocean, boys. stage = {spit.stage}')
        if len(spit.stage) == 0: 
            if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            pot_claimed = False
            players_active = players_tonight.copy() # re-activate all tonight's players
            emit('clear_log',{}, broadcast = True)  # clear the msg area
            #pot_update(-pot_amount) # if beginning of game, clear pot amount
        hands = spit.deal(players_active)
        pg1_tmp = spit.get_display(hands, 'player1')
        pg2_tmp = spit.get_display(hands, 'player2')
        pg3_tmp = spit.get_display(hands, 'player3')
        pg4_tmp = spit.get_display(hands, 'player4')
        pg5_tmp = spit.get_display(hands, 'player5')
        pg6_tmp = spit.get_display(hands, 'player6')
        
    if 'five_card_stud' in http_ref:
        print(f'Game is 5-card stud, boys. stage = {five_card_stud.stage}; max_bet is {max_bet}')
        if len(five_card_stud.stage) == 0: 
            if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            pot_claimed = False
            players_active = players_tonight.copy() # re-activate all tonight's players
            emit('clear_log',{}, broadcast = True)  # clear the msg area
            #pot_update(-pot_amount) # if beginning of game, clear pot amount            
        hands = five_card_stud.deal(players_active)
        pg1_tmp = five_card_stud.get_display(hands, 'player1')
        pg2_tmp = five_card_stud.get_display(hands, 'player2')
        pg3_tmp = five_card_stud.get_display(hands, 'player3')
        pg4_tmp = five_card_stud.get_display(hands, 'player4')
        pg5_tmp = five_card_stud.get_display(hands, 'player5')
        pg6_tmp = five_card_stud.get_display(hands, 'player6')

    if 'seven_card_stud' in http_ref:
        print(f'Game is 7-card stud, boys. stage = {seven_card_stud.stage}; max_bet is {max_bet}')
        if len(seven_card_stud.stage) == 0: 
            if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            pot_claimed = False
            players_active = players_tonight.copy() # re-activate all tonight's players
            emit('clear_log',{}, broadcast = True)  # clear the msg area
        hands = seven_card_stud.deal(players_active)
        pg1_tmp = seven_card_stud.get_display(hands, 'player1')
        pg2_tmp = seven_card_stud.get_display(hands, 'player2')
        pg3_tmp = seven_card_stud.get_display(hands, 'player3')
        pg4_tmp = seven_card_stud.get_display(hands, 'player4')
        pg5_tmp = seven_card_stud.get_display(hands, 'player5')
        pg6_tmp = seven_card_stud.get_display(hands, 'player6')
    
    if 'omaha' in http_ref:        
        print(f'Game is Omaha, boys. stage = {omaha.stage}; max_bet is {max_bet}')
        if len(omaha.stage) == 0: # re-activate all tonight's players
            if pot_amount > 0 and pot_claimed==False : # disallow staring new game 
                emit('money_left_alert', {}, room=room_map[requesting_player]) 
                return None
            pot_claimed = False
            players_active = players_tonight.copy()
            emit('clear_log',{}, broadcast = True)  # clear the msg area  
        hands = omaha.deal(players_active)
        pg1_tmp = omaha.get_display(hands, 'player1')
        pg2_tmp = omaha.get_display(hands, 'player2')
        pg3_tmp = omaha.get_display(hands, 'player3')
        pg4_tmp = omaha.get_display(hands, 'player4')
        pg5_tmp = omaha.get_display(hands, 'player5')
        pg6_tmp = omaha.get_display(hands, 'player6')
        
    for key in pg1_tmp.keys():
        cards_player1_pg[key] = pg1_tmp[key]        
        cards_player2_pg[key] = pg2_tmp[key]        
        cards_player3_pg[key] = pg3_tmp[key]        
        cards_player4_pg[key] = pg4_tmp[key]        
        cards_player5_pg[key] = pg5_tmp[key]        
        cards_player6_pg[key] = pg6_tmp[key]
        
    # for draw and spit in the ocean, each player sees his cards in the middle,
    # to faciliate the draw UI approach. I'm also changing the cards in his
    # normal position on the table to blanks so it's not confusing.
   
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])
    
    # show everyone their current stash amt
    emit('stash_msg', {'stash_map': player_stash_map, 'buy_in': buy_in}, 
         broadcast=True)    
    
    emit('pot_msg', {'amt': pot_amount, 'call': max_bet}, broadcast=True) # broadcast pot update
   
    # clear everybody's bet log unless it's Hold 'em first round
    if 'holdem' in http_ref:
        if len(holdem.stage) > 0 and holdem.stage[0] == 'flop':            
            round_bets = round_bets_tmp.copy()
            has_bet_this_round = has_bet_this_round_tmp.copy()
            for player in players_active:
                emit('pot_msg', {'amt': pot_amount, 'call':  max(round_bets.values()) - round_bets[player]}, 
                     room=room_map[player]) # update active players' call amts
            return
    emit('clear_bet_log', broadcast=True)
    if 'monty' in http_ref:        
        # If everybody, drops, emit a message so they know to ante again, and dealer knows to deal again.        
        if len(players_active) == drops:
             emit('all_dropped_msg', broadcast=True)
             # clear the drop_dict
             monty.drop_dict.clear()

##########################################################################
### FOLD and REVEAL
##########################################################################
@socketio.on('fold', namespace='/test')
def fold():
    print(f'\nfrom fold(): request.eviron["HTTP_REFERER"]:{request.environ["HTTP_REFERER"]} ')
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'We thus conclude that {requesting_player} ({player_name_map[requesting_player]})' +
          ' wants to fold, so I will fold them!...')
    hand_len = len(hands[requesting_player])
    seven_card_stud.hands[requesting_player] = [seven_card_stud.card_back] * hand_len
    five_card_stud.hands[requesting_player] = [five_card_stud.card_back] * hand_len
    omaha.hands[requesting_player] = [omaha.card_back] * hand_len
    draw.hands[requesting_player] = [draw.card_back] * hand_len
    spit.hands[requesting_player] = [spit.card_back] * hand_len
    holdem.hands[requesting_player] = [holdem.card_back] * hand_len
    
    players_active.remove(requesting_player) # should add try/catch here in case player not in list
    if requesting_player in has_bet_this_round:
        has_bet_this_round.remove(requesting_player)
        
    cards_player1_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player2_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player3_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player4_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player5_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player6_pg[requesting_player] = [draw.card_back] * hand_len
    
    if 'draw' in http_ref or 'spit' in http_ref:  # for draw and spit we'll just blank out the display in the center
        if requesting_player == 'player1':
            cards_player1_pg['requesting_player'] = [None] * 5
        if requesting_player == 'player2':
            cards_player2_pg['requesting_player'] = [None] * 5
        if requesting_player == 'player3':
            cards_player3_pg['requesting_player'] = [None] * 5
        if requesting_player == 'player4':
            cards_player4_pg['requesting_player'] = [None] * 5
        if requesting_player == 'player5':
            cards_player5_pg['requesting_player'] = [None] * 5
        if requesting_player == 'player6':
            cards_player6_pg['requesting_player'] = [None] * 5
    
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])
    emit('who_folded',{'player': player_name_map[requesting_player] + ' folded.'},
                       broadcast=True)
    # include the player folds msg in the bet log also
    emit('bet_msg',{'player':  player_name_map[requesting_player], 
                    'player_by_number':requesting_player, 'fold': True},
                       broadcast=True) # broadcast latest player's bet
    # if all but one have folded, remaining player wins; push pot amount to him/her
    if len(players_active) == 1:
        winner_player_number = players_active[0]
        winning_player = player_name_map[winner_player_number]
        emit('all_folded_msg', {'winner': winning_player}, broadcast=True)
        claim_pot(default_winner=winner_player_number)

@socketio.on('reveal', namespace='/test')
def reveal_cards():
    global reveal_players_monty
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'\nreveal_cards() got called...')
    
    # REVEAL in Monty means something different from in the other games:
    # here it is the dealer's right to reveal the cards of everyone 
    # who holds, to everyone playing.
    if 'monty' in http_ref:
        print('"REVEAL" for all holders in Monty has been invoked')
        print(f'contents of monty.hold_dict: {monty.hold_dict}')
        for player in monty.hold_dict.keys(): 
            print(f'value for monty.hold_dict[{player}] is {monty.hold_dict[player]}')
            if monty.hold_dict[player] == 'hold':
                cards_player1_pg[player] = hands[player]
                cards_player2_pg[player] = hands[player]
                cards_player3_pg[player] = hands[player]
                cards_player4_pg[player] = hands[player]
                cards_player5_pg[player] = hands[player]
                cards_player6_pg[player] = hands[player]
            else:
                print(f'{player} does not want to hold')  
        print(f'from reveal_cards(), reveal_players_monty = {reveal_players_monty}')
                    
    else:
        print(f'...we thus conclude that {requesting_player} ({player_name_map[requesting_player]})' +
              ' wants to reveal their cards.')
        cards_player1_pg[requesting_player] = hands[requesting_player]        
        cards_player2_pg[requesting_player] = hands[requesting_player]
        cards_player3_pg[requesting_player] = hands[requesting_player]
        cards_player4_pg[requesting_player] = hands[requesting_player]
        cards_player5_pg[requesting_player] = hands[requesting_player]
        cards_player6_pg[requesting_player] = hands[requesting_player]
        if requesting_player == 'player1':
            cards_player1_pg['player1'] = hands['player1']
        if requesting_player == 'player2':
            cards_player2_pg['player2'] = hands['player2']
        if requesting_player == 'player3':
            cards_player3_pg['player3'] = hands['player3']
        if requesting_player == 'player4':
            cards_player4_pg['player4'] = hands['player4']
        if requesting_player == 'player5':
            cards_player5_pg['player5'] = hands['player5']
        if requesting_player == 'player6':
            cards_player6_pg['player6'] = hands['player6']
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])

##########################################################################
### New Game
##########################################################################
@socketio.on('new_game', namespace='/test')
def start_new_game():
    global max_bet
    global round_bets
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    if pot_amount > 0: # and pot_claimed==False: # disallow staring new game 
        emit('money_left_alert', {}, room=room_map[requesting_player]) 
        return None
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    max_bet = 0
    print('\n start_new_game() has been called.')
    http_ref = request.environ['HTTP_REFERER']
    #no need to clear pot amount anymore, since if it's > 0, cannot have gotten this far
    emit('pot_msg', {'amt': pot_amount, 'call': max_bet}, broadcast=True) # broadcast pot update

    for key in cards_player1_pg.keys():
        cards_player1_pg[key] = []
        cards_player2_pg[key] = []
        cards_player3_pg[key] = []
        cards_player4_pg[key] = []
        cards_player5_pg[key] = []
        cards_player6_pg[key] = []
    # What game is asking for a new hand:
    if 'draw' in http_ref:        
        draw.new_game(players = players_tonight)    
    elif 'five_card_stud' in http_ref:
        five_card_stud.new_game(players = players_tonight)
    elif 'seven_card' in http_ref:
        seven_card_stud.new_game(players = players_tonight)
    elif 'omaha' in http_ref:
        omaha.new_game(players = players_tonight)
    elif 'monty' in http_ref:
        monty.new_game(players = players_tonight)
    elif 'spit' in http_ref:
        spit.new_game(players = players_tonight)        
        cards_player1_pg['spit'] = None
        cards_player2_pg['spit'] = None       
        cards_player3_pg['spit'] = None
        cards_player4_pg['spit'] = None
        cards_player5_pg['spit'] = None 
        cards_player6_pg['spit'] = None
    elif 'holdem' in http_ref:
        holdem.new_game(players = players_tonight)

    emit('clear_bet_log', broadcast=True)
        
    ### Have to clear everybody's cards for display
    ### It's fine if not all these players are active
    print('here are the keys in cards_player1_pg: ',  cards_player1_pg.keys())
   
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])
    
    emit('clear_log',{}, broadcast = True)

@socketio.on('change_game', namespace='/test')
def change_game(new_game):
    print('change_game(new_game) got called on the server, argument passed; ', new_game['new_game'])
    emit('redirect_all_players', {'new_game': new_game['new_game']}, broadcast = True)
##########################################################################
### Betting Handlers
##########################################################################

@socketio.on('bet_receive', namespace='/test')
def receive_bet(message):
    global max_bet
    global round_bets
    global has_bet_this_round
    global pot_claimed
    global players_active
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    
    # first let's make sure the player is allowed to bet, IOW, hasn't folded
    if requesting_player in players_active:
        bet_allowed = True # this is a dummy that does nothing
    else: # disallow bet: send window alert to client, return out of receive_bet()
        emit('illegal_bet_alert', {}, room = room_map[requesting_player])
        return
    has_bet_this_round.append(requesting_player)
    amt = int(message['amt'])
    # first let's validate bet to ensure player is not entering a negative amt
    # that is larger magnitude that what he's bet. Negative amounts are allowed to 
    # correct input errors, but not to get "free money."
    player_tot_bet = round_bets[requesting_player]
    if amt < 0 and abs(amt) > player_tot_bet:
        print(f'{requesting_player} just tried to take out more from the pot than he put in: {amt}')
        emit('hand_in_till', {'err': 'error code 212: Your hand in till. Can\'t take out more than you put in'},
             room=room_map[requesting_player])
        return None
    
    pot_update(amt=amt) # update the pot total
    round_bets[requesting_player] += amt # update the record for this player for this betting round
    max_bet = max(round_bets.values()) #the max that anyone has bet in a round is the call amount
    print(f'{requesting_player} just bet ${amt}.')
    
    # decrement player's stash, and send new stash amount to the player
    player_stash_map[requesting_player] = player_stash_map[requesting_player] - int(amt)
    emit('stash_msg', {'stash_map': player_stash_map, 'buy_in': buy_in}, 
         broadcast=True)
    # hold em gets its own bet logic
    if 'holdem' in http_ref:
        print('from receive_bet(), holdem.stage: ', holdem.stage)
        if len(holdem.stage) == 0:
            if pot_claimed == True:
                holdem_stage = 0
            else:
                holdem_stage = 'river' # this is just a guess
            #pot_claimed = False # normally we do this in deal_click() but we want to do it
                                # after the blinds are placed because otherwise we lose track
                                # of who placed the blinds.
        else:
            holdem_stage = holdem.stage
        emit('bet_msg',{'player':  player_name_map[requesting_player], 
                    'player_by_number':requesting_player, 'amt': amt, 
                    'fold': 'no', 'stage': holdem_stage},
                       broadcast=True) # broadcast latest player's bet
        for player in players_tonight:
            if len(holdem.stage) == 0 and pot_claimed == True:
                call_amt = 0
            else:
                call_amt = max_bet - round_bets[player]
            emit('pot_msg', {'amt': pot_amount, 'call': call_amt}, 
                     room=room_map[player]) # update active players' call amts
        return
    
    emit('bet_msg',{'player':  player_name_map[requesting_player], 
                    'player_by_number':requesting_player, 'amt': amt, 'fold': 'no'},
                       broadcast=True) # broadcast latest player's bet
    for player in players_tonight:
        if player in players_active:
            emit('pot_msg', {'amt': pot_amount, 'call': max_bet - round_bets[player]}, 
                 room=room_map[player]) # update active players' call amts
        else:
            emit('pot_msg', {'amt': pot_amount, 'call': 0}, 
                 room=room_map[player]) # update folded players' call amts
    

@socketio.on('claim_pot', namespace='/test')
def claim_pot(default_winner = None):
    global max_bet
    global round_bets
    global pot_claimed
    global players_active
    max_bet = 0
    pot_claimed = True
    has_bet_this_round.clear()
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]

    if default_winner != None: # this occurs when all players but one fold. Push the pot to remaining player.
        requesting_player = default_winner
    player_stash_map[requesting_player] = player_stash_map[requesting_player] + int(pot_amount)
    
    # if a pot is claimed the game is over, whether or not the game has been
    # dealt to completion, so reset stage of all games
    draw.stage.clear()
    five_card_stud.stage.clear()
    omaha.stage.clear()
    spit.stage.clear()
    monty.stage.clear()
    holdem.stage.clear()
        
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    pot_tmp = pot_amount
    pot_update(-pot_amount) # clear pot amount
     # show everyone the winner's increased stash
    emit('stash_msg', {'stash_map': player_stash_map, 'buy_in': buy_in}, 
         broadcast=True)
    
        
    emit('pot_msg', {'amt': pot_amount, 'call': max_bet}, 
         broadcast=True) # broadcast pot update
    # In Monty, it's nice to have a record of how much the winner just took, for matching.
    if 'monty' in http_ref:
        emit('pot_msg', {'amt': pot_amount, 'call': max_bet, 'winner': player_name_map[requesting_player],
                'winnings': pot_tmp}, broadcast=True) # broadcast pot update
        
    # Without doing this here, if an ante is entered in the next game,
    # pre-deal, players who folded in previous game won't see the pot amt when
    # they ante. Not crucial, but it will feel a little weird to them not to see the pot.
    players_active = players_tonight.copy()
    # the following are for logging purposes: will print to online log files and can then
    # retrieve at the end of the evening or later to get the player stashes
    print(f'\n{requesting_player} has just claimed the pot.')
    print(f'player_stash_map: {player_stash_map}')
    print(f'player_name_map: {player_name_map}')

##########################################################################
### Connection Handlers
##########################################################################
@socketio.on('my_event', namespace='/test')
def test_message(message):
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    client_sid = request.sid
    if 'player' in message.keys():
        player = message['player']
    elif len(requesting_player) == 7: # assume query string data is working right
        player = requesting_player
    else:
        player = ''
    update_room_map(player = player, client_sid = client_sid)
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('connect_msg',
         {'data': message['data'], 
          'player': player,
          'sid': client_sid})

@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    print(f'from join(), message[\'room\'] = {message["room"]}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('join_msg',
         {'data': 'you\'re in room  ' + ', '.join(rooms()),
          'count': ''})

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def connect_success():
    print('\ntest_connect() got called.')
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    client_sid = request.sid
    # when a client connects, grab it's sid and update the player-sid
    # map using also requesting_player captured from http_ref
    update_room_map(player = requesting_player, client_sid = client_sid)
    #global thread
    #with thread_lock:
    #   if thread is None:
    #       thread = socketio.start_background_task(background_thread)
    emit('connect_msg', {'data': 'Trying...', 
                         'player':requesting_player,
                         'sid': request.sid})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)
    
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=False) # debug=True doesn't work

    
