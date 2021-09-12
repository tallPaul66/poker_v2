const url_params = new URLSearchParams(window.location.search);

function chip_image_display(msg) {
    const player_name = url_params.get('player');
    var stash_map = msg.stash_map
    var buy_in = msg.buy_in
    // This prints each player's exact stash amount that only he/she can see.
    if (player_name == 'player1') {
        $('#player1_stash').text($('<div/>').text('$' + stash_map.player1).html());
    } else if (player_name == 'player2') {
        $('#player2_stash').text($('<div/>').text('$' + stash_map.player2).html());
    } else if (player_name == 'player3') {
        $('#player3_stash').text($('<div/>').text('$' + stash_map.player3).html());
    } else if (player_name == 'player4') {
        $('#player4_stash').text($('<div/>').text('$' + stash_map.player4).html());
    } else if (player_name == 'player5') {
        $('#player5_stash').text($('<div/>').text('$' + stash_map.player5).html());  
    }
    var players = Object.keys(stash_map)
    var chips_img0 = "static/card_pics/chips--6_stack_plus_2_small.png";
    var chips_img1 = "static/card_pics/chips--6_stack_small.png";
    var chips_img2 = "static/card_pics/chips--6_stack_minus_2_small.png" ;
    var chips_img3 = "static/card_pics/chips--6_stack_minus_4_small.png";
    var chips_img4 = "static/card_pics/chips--6_stack_minus_6_small.png";
    var chips_img5 = "static/card_pics/chips--6_stack_minus_7_small.png";
    var chips_img6 = "static/card_pics/chips--6_stack_minus_8_small.png";
    var chips_default = "static/card_pics/card_place_holder_img2_sm2.png";
    for (i=0; i<players.length; i++){
        player = players[i]                  
        switch(player){
            case "player1":
                switch(true){
                    case stash_map[player] > 1.4*buy_in:
                        document.getElementById('player1_stash_img').src = chips_img0;
                        break;
                    case stash_map[player] > 1.2*buy_in:                                    
                        document.getElementById('player1_stash_img').src = chips_img1;
                        break;
                    case stash_map[player] > buy_in:
                        document.getElementById('player1_stash_img').src = chips_img2
                        break;
                    case stash_map[player] > 0.8*buy_in:                                    
                        document.getElementById('player1_stash_img').src = chips_img3
                        break;
                    case stash_map[player] > 0.6*buy_in:
                        document.getElementById('player1_stash_img').src = chips_img4
                        break;
                    case stash_map[player] > 0.4*buy_in:
                        document.getElementById('player1_stash_img').src = chips_img5
                        break;
                    case stash_map[player] > 0.2*buy_in:
                        document.getElementById('player1_stash_img').src = chips_img6
                        break;
                    default:
                        document.getElementById('player1_stash_img').src = chips_default
                        break;
                }
            case "player2":
                switch(true){
                    case stash_map[player] > 1.4*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img0;
                        break;
                    case stash_map[player] > 1.2*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img1;
                        break;
                    case stash_map[player] > buy_in:
                        document.getElementById('player2_stash_img').src = chips_img2
                        break;
                    case stash_map[player] > 0.8*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img3
                        break;
                    case stash_map[player] > 0.6*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img4
                        break;
                    case stash_map[player] > 0.4*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img5
                        break;
                    case stash_map[player] > 0.2*buy_in:
                        document.getElementById('player2_stash_img').src = chips_img6
                        break;
                    default:
                        document.getElementById('player2_stash_img').src = chips_default
                        break;
                }
            case "player3":
                switch(true){
                    case stash_map[player] > 1.4*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img0;
                        break;
                    case stash_map[player] > 1.2*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img1;
                        break;
                    case stash_map[player] > buy_in:
                        document.getElementById('player3_stash_img').src = chips_img2
                        break;
                    case stash_map[player] > 0.8*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img3
                        break;
                    case stash_map[player] > 0.6*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img4
                        break;
                    case stash_map[player] > 0.4*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img5
                        break;
                    case stash_map[player] > 0.2*buy_in:
                        document.getElementById('player3_stash_img').src = chips_img6
                        break;
                    default:
                        document.getElementById('player3_stash_img').src = chips_default
                        break;
                }
            case "player4":
                switch(true){
                    case stash_map[player] > 1.4*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img0;
                        break;
                    case stash_map[player] > 1.2*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img1;
                        break;
                    case stash_map[player] > buy_in:
                        document.getElementById('player4_stash_img').src = chips_img2
                        break;
                    case stash_map[player] > 0.8*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img3
                        break;
                    case stash_map[player] > 0.6*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img4
                        break;
                    case stash_map[player] > 0.4*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img5
                        break;
                    case stash_map[player] > 0.2*buy_in:
                        document.getElementById('player4_stash_img').src = chips_img6
                        break;
                    default:
                        document.getElementById('player4_stash_img').src = chips_default
                        break;
                }
            case "player5":
                switch(true){
                    case stash_map[player] > 1.4*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img0;
                        break;
                    case stash_map[player] > 1.2*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img1;
                        break;
                    case stash_map[player] > buy_in:
                        document.getElementById('player5_stash_img').src = chips_img2
                        break;
                    case stash_map[player] > 0.8*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img3
                        break;
                    case stash_map[player] > 0.6*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img4
                        break;
                    case stash_map[player] > 0.4*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img5
                        break;
                    case stash_map[player] > 0.2*buy_in:
                        document.getElementById('player5_stash_img').src = chips_img6
                        break;
                    default:
                        document.getElementById('player5_stash_img').src = chips_default
                        break;
                }
        }
    }        
 }
 
function negligent_bettor_alert(msg) {
    var players = msg.negligent_bettors
    if(players.length==1){
        has_verb = "has"
        need_verb = "needs"
        owes_verb = "owes"
    } else {
        has_verb = "have"
        need_verb = "need"
        owes_verb = "owe"
    }
    var fault_type = msg.fault_type
    console.log('lenth of players', players.length)
    if(fault_type == "no_match"){
        //window.alert(players + " " + need_verb + " to match the pot.");
        var result = window.confirm(players + " " + need_verb + " to match the pot. You can " +
        "override and continue the deal by pressing \'OK\', otherwise click \'Cancel\'");
            if (result === true) {
                socket.emit('override_no_deal', {msg: 'override'});
            } 
    } else if(fault_type == "no_call"){
        //window.alert(players + " " + owes_verb + " money to the pot.");
        var result = window.confirm(players + " " + owes_verb + " money to the pot. You can " +
        "override and continue the deal by pressing \'OK\', otherwise click \'Cancel\'");
            if (result === true) {
                socket.emit('override_no_deal', {msg: 'override'});
            } 
    } else if (fault_type == "no_bet"){
        //window.alert(players + " " + has_verb + " not bet.");        
        var result = window.confirm(players + " " + has_verb + " not bet. You can " +
        "override and continue the deal by pressing \'OK\', otherwise click \'Cancel\'");
            if (result === true) {
                socket.emit('override_no_deal', {msg: 'override'});
            } 
    }
}
function check_pot(game) {
    if(pot_value != 0){
        window.alert("There's still money in the pot. Links won't work until it's claimed.");
    } 
    else if (game=='draw'){
         if(window.confirm("Take all players to Draw Poker?")){
             socket.emit('change_game', {new_game:'draw'})                     
         }                 
    } 
    else if (game=='fcs'){
         if(window.confirm("Take all players to Five Card Stud?")){
             socket.emit('change_game', {new_game:'fcs'})                     
         }
    } 
    else if (game=='scs'){
         if(window.confirm("Take all players to Seven Card Stud?")){
             socket.emit('change_game', {new_game:'scs'})                     
         }
    } 
    else if (game=='spit'){
         if(window.confirm("Take all players to Spit/Hootenanny?")){
             socket.emit('change_game', {new_game:'spit'})                     
         }
    } 
    else if (game=='omaha'){
         if(window.confirm("Take all players to Omaha?")){
             socket.emit('change_game', {new_game:'omaha'})                     
         }
    } 
    else if (game=='cross'){
         if(window.confirm("Take all players to Fiery Cross?")){
             socket.emit('change_game', {new_game:'cross'})                     
         }
    }
    else if (game=='monty'){
         if(window.confirm("Take all players to 3-Card Monty?")){
             socket.emit('change_game', {new_game:'monty'})                     
         }
    }
    else if (game=='holdem'){
         if(window.confirm("Take all players to Hold 'em?")){
             socket.emit('change_game', {new_game:'holdem'})                     
         }
    } 
    else {
        window.alert("from check_pot() function: The game selected is not associated with any link.");
    }
    return false;
}

function redirect_all(msg){
    const player_name = url_params.get('player');
    if(msg.new_game == 'draw'){
        window.location.href = "draw?player=" + player_name;
    } else if(msg.new_game == 'spit') {        
        window.location.href = "spit?player=" + player_name;
    } else if (msg.new_game=='fcs'){
        window.location.href = "five_card_stud?player=" + player_name;
    } else if (msg.new_game=='scs'){
        window.location.href = "seven_card_stud?player=" + player_name;
    } else if (msg.new_game=='monty'){
        window.location.href = "monty?player=" + player_name;
    } else if (msg.new_game=='holdem'){
        window.location.href = "holdem?player=" + player_name;
    } else if (msg.new_game=='omaha'){
        window.location.href = "omaha?player=" + player_name;
    } else if (msg.new_game=='cross'){
        window.location.href = "cross?player=" + player_name;
    }
} 

// this function writes values into the betting text box according to which icon player clicks
function writeNumbers(x, currency_factor){
    console.log('currency_factor', currency_factor)
    currency_factor = parseFloat(currency_factor);
    var y = parseFloat(x);    
    y = y*currency_factor;
    var txt = document.getElementById("bet_entered");
    var bet_amt = y;
    if(txt.value==""){ txt.value = 0 + bet_amt;}
    else {txt.value = parseFloat(txt.value) + bet_amt;}
}