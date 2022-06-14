import pandas as pd
import numpy as np
import time
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def get_card(card, trump):
    suit = card[0]
    if suit == trump:
        order_of_cards = {1: '11', 2: '9', 3:'14', 4:'10', 5:'13', 6:'12', 7:'8', 8:'7'}
        for rank, number in order_of_cards.items():
            if card[1:] == number:
                return suit + str(rank)
    else:
        order_of_cards = {1: '14', 2: '10', 3:'13', 4:'12', 5:'11', 6:'9', 7:'8', 8:'7'}
        for rank, number in order_of_cards.items():
            if card[1:] == number:
                return suit + str(rank)

def transform_played_cards(played_cards, trump):
    if type(played_cards) == float:
        cards = np.nan
    elif type(played_cards) != list:
        cards = get_card(played_cards, trump)
    else:
        cards = []
        for card in played_cards:
            if card == '.':
                cards.append('.')
            else:
                card = get_card(card, trump)
                cards.append(card)
    return cards

def get_list_played_card(cards_played, list_of_hearts, list_of_diamonds, list_of_clubs, list_of_spades):
    if type(cards_played) != float and type(cards_played) != np.float64:
        for card in cards_played:
            suit = card[0]
            rank_card = int(card[1])
            if suit == 'h':
                list_of_hearts.append(rank_card)
            elif suit == 'r':
                list_of_diamonds.append(rank_card)
            elif suit == 'k':
                list_of_clubs.append(rank_card)
            else:
                list_of_spades.append(rank_card)    
    return list_of_hearts, list_of_diamonds, list_of_clubs, list_of_spades

def get_highest_card(list_of_cards):
    not_played_cards = [card for card in range(1,9) if card not in list_of_cards]
    second_highest_card = np.nan
    if not not_played_cards:
        highest_card = np.nan
    else:
        highest_card = str(not_played_cards[0])
        if len(not_played_cards) > 1:
            second_highest_card = str(not_played_cards[1])
    return highest_card, second_highest_card

def list_to_string(list): 
    if type(list) == float or type(list) == np.float64:
        string = np.nan
    elif len(list) == 0:
        string = np.nan
    else:
        string = list[0]
        for card in list[1:]: 
            string += ' ' + card   
    return string

def check_teammate_winning(rank_card1, suit_card1, rank_card2, suit_card2, rank_card3, suit_card3, trump):
    if type(suit_card3) == float:
        if suit_card1 == suit_card2:
            if rank_card1 < rank_card2:
                return 1
            else:
                return 0
        elif suit_card1 == trump:
            return 1
        elif suit_card2 == trump:
            return 0
        else:
            return 1
    else:
        if suit_card2 == trump:
            if suit_card1 == trump and suit_card3 == trump:
                if rank_card2 < rank_card1 and rank_card2 < rank_card3:
                    return 1
                else:
                    return 0
            elif suit_card1 == trump:
                if rank_card2 < rank_card1:
                    return 1
                else:
                    return 0
            elif suit_card3 == trump:
                if rank_card2 < rank_card3:
                    return 1
                else:
                    return 0
            else:
                return 1
        elif suit_card2 != suit_card1:
            return 0
        else:
            if suit_card3 == trump:
                return 0
            elif suit_card3 == suit_card1:
                if rank_card2 < rank_card1 and rank_card2 < rank_card3:
                    return 1
                else:
                    return 0
            else:
                if rank_card2 < rank_card1:
                    return 1
                else:
                    return 0

def get_center(center):
    if len(center) == 2:
        return center[0][0], int(center[0][1]), center[1][0], int(center[1][1]), np.nan, np.nan
    else:
        return center[0][0], int(center[0][1]), center[1][0], int(center[1][1]), center[2][0], int(center[2][1])

def check_higher_card(card, center, trump):
    if type(center) == float:
        return 1
    if len(center) == 1:
        if center[0][0] == card[0]:
            if card[1] < center[0][1]:
                return 1
        elif card[0] == trump:
            return 1
    elif len(center) == 2:
        if center[0][0] != card[0]:
            if card[0] == trump:
                if center[1][0] == trump:
                    if card[1] < center[1][1]:
                        return 1
                else:
                    return 1
        elif center[0][0] == center[1][0]:
            if card[1] < center[0][1] and card[1] < center[1][1]:
                return 1
        elif center[1][0] != trump:
            if card[1] < center[0][1]:
                return 1
    else:
        if center[0][0] != card[0]:
            if card[0] == trump:
                if center[1][0] == trump:
                    if center[2][0] == trump:
                        if card[1] < center[1][1] and card[1] < center[2][1]:
                            return 1
                elif center[2][0] == trump:
                    if card[1] < center[2][1]:
                        return 1
                else:
                    return 1
        elif center[0][0] == center[1][0] and center[0][0] == center[2][0]:
            if card[1] < center[0][1] and card[1] < center[1][1] and card[1] < center[2][1]:
                return 1
        elif center[0][0] == center[1][0]:
            if center[2][0] != trump:
                if card[1] < center[0][1] and card[1] < center[1][1]:
                    return 1
        elif center[0][0] == center[2][0]:
            if center[1][0] != trump:
                if card[1] < center[0][1] and card[1] < center[2][1]:
                    return 1
        elif center[1][0] != trump and center[2][0] != trump:
            if card[1] < center[0][1]:
                return 1                  
    return 0

def get_value(card, trump):
    if card[0] == trump:
        values = {'1': 20, '2':14, '3':11, '4':10, '5':4, '6':3, '7':0, '8':0}
        return values[card[1]]
    else:
        values = {'1': 11, '2':10, '3':4, '4':3, '5':2, '6':0, '7':0, '8':0}
        return values[card[1]]

def can_create_small_street(center, hand):
    street_making_cards = []
    if type(center) == float:
        return 0, street_making_cards
    if len(center) == 3:
        if center[0][0] == center[1][0] and center[0][0] == center[2][0]:
            numbers = []
            for card in center:
                numbers.append(int(card[1]))
            numbers.sort()
            if check_distance_numbers(numbers) != 0:
                needed_numbers = get_needed_number(numbers)
                for card in hand:
                    if card[0] == center[0][0]:
                        if int(card[1]) in needed_numbers:
                            street_making_cards.append(card)
        elif center[0][0] == center[1][0]:
            center = [center[0], center[1]]
        elif center[0][0] == center[2][0]:
            center = [center[0], center[2]]
    if len(center) == 2:
        if center[0][0] == center[1][0]:
            numbers = [int(center[0][1]), int(center[1][1])]
            numbers.sort()
            if check_distance_numbers(numbers) != 0:
                needed_numbers = get_needed_number(numbers)
                for card in hand:
                    if card[0] == center[0][0]:
                        if int(card[1]) in needed_numbers:
                            street_making_cards.append(card)
    if len(street_making_cards) > 0:
        return 1, street_making_cards
    return 0, street_making_cards              

def check_distance_numbers(numbers):
    if len(numbers) == 2:
        if numbers[1] - numbers[0] < 3:
            return 1
    elif len(numbers) == 3:
        if numbers[1] - numbers[0] < 3 or numbers[2] - numbers[1]:
            return 1
    return 0

def check_is_small_street(center):
    if type(center) == float:
        return 0
    if len(center) == 3:
        if center[0][0] == center[1][0] == center[2][0]:
            numbers = []
            for card in center:
                numbers.append(int(card[1]))
            numbers.sort()
            if numbers[1] - numbers[0] == 1 and numbers[2] - numbers[1] == 1:
                return 1
    return 0

def get_needed_number(numbers):
    needed_numbers = []
    if len(numbers) == 2:
        if numbers[1] - numbers[0] == 1:
            if numbers[0] != 1:
                needed_numbers.append(numbers[0] - 1)
            if numbers[1] != 8:
                needed_numbers.append(numbers[1] + 1)
        if numbers[1] - numbers[0] == 2:
            needed_numbers.append(numbers[0] + 1)
    else:
        if numbers[1] - numbers[0] == 1 and numbers[2] - numbers[1] == 1:
            if numbers[0] != 1:
                needed_numbers.append(numbers[0] - 1)
            if numbers[2] != 8:
                needed_numbers.append(numbers[2] + 1)
        elif numbers[1] - numbers[0] == 1:
            if numbers[0] != 1:
                needed_numbers.append(numbers[0] - 1)
            if numbers[1] != 8:
                needed_numbers.append(numbers[1] + 1)
        elif numbers[2] - numbers[1] == 1:
            if numbers[1] != 1:
                needed_numbers.append(numbers[1] - 1)
            if numbers[2] != 8:
                needed_numbers.append(numbers[2] + 1)
        
        if numbers[1] - numbers[0] == 2:
            needed_numbers.append(numbers[0] + 1)
        if numbers[2] - numbers[1] == 2:
            needed_numbers.append(numbers[1] + 1)
    needed_numbers = set(needed_numbers)
    needed_numbers = list(needed_numbers)
    return needed_numbers

def get_suit_player(card, center, suit_trump):
    suit_card = card[0]
    if type(center) == float:
        if suit_card == suit_trump:
            return '2'
        else:
            return '0'
    suit_first_card = center[0][0]
    if suit_card == suit_first_card:
        return '1'
    elif suit_card == suit_trump:
        return '2'
    else:
        return '0'

def get_turn(center):
    if type(center) == float:
        return '1'
    elif len(center) == 1:
        return '2'
    elif len(center) == 2:
        return '3'
    else:
        return '4'

def check_player_suit_hascolor(player_colors, suit):
    if suit == 'k':
        if player_colors[0] == '1':
            return 1
    elif suit == 'h':
        if player_colors[1] == '1':
            return 1
    elif suit == 'r':
        if player_colors[2] == '1':
            return 1
    else:
        if player_colors[3] == '1':
            return 1
    return 0

def check_possibility_to_win(center, hand, playablecardbits, trump):
    winning_cards = get_winning_cards(center, trump)
    suits = {0: 'k', 1: 'h', 2: 'r', 3: 's'}
    winning_cards_in_hand = []
    for i, card in enumerate(hand):
        if playablecardbits[i] == '1':
            for rank, suit in suits.items():
                if card[0] == suit:
                    if int(card[1]) in winning_cards[rank]:
                        winning_cards_in_hand.append(card)
    return winning_cards_in_hand

def get_winning_cards(center, trump):
    winning_cards = [[], [], [], []]
    suits = {0: 'k', 1: 'h', 2: 'r', 3: 's'}
    if center[0][0] != trump and center[1][0] != trump and center[2][0] != trump:
        number_to_beat = int(center[0][1])
        if center[1][0] == center[0][0]:
            if number_to_beat > int(center[1][1]):
                number_to_beat = int(center[1][1])
        if center[2][0] == center[0][0]:
            if number_to_beat > int(center[2][1]):
                number_to_beat = int(center[2][1])
        for rank, suit in suits.items():
            if suit == trump:
                for i in range(1,9):
                    winning_cards[rank].append(i)
            elif suit == center[0][0]:
                for i in range(1,9):
                    if i == number_to_beat:
                        break
                    winning_cards[rank].append(i)
    else:
        number_to_beat = 9
        if center[0][0] == trump:
            number_to_beat = int(center[0][1])
        if center[1][0] == trump:
            if number_to_beat > int(center[1][1]):
                number_to_beat = int(center[1][1])
        if center[2][0] == trump:
            if number_to_beat > int(center[2][1]):
                number_to_beat = int(center[2][1])
        for rank, suit in suits.items():
            for i in range(1,9):
                if suit == trump:
                    if i == number_to_beat:
                        break
                    winning_cards[rank].append(i)
    return winning_cards

def check_has_number(hand, suit, number_h, number_d, number_c, number_s):
    for card in hand:
        if card == '.':
            continue
        if suit == 'h':
            if card[1] == number_h:
                return 1
        elif suit == 'r':
            if card[1] == number_d:
                return 1
        elif suit == 'k':
            if card[1] == number_c:
                return 1
        else:
            if card[1] == number_s:
                return 1
    return 0

def check_card_still_in_game(center, number_h, number_d, number_c, number_s):
    if type(center) == float:
        return 1
    center = [center]
    suit = center[0][0]
    for card in center:
        if card[0] == suit:
            if suit == 'h':
                if card[1] == number_h:
                    return 0
            elif suit == 'r':
                if card[1] == number_d:
                    return 0
            elif suit == 'k':
                if card[1] == number_c:
                    return 0
            else:
                if card[1] == number_s:
                    return 0
    return 0

def get_suit_center(center, trump):
    if type(center) == float:
        return '0'
    elif center[0][0] == trump:
        return '1'
    else:
        return '2' 

def get_no_of_cards_suit(cards_played0, cards_played1, cards_played2, cards_played3):
    cards = {0: cards_played0, 1: cards_played1, 2: cards_played2, 3: cards_played3}
    no_h = no_d = no_c = no_s = 8
    for i in range(4):
        if type(cards[i]) == float or type(cards[i]) == np.float64:
            continue
        for card in cards[i]:
            suit = card[0]
            if suit == 'h':
                no_h -= 1
            elif suit == 'r':
                no_d -= 1
            elif suit == 'k':
                no_c -= 1
            else:
                no_s -= 1
    return no_h, no_d, no_c, no_s

def get_no_of_suits_in_hand(hand):
    no_h = no_d = no_c = no_s = 0
    for card in hand:
        if card == '.':
            continue
        suit = card[0]
        if suit == 'h':
            no_h += 1
        elif suit == 'r':
            no_d += 1
        elif suit == 'k':
            no_c += 1
        else:
            no_s += 1
    return no_h, no_d, no_c, no_s

def check_player_suit_nocards(suit, no_h_left, no_d_left, no_c_left, no_s_left, no_h_hand, no_d_hand, no_c_hand, no_s_hand):
    if suit == 'h':
        if no_h_left == no_h_hand:
            return 0
    elif suit == 'r':
        if no_d_left == no_d_hand:
            return 0
    elif suit == 'k':
        if no_c_left == no_c_hand:
            return 0
    else:
        if no_s_left == no_s_hand:
            return 0
    return 1

def Main(rotterdam_data):
    start_time = time.time() 
    trump = rotterdam_data['Troef'][0]

    rotterdam_data['Cards'] = [transform_played_cards(rotterdam_data['Cards'][0], trump)]
    rotterdam_data['Center'] = [transform_played_cards(rotterdam_data['Center'][0], trump)]
    rotterdam_data['CardsPlayed0'] = [transform_played_cards(rotterdam_data['CardsPlayed0'][0], trump)]
    rotterdam_data['CardsPlayed1'] = [transform_played_cards(rotterdam_data['CardsPlayed1'][0], trump)]
    rotterdam_data['CardsPlayed2'] = [transform_played_cards(rotterdam_data['CardsPlayed2'][0], trump)]
    rotterdam_data['CardsPlayed3'] = [transform_played_cards(rotterdam_data['CardsPlayed3'][0], trump)]

    is_winning = 0
    has_higher = 0
    teammate_has_played = 0
    can_win = 0
    cards_to_win = []
    center = rotterdam_data['Center'][0]
    suit_trump = rotterdam_data['Troef'][0]
    cards = rotterdam_data['Cards'][0]

    list_of_hearts = [] 
    list_of_diamonds = [] 
    list_of_clubs = []
    list_of_spades = []
    for i in range(4):
        list_of_hearts, list_of_diamonds, list_of_clubs, list_of_spades = get_list_played_card(rotterdam_data['CardsPlayed{}'.format(i)][0], list_of_hearts, list_of_diamonds, list_of_clubs, list_of_spades)

    first_h, second_h = get_highest_card(list_of_hearts)
    first_d, second_d = get_highest_card(list_of_diamonds)
    first_c, second_c = get_highest_card(list_of_clubs)
    first_s, second_s = get_highest_card(list_of_spades)

    player_turn = get_turn(rotterdam_data['Center'][0])
    
    no_h, no_d, no_c, no_s = get_no_of_cards_suit(rotterdam_data['CardsPlayed0'][0], rotterdam_data['CardsPlayed1'][0], rotterdam_data['CardsPlayed2'][0],rotterdam_data['CardsPlayed3'][0])
    h_in_hand, d_in_hand, c_in_hand, s_in_hand = get_no_of_suits_in_hand(rotterdam_data['Cards'][0])

    if player_turn != '1':
        if check_player_suit_nocards(center[0][0], no_h, no_d, no_c, no_s, h_in_hand, d_in_hand, c_in_hand, s_in_hand):
            rotterdam_data['Player1_has_suit'] = check_player_suit_hascolor(rotterdam_data['HasColor1'][0], center[0][0])
            rotterdam_data['Player2_has_suit'] = check_player_suit_hascolor(rotterdam_data['HasColor2'][0], center[0][0])
            rotterdam_data['Player3_has_suit'] = check_player_suit_hascolor(rotterdam_data['HasColor3'][0], center[0][0])
        else:
            rotterdam_data['Player1_has_suit'] = 0
            rotterdam_data['Player2_has_suit'] = 0
            rotterdam_data['Player3_has_suit'] = 0
        rotterdam_data['Has_highest_suit'] = check_has_number(rotterdam_data['Cards'][0], center[0][0], first_h, first_d, first_c, first_s)
        rotterdam_data['Has_second_highest_suit'] = check_has_number(rotterdam_data['Cards'][0], center[0][0], second_h, second_d, second_c, second_s)
    else:
        player1_suit_all.append(1)
        player2_suit_all.append(1)
        player3_suit_all.append(1)
        rotterdam_data['Has_highest_suit'] = 1
        rotterdam_data['Has_second_highest_suit'] = 1
    
    if check_player_suit_nocards(rotterdam_data['Troef'][0], no_h, no_d, no_c, no_s, h_in_hand, d_in_hand, c_in_hand, s_in_hand):
        rotterdam_data['Player1_has_trump'] = check_player_suit_hascolor(rotterdam_data['HasColor1'][0], rotterdam_data['Troef'][0])
        rotterdam_data['Player2_has_trump'] = check_player_suit_hascolor(rotterdam_data['HasColor2'][0], rotterdam_data['Troef'][0])
        rotterdam_data['Player3_has_trump'] = check_player_suit_hascolor(rotterdam_data['HasColor3'][0], rotterdam_data['Troef'][0])
    else:
        rotterdam_data['Player1_has_trump'] = 0
        rotterdam_data['Player2_has_trump'] = 0
        rotterdam_data['Player3_has_trump'] = 0

    if player_turn == '4':
        cards_to_win = check_possibility_to_win(rotterdam_data['Center'][0], rotterdam_data['Cards'][0], rotterdam_data['PlayableCardBits'][0], rotterdam_data['Troef'][0])
        if cards_to_win:
            can_win = 1

    if type(center) != float:
        if len(center) >= 2:
            suit_card1, rank_card1, suit_card2, rank_card2, suit_card3, rank_card3 = get_center(center)
            is_winning = check_teammate_winning(rank_card1, suit_card1, rank_card2, suit_card2, rank_card3, suit_card3, suit_trump)
            teammate_has_played = 1

    is_higher_cards = []
    lowest_value = 21
    highest_value = 0
    lowest_card = 10
    highest_card = 10
    for i, card in enumerate(cards):
        higher = 0
        if rotterdam_data['PlayableCardBits'][0][i] == '1':
            if card != '.':
                higher = check_higher_card(card, center, suit_trump)
                if higher == 1:
                    has_higher = 1
                value_card = get_value(card, suit_trump)
                if value_card < lowest_value:
                    lowest_value = value_card
                    lowest_card = i
                if value_card > highest_value:
                    highest_value = value_card
                    highest_card = i

        is_higher_cards.append(higher)
    
    list_lowest_card = [0 if x != lowest_card else 1 for x in range(8)]
    list_highest_card = [0 if x != highest_card else 1 for x in range(8)]
        
    create_street, cards_create_street = can_create_small_street(rotterdam_data['Center'][0], rotterdam_data['Cards'][0])

    rotterdam_data['Teammate_winning'] = is_winning
    rotterdam_data['Has_higher'] = has_higher
    rotterdam_data['Is_higher'] = [is_higher_cards]
    rotterdam_data['Is_lowest_value'] = [list_lowest_card]
    rotterdam_data['Is_highest_value'] = [list_highest_card]
    rotterdam_data['Teammate_played'] = teammate_has_played
    rotterdam_data['Player_turn'] = player_turn
    rotterdam_data['Can_create_street'] = create_street
    rotterdam_data['Cards_create_street'] = [cards_create_street]
    rotterdam_data['Can_win'] = can_win
    rotterdam_data['Cards_to_win'] = [cards_to_win]
    rotterdam_data['Highest_h'] =  first_h
    rotterdam_data['Second_h'] = second_h    
    rotterdam_data['Highest_d'] = first_d
    rotterdam_data['Second_d'] = second_d
    rotterdam_data['Highest_c'] = first_c
    rotterdam_data['Second_c'] = second_c
    rotterdam_data['Highest_s'] = first_s
    rotterdam_data['Second_s'] = second_s

    rotterdam_data['Asked_suit'] = get_suit_center(rotterdam_data['Center'][0], rotterdam_data['Troef'][0])
    rotterdam_data['No_h_left'] = no_h
    rotterdam_data['No_d_left'] = no_d
    rotterdam_data['No_c_left'] = no_c
    rotterdam_data['No_s_left'] = no_s
    rotterdam_data['No_h_hand'] = h_in_hand
    rotterdam_data['No_d_hand'] = d_in_hand
    rotterdam_data['No_c_hand'] = c_in_hand
    rotterdam_data['No_s_hand'] = s_in_hand

    list_of_bits = rotterdam_data['PlayableCardBits'].to_list()
    all_bits = []
    number_of_cards = []
    for bit in list_of_bits:
        bit = list(bit)
        number_of_available_cards = 0
        for number in bit:
            if number == '1':
                number_of_available_cards += 1
        all_bits.append(bit)
        number_of_cards.append(number_of_available_cards)
    rotterdam_data['PlayableCardBits'] = all_bits
    rotterdam_data['No_playable_cards'] = number_of_cards

    rotterdam_data['Center'] = list_to_string(center)
    rotterdam_data['CardsPlayed0'] = list_to_string(rotterdam_data['CardsPlayed0'.format(i)][0])
    rotterdam_data['CardsPlayed1'] = list_to_string(rotterdam_data['CardsPlayed1'.format(i)][0])
    rotterdam_data['CardsPlayed2'] = list_to_string(rotterdam_data['CardsPlayed2'.format(i)][0])
    rotterdam_data['CardsPlayed3'] = list_to_string(rotterdam_data['CardsPlayed3'.format(i)][0])
    rotterdam_data['Cards_create_street'] = list_to_string(rotterdam_data['Cards_create_street'][0])
    rotterdam_data['Cards_to_win'] = list_to_string(rotterdam_data['Cards_to_win'][0])

    original_cards_rotterdam = []
    for card in rotterdam_data['Cards'][0]:
        if card[0] != '.':
            original_cards_rotterdam.append(rotterdam_data['Cards'][0])

    rotterdam_data = rotterdam_data.set_index(['No_h_left', 'No_d_left', 'No_c_left', 'No_s_left', 'No_h_hand', 'No_d_hand', 'No_c_hand', 'No_s_hand', 'Asked_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 'Player2_has_trump', 'Player3_has_trump', 'Highest_h', 'Highest_d', 'Highest_c', 'Highest_s', 'Second_h', 'Second_d', 'Second_c', 'Second_s', 'Center','CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'Troef','Can_win', 'Cards_to_win', 'PlayCard', 'No_playable_cards', 'Teammate_winning', 'Teammate_played', 'Has_higher', 'Can_create_street', 'Cards_create_street', 'Player_turn', 'Has_highest_suit', 'Has_second_highest_suit']).apply(pd.Series.explode).reset_index()

    rotterdam_data = rotterdam_data[rotterdam_data['Cards'] != '.']

    rotterdam_data['Original_hand'] = original_cards_rotterdam
    rotterdam_data = rotterdam_data[rotterdam_data['PlayableCardBits'] == '1']
    rotterdam_data = rotterdam_data.reset_index(drop = True)

    is_card_that_creates_street = []
    suit_all_cards = []
    is_card_to_win_all = []
    player1_suit_all = rotterdam_data['Player1_has_suit']
    player1_suit_all = list(player1_suit_all)
    player2_suit_all = rotterdam_data['Player2_has_suit']
    player2_suit_all = list(player2_suit_all)
    player3_suit_all = rotterdam_data['Player3_has_suit']
    player3_suit_all = list(player3_suit_all)
    has_highest_suit_all = rotterdam_data['Has_highest_suit']
    has_highest_suit_all = list(has_highest_suit_all)
    is_highest_suit_all = []
    has_second_highest_suit_all = rotterdam_data['Has_second_highest_suit']
    has_second_highest_suit_all = list(has_second_highest_suit_all)
    is_second_highest_suit_all = []
    highest_card_still_in_game_all = []

    player_turn = rotterdam_data['Player_turn'][0]
    can_win = rotterdam_data['Can_win'][0]
    cards_to_win = rotterdam_data['Cards_to_win'][0]
    cards_create_street = rotterdam_data['Cards_create_street'][0]
    for index in rotterdam_data.index:
        creates_street = 0
        is_card_to_win = 0
        card = rotterdam_data['Cards'][index]

        if player_turn == '1':
            if player1_suit_all[index] == 1:
                player1_suit_all[index] = check_player_suit_hascolor(rotterdam_data['HasColor1'][0], card[0])
            if player2_suit_all[index] == 1:
                player2_suit_all[index] = check_player_suit_hascolor(rotterdam_data['HasColor2'][0], card[0])
            if player3_suit_all[index] == 1:
                player3_suit_all[index] = check_player_suit_hascolor(rotterdam_data['HasColor3'][0], card[0])
            has_highest_suit_all[index] = check_has_number(rotterdam_data['Original_hand'][0], card[0], rotterdam_data['Highest_h'][0], rotterdam_data['Highest_d'][0], rotterdam_data['Highest_c'][0], rotterdam_data['Highest_s'][0])
            has_second_highest_suit_all[index] = check_has_number(rotterdam_data['Original_hand'][0], card[0], rotterdam_data['Second_h'][0], rotterdam_data['Second_d'][0], rotterdam_data['Second_c'][0], rotterdam_data['Second_s'][0])

        if type(cards_create_street) != float and type(cards_create_street) != np.float64:
            if card in cards_create_street:
                creates_street = 1

        suit_card = get_suit_player(card, rotterdam_data['Center'][0], rotterdam_data['Troef'][0])

        if can_win == 1:
            if card in cards_to_win:
                is_card_to_win = 1
        
        if has_highest_suit_all[index] == 0:
            highest_card_still_in_game_all.append(check_card_still_in_game(rotterdam_data['Center'][0], rotterdam_data['Highest_h'][0], rotterdam_data['Highest_d'][0], rotterdam_data['Highest_c'][0], rotterdam_data['Highest_s'][0]))
        else:
            highest_card_still_in_game_all.append(0)

        is_card_that_creates_street.append(creates_street)
        suit_all_cards.append(suit_card)
        is_card_to_win_all.append(is_card_to_win)
        is_highest_suit_all.append(check_has_number([card], card[0], rotterdam_data['Highest_h'][0], rotterdam_data['Highest_d'][0], rotterdam_data['Highest_c'][0], rotterdam_data['Highest_s'][0]))
        is_second_highest_suit_all.append(check_has_number([card], card[0], rotterdam_data['Second_h'][0], rotterdam_data['Second_d'][0], rotterdam_data['Second_c'][0], rotterdam_data['Second_s'][0]))

    rotterdam_data['Creates_street'] = is_card_that_creates_street
    rotterdam_data['Suit'] = suit_all_cards
    rotterdam_data['Is_card_to_win'] = is_card_to_win_all
    rotterdam_data['Player1_has_suit'] = player1_suit_all
    rotterdam_data['Player2_has_suit'] = player2_suit_all
    rotterdam_data['Player3_has_suit'] = player3_suit_all
    rotterdam_data['Has_highest_suit'] = has_highest_suit_all
    rotterdam_data['Has_second_highest_suit'] = has_second_highest_suit_all
    rotterdam_data['Is_highest_suit'] = is_highest_suit_all
    rotterdam_data['Is_second_highest_suit'] = is_second_highest_suit_all
    rotterdam_data['Still_in_game'] = highest_card_still_in_game_all
    
    rotterdam_data['p_none'] = np.nan
    rotterdam_data['p_s'] = np.nan
    rotterdam_data['p_t'] = np.nan
    rotterdam_data['empty_center'] = np.nan
    rotterdam_data['trump_asked'] = np.nan
    rotterdam_data['other_suit_asked'] = np.nan
    rotterdam_data['first_turn'] = np.nan
    rotterdam_data['second_turn'] = np.nan
    rotterdam_data['third_turn'] = np.nan
    rotterdam_data['last_turn'] = np.nan

    for index in rotterdam_data.index:
        if rotterdam_data['Suit'].iloc[index] == '0':
            rotterdam_data.at[index, 'p_none'] = 1
            rotterdam_data.at[index, 'p_s'] = 0
            rotterdam_data.at[index, 'p_t'] = 0
        elif rotterdam_data['Suit'].iloc[index] == '1':
            rotterdam_data.at[index, 'p_none'] = 1
            rotterdam_data.at[index, 'p_s'] = 0
            rotterdam_data.at[index, 'p_t'] = 0
        else:
            rotterdam_data.at[index, 'p_none'] = 1
            rotterdam_data.at[index, 'p_s'] = 0
            rotterdam_data.at[index, 'p_t'] = 0

        if rotterdam_data['Player_turn'].iloc[index] == '1':
            rotterdam_data.at[index, 'first_turn'] = 1
            rotterdam_data.at[index, 'second_turn'] = 0
            rotterdam_data.at[index, 'third_turn'] = 0
            rotterdam_data.at[index, 'last_turn'] = 0
        elif rotterdam_data['Player_turn'].iloc[index] == '2':
            rotterdam_data.at[index, 'first_turn'] = 0
            rotterdam_data.at[index, 'second_turn'] = 1
            rotterdam_data.at[index, 'third_turn'] = 0
            rotterdam_data.at[index, 'last_turn'] = 0
        elif rotterdam_data['Player_turn'].iloc[index] == '3':
            rotterdam_data.at[index, 'first_turn'] = 0
            rotterdam_data.at[index, 'second_turn'] = 0
            rotterdam_data.at[index, 'third_turn'] = 1
            rotterdam_data.at[index, 'last_turn'] = 0
        else:
            rotterdam_data.at[index, 'first_turn'] = 0
            rotterdam_data.at[index, 'second_turn'] = 0
            rotterdam_data.at[index, 'third_turn'] = 0
            rotterdam_data.at[index, 'last_turn'] = 1

        if rotterdam_data['Asked_suit'].iloc[index] == '0':
            rotterdam_data.at[index, 'empty_center'] = 1
            rotterdam_data.at[index, 'trump_asked'] = 0
            rotterdam_data.at[index, 'other_suit_asked'] = 0
        elif rotterdam_data['Asked_suit'].iloc[index] == '1':
            rotterdam_data.at[index, 'empty_center'] = 0
            rotterdam_data.at[index, 'trump_asked'] = 1
            rotterdam_data.at[index, 'other_suit_asked'] = 0
        else:
            rotterdam_data.at[index, 'empty_center'] = 0
            rotterdam_data.at[index, 'trump_asked'] = 0
            rotterdam_data.at[index, 'other_suit_asked'] = 1

    
    # p_suit_dummie = pd.get_dummies(rotterdam_data['Suit'])
    # p_suit_dummie = p_suit_dummie.rename(columns = {'0': 'p_none', '1' : 'p_s', '2' : 'p_t'})

    # p_turn_dummie = pd.get_dummies(rotterdam_data['Player_turn'])
    # p_turn_dummie = p_turn_dummie.rename(columns = {'1': 'first_turn', '2': 'second_turn', '3': 'third_turn', '4': 'last_turn'})

    # asked_suit_dummie = pd.get_dummies(rotterdam_data['Asked_suit'])
    # asked_suit_dummie = asked_suit_dummie.rename(columns = {'0' : 'empty_center', '1' : 'trump_asked', '2' : 'other_suit_asked'})
    # rotterdam_data = pd.concat([rotterdam_data, p_suit_dummie, p_turn_dummie, asked_suit_dummie], axis = 1)


    
    attributes = rotterdam_data[['empty_center', 'trump_asked', 'other_suit_asked', 'Still_in_game', 'Is_second_highest_suit', 'Is_highest_suit', 'Has_second_highest_suit', 'Has_highest_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 'Player2_has_trump','Player3_has_trump', 'Is_card_to_win', 'Can_win', 'Is_higher', 'Has_higher', 'No_playable_cards', 'Is_lowest_value', 'Is_highest_value', 'Teammate_winning', 'Teammate_played', 'Can_create_street', 'Creates_street', 'p_none', 'p_s', 'p_t', 'first_turn', 'second_turn', 'third_turn', 'last_turn']]
    return attributes   


# play_data = pd.read_csv('Play.csv', nrows=10000, usecols=['Cards', 'Center', 'CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'PlayCard', 'Troef', 'Variant', 'PlayableCardBits'], dtype={'HasColor0' : str, 'HasColor1' : str, 'HasColor2' : str, 'HasColor3' : str})

# rotterdam_data = play_data[play_data['Variant'] == 'Rotterdams'].loc[:, ['Cards', 'Center', 'CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'Troef', 'PlayableCardBits', 'PlayCard' ]]
# rotterdam_data = rotterdam_data.reset_0(drop=True)

# del play_data



# rotterdam_data = Main(rotterdam_data)

