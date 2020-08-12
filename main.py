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
import draw
import five_card_stud
import omaha 
# import seven_card_stud be sure to clear game stage in claim_pot()
# import monty be sure to clear game stage in claim_pot()
# import spit be sure to clear game stage in claim_pot()
    

#~~~~~~~~~~~~~~~~~~~ Config Stuff ~~~~~~~~~~~~~~~~~
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, ping_interval=10000, ping_timeout=25000) #,ping_interval=10, ping_timeout=60)
thread = None
thread_lock = Lock()
#~~~~~~~~~~~~~~~~~~~ Config Stuff ~~~~~~~~~~~~~~~~~
# global variables
players_tonight = []
possible_players = ['player1', 'player2', 'player3', 'player4', 'player5', 'player6']
player_name_map = {}
player_stash_map = {'player1':'', 'player2':'', 'player3':'', 'player4':'', 
             'player5':'', 'player6':''}
round_bets = {'player1':0, 'player2':0, 'player3':0, 'player4':0, 
             'player5':0, 'player6':0} # keep track of players' bets in a single round
pot_amount = 0
max_bet = 0

def pot_update(amt):
    amt = int(amt)
    global pot_amount
    global max_bet    
    if amt > max_bet: # increase call amt
        max_bet = amt
    pot_amount = pot_amount + amt
    
    

stash_default = 100
# games that require choices on the player's part beyond folding or staying in
choice_games = ['draw', 'monty', 'spit']

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

@app.route('/', methods=['GET', 'POST'])
def home(): 
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
                player_stash_map[key] = stash_default

        print('Using the text box entries:')
        print(f'from home(): form submitted, players set for tonight: {players_tonight}')
        print(player_name_map)
        print(player_stash_map)
        
        ''' we do the below regardless of who is playing tonight. That way, if someone
        is later removed from the night's lineup, when someone calls get_img()
        that someone's cards will be blank, no matter what is going on in the
        game or what stage things are at. I.e., this resets the now-missing
        player's cards to null, which would not have happened if you simply
        remove the player from the lineup (unless everyone clicks New Game).'''


    return render_template('home.html', async_mode=socketio.async_mode)

#~~~~~~~~~~~~~~ draw poker ~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/draw', methods = ['GET', 'POST'])
def draw_play():    
    return render_template('draw.html', names = player_name_map)

@app.route('/link_to_draw')
def redirect_to_draw():
    # start_new_game() # this causes error
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]    
    return redirect(url_for('draw_play', player=requesting_player))

# special function for the game of draw poker to register discards for each
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
        for i in range(len(cards_player1_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player1_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player1_pg}, room=room_map['player1'])
        
        # 2. register the cards s/he wants drawn in draw.py
        draw.draw_card_idxs['player1'] = hold_statuses
    elif requesting_player == 'player2':
        for i in range(len(cards_player2_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player2_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player2_pg}, room=room_map['player2'])
        draw.draw_card_idxs['player2'] = hold_statuses
    elif requesting_player == 'player3':
        for i in range(len(cards_player3_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player3_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player3_pg}, room=room_map['player3'])
        draw.draw_card_idxs['player3'] = hold_statuses
    elif requesting_player == 'player4':
        for i in range(len(cards_player4_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player4_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player4_pg}, room=room_map['player4'])
        draw.draw_card_idxs['player4'] = hold_statuses
    elif requesting_player == 'player5':
        for i in range(len(cards_player5_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player5_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player5_pg}, room=room_map['player5'])
        draw.draw_card_idxs['player5'] = hold_statuses
    elif requesting_player == 'player6':
        for i in range(len(cards_player6_pg['requesting_player'])):
            if hold_statuses[i] == False:                
                cards_player6_pg['requesting_player'][i] = None
        emit('get_cards',  {'cards': cards_player6_pg}, room=room_map['player6'])
        draw.draw_card_idxs['player6'] = hold_statuses
    # this broadcasts the message to everybody how many cards the requesting player took
    emit('who_drew_what',
                      {'data': 5-sum(hold_statuses), 
                       'player': player_name_map[requesting_player] + ' takes '},
                       broadcast=True)

#~~~~~~~~~~~~~~ FIVE-CARD STUD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/five_card_stud', methods = ['GET', 'POST'])
def five_card_play():     
    return render_template('five_card_stud.html', names = player_name_map)

@app.route('/link_to_five_card_stud')
def redirect_to_five_card_stud():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'msg from link_to_five_card_stud(): requesting_player is {requesting_player}')
    return redirect(url_for('five_card_play', player=requesting_player))

#~~~~~~~~~~~~~~~~~~~ OMAHA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/omaha', methods = ['GET', 'POST'])
def omaha_play():     
    return render_template('omaha.html', names = player_name_map)

@app.route('/link_to_omaha')
def redirect_to_omaha():
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'msg from link_to_omaha(): requesting_player is {requesting_player}')
    return redirect(url_for('omaha_play', player=requesting_player))

#~~~~~~~~~~~~~~ Functions and Handlers ~~~~~~~~~~~~~~~~~~~~~~~~~

@socketio.on('deal', namespace='/test')
def deal_click():  
    global hands
    global players_active
    global max_bet    
    global round_bets
    http_ref = request.environ['HTTP_REFERER']
    print(f'\ndeal_click() got called!')
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    
    if 'draw' in http_ref:
        max_bet = 0  # reset the call amount
        print(f'Game is draw poker, boys. stage = {draw.stage}')
        if len(draw.stage) == 0: # re-activate all tonight's players
            players_active = players_tonight.copy()
            emit('clear_log',{}, broadcast = True)  # clear the draw cards msg area
            pot_update(-pot_amount) # if beginning of game, clear pot amount
        hands = draw.deal(players_active)
        pg1_tmp = draw.get_display(hands, 'player1')
        pg2_tmp = draw.get_display(hands, 'player2')
        pg3_tmp = draw.get_display(hands, 'player3')
        pg4_tmp = draw.get_display(hands, 'player4')
        pg5_tmp = draw.get_display(hands, 'player5')
        pg6_tmp = draw.get_display(hands, 'player6')
        
    if 'five_card_stud' in http_ref:
        max_bet = 0  # reset the call amount
        print(f'\Game is 5-card stud, boys. stage = {five_card_stud.stage}; max_bet is {max_bet}')
        if len(five_card_stud.stage) == 0: # re-activate all tonight's players
            players_active = players_tonight.copy()
            emit('clear_log',{}, broadcast = True)  # clear the draw cards msg area
            pot_update(-pot_amount) # if beginning of game, clear pot amount            
        hands = five_card_stud.deal(players_active)
        pg1_tmp = five_card_stud.get_display(hands, 'player1')
        pg2_tmp = five_card_stud.get_display(hands, 'player2')
        pg3_tmp = five_card_stud.get_display(hands, 'player3')
        pg4_tmp = five_card_stud.get_display(hands, 'player4')
        pg5_tmp = five_card_stud.get_display(hands, 'player5')
        pg6_tmp = five_card_stud.get_display(hands, 'player6')
    
    if 'omaha' in http_ref:
        max_bet = 0  # reset the call amount
        print(f'Game is Omaha, boys. stage = {omaha.stage}; max_bet is {max_bet}')
        if len(omaha.stage) == 0: # re-activate all tonight's players
            players_active = players_tonight.copy()
            emit('clear_log',{}, broadcast = True)  # clear the draw cards msg area
            pot_update(-pot_amount) # if beginning of game, clear pot amount            
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
    if 'draw' in http_ref:
        if 'player1' in pg1_tmp.keys():
            cards_player1_pg['requesting_player'] = pg1_tmp['player1']
            cards_player1_pg['player1'] = [None]*5
        if 'player2' in pg2_tmp.keys():
            cards_player2_pg['requesting_player'] = pg2_tmp['player2']
            cards_player2_pg['player2'] = [None]*5
        if 'player3' in pg3_tmp.keys():
            cards_player3_pg['requesting_player'] = pg3_tmp['player3']
            cards_player3_pg['player3'] = [None]*5
        if 'player4' in pg4_tmp.keys():
            cards_player4_pg['requesting_player'] = pg4_tmp['player4']
            cards_player4_pg['player4'] = [None]*5
        if 'player5' in pg5_tmp.keys():
            cards_player5_pg['requesting_player'] = pg5_tmp['player5']
            cards_player5_pg['player5'] = [None]*5
        if 'player5' in pg5_tmp.keys():
            cards_player6_pg['requesting_player'] = pg6_tmp['player6']
            cards_player6_pg['player6'] = [None]*5
    
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])
    
    # show everyone their current stash amt
    emit('stash_msg', {'stash': player_stash_map['player1'], 'player': 'player1'}, 
         room=room_map['player1'])
    emit('stash_msg', {'stash': player_stash_map['player2'], 'player': 'player2'}, 
         room=room_map['player2'])
    emit('stash_msg', {'stash': player_stash_map['player3'], 'player': 'player3'}, 
         room=room_map['player3'])
    emit('stash_msg', {'stash': player_stash_map['player4'], 'player': 'player4'}, 
         room=room_map['player4'])
    emit('stash_msg', {'stash': player_stash_map['player5'], 'player': 'player5'}, 
         room=room_map['player5'])
    emit('stash_msg', {'stash': player_stash_map['player6'], 'player': 'player6'}, 
         room=room_map['player6'])
    
    emit('pot_msg', {'amt': pot_amount, 'max': max_bet}, broadcast=True) # broadcast pot update
    # clear everybody's bet log
    emit('clear_bet_log', broadcast=True)

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
    #seven_card_stud.hands[requesting_player] = [seven_card_stud.card_back] * hand_len
    five_card_stud.hands[requesting_player] = [five_card_stud.card_back] * hand_len
    omaha.hands[requesting_player] = [omaha.card_back] * hand_len
    draw.hands[requesting_player] = [draw.card_back] * hand_len
    #spit.hands[requesting_player] = [spit.card_back] * hand_len
    players_active.remove(requesting_player) # should add try/catch here in case player not in list
        
    cards_player1_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player2_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player3_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player4_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player5_pg[requesting_player] = [draw.card_back] * hand_len
    cards_player6_pg[requesting_player] = [draw.card_back] * hand_len
    
    if 'draw' in http_ref:  # for draw we'll just blank out the display in the center
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

@socketio.on('reveal', namespace='/test')
def reveal_cards():
    global reveal_players_monty
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    print(f'\nHey! reveal_cards() got called...')
    
    # REVEAL in Monty means something different from in the other games:
    # here it is the dealer's right to reveal the cards of everyone 
    # who holds, to everyone playing.
    if 'monty' in http_ref:
        reveal_players_monty = 1 # set the flag, for use in get_img()
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
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    max_bet = 0
    print('\n start_new_game() has been called.')
    http_ref = request.environ['HTTP_REFERER']
    pot_update(-pot_amount) # clear pot amount
    emit('pot_msg', {'amt': pot_amount, 'max': max_bet}, broadcast=True) # broadcast pot update
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
    emit('clear_bet_log', broadcast=True)
        
    ### Have to clear everybody's cards for display when "Update Cards" is called
    ### It's fine if not all these players are active
    for key in cards_player1_pg.keys():
        cards_player1_pg[key] = ()
        cards_player2_pg[key] = ()
        cards_player3_pg[key] = ()
        cards_player4_pg[key] = ()
        cards_player5_pg[key] = ()
        cards_player6_pg[key] = ()
    emit('get_cards', {'cards': cards_player1_pg}, room=room_map['player1'])
    emit('get_cards', {'cards': cards_player2_pg}, room=room_map['player2'])
    emit('get_cards', {'cards': cards_player3_pg}, room=room_map['player3'])
    emit('get_cards', {'cards': cards_player4_pg}, room=room_map['player4'])
    emit('get_cards', {'cards': cards_player5_pg}, room=room_map['player5'])
    emit('get_cards', {'cards': cards_player6_pg}, room=room_map['player6'])
    
    emit('clear_log',{}, broadcast = True)

##########################################################################
### Betting Handlers
##########################################################################

@socketio.on('bet_receive', namespace='/test')
def receive_bet(message):
    global max_bet
    global round_bets
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    amt = message['amt']
    pot_update(amt=amt) # update the pot total
    for key in round_bets.keys():
        if key == requesting_player:            
            round_bets[key] += int(amt)
    max_bet = max(round_bets.values()) #the max that anyone has betted in a round is the call amount
    print(f'{requesting_player} just bet ${amt}.')
    
    # decrement player's stash, and send new stash amount to the player
    player_stash_map[requesting_player] = player_stash_map[requesting_player] - int(amt)
    emit('stash_msg', {'stash': player_stash_map[requesting_player], 'player': requesting_player}, 
         room=room_map[requesting_player])
    
    emit('bet_msg',{'player':  player_name_map[requesting_player], 
                    'player_by_number':requesting_player, 'amt': amt},
                       broadcast=True) # broadcast latest player's bet
    for player in players_active:
        emit('pot_msg', {'amt': pot_amount, 'max': max_bet - round_bets[player]}, 
                 room=room_map[player]) # update each player's call amt
    

@socketio.on('claim_pot', namespace='/test')
def claim_pot():
    global max_bet
    global round_bets
    max_bet = 0
    http_ref = request.environ['HTTP_REFERER']
    requesting_player = http_ref[http_ref.find('player=')+7:]
    player_stash_map[requesting_player] = player_stash_map[requesting_player] + int(pot_amount)
    
    # if a pot is claimed the game is over, even if whether or not the game has been
    # dealt to completion, so reset stage of all games
    draw.stage.clear()
    five_card_stud.stage.clear()
    omaha.stage.clear()
    
    # show player his/her increased stash
    emit('stash_msg', {'stash': player_stash_map[requesting_player], 'player': requesting_player}, 
         room=room_map[requesting_player])
    round_bets = {x: 0 for x in round_bets.keys()} # clear out previous round bets
    pot_update(-pot_amount) # clear pot amount
    emit('pot_msg', {'amt': pot_amount, 'max': max_bet}, broadcast=True) # broadcast pot update

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
    socketio.run(app, host='0.0.0.0') #, debug=True) # debug=True doesn't work

    
