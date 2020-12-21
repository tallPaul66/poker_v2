function chip_image_display(msg) {
    const url_params = new URLSearchParams(window.location.search);
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