import pandas as pd
import joblib

from meld import check_possible_street

suits = ['k', 'h', 'r', 's']

random_forest = joblib.load("./played_card_prediction.joblib")

def get_asked_suit(center, trump):
    if not center:
        return [1, 0, 0]
    elif center[0].suit == trump:
        return [0, 1, 0]
    else: 
        return [0, 0, 1]

def get_turn(center):
    return [1 if x == len(center) else 0 for x in range(4)]

def player_has_suit(has_suit0, has_suit1, has_suit2, suit):
    suit_index = suits.index(suit)
    has_suit0 = has_suit0[suit_index]
    has_suit1 = has_suit1[suit_index]
    has_suit2 = has_suit2[suit_index]
    return [has_suit0, has_suit1, has_suit2]

def check_has_higher(highest, moves, leading_suit, trump):
    higher_cards = []
    for card in moves:
        if (card.order(trump) > highest.order(trump) and
            (card.suit == leading_suit or
                card.suit == trump)):
            higher_cards.append(card)
    return higher_cards, int(len(higher_cards) > 0)  

def get_player_suit(center, card, trump):
    if card.suit == trump:
        return [0, 0, 1]
    if center:
        if center[0].suit == card.suit:
            return [0, 1, 0]
    return [1, 0, 0]    

def get_played_cards(cardsplayed0, cardsplayed1, cardsplayed2, cardsplayed3):
    dictionary = {'cardsplayed0': cardsplayed0, 'cardsplayed1': cardsplayed1, 'cardsplayed2': cardsplayed2, 'cardsplayed3': cardsplayed3}
    played_cards = [[],[],[],[]]
    for i in range(4):
        for card in dictionary['cardsplayed{}'.format(i)]:
            index = suits.index(card.suit)
            played_cards[index].append(card)
    return played_cards

def get_highest_cards(cardsplayed):
    highest_cards = []
    for i in range(4):
        cards_played = [card.value for card in cardsplayed[i]]
        cards_left = [x for x in range(7,14) if x not in cards_played]
        if len(cards_left) > 1:
            highest_cards.append([cards_left[-1], cards_left[-2]])
        elif len(cards_left) > 0:
            highest_cards.append([cards_left[-1]])
        else:
            highest_cards.append([])
    return highest_cards

def check_has_card(cards, suit, highest_cards, order):
    index = suits.index(suit)
    try:
        for card in cards:
            if card.value == highest_cards[index][order]:
                return 1
        return 0
    except:
        return 0
    
def check_in_game(center, highest_cards):
    index = suits.index(center[0].suit)
    try:
        for card in center:
            if card.suit == center[0].suit:
                if card.value == highest_cards[index][0]:
                    return 0
        return 1
    except:
        return 1

def check_is_card(highest_cards, card, order):
    index = suits.index(card.suit)
    try:
        if highest_cards[index][order] == card.value:
            return 1
        return 0
    except:
        return 0

def check_can_create_street(center, cards):
    cards_to_create_street = []
    for card in cards:
        possible_street = check_possible_street(center, card)
        if possible_street:
            cards_to_create_street.append(card)
    return int(len(cards_to_create_street) > 0), cards_to_create_street

def get_best_card(round, player, hand):
    trick = round.tricks[-1]
    trump = round.trump_suit
    center = trick.cards
    legal_moves = round.legal_moves(hand, player)
    if len(center) > 0:
        highest_card = trick.highest_card(trump)
    all_cards_played = get_played_cards(round.cardsplayed0, round.cardsplayed1, round.cardsplayed2, round.cardsplayed3)
    highest_cards_left = get_highest_cards(all_cards_played)
    data = []
    
    asked_suit = get_asked_suit(center, trump)
    for i in range(3):
        data.append(asked_suit[i])

    if len(center) > 0:
        has_second_highest_suit = check_has_card(legal_moves, center[0].suit, highest_cards_left, 1)
        has_highest_suit = check_has_card(legal_moves, center[0].suit, highest_cards_left, 0)
        if has_highest_suit:
            still_in_game = 0
        else:
            still_in_game = check_in_game(center, highest_cards_left)
    else:
        has_second_highest_suit = []
        has_highest_suit = []
        still_in_game = []
        for card in legal_moves:
            has_second_highest_suit.append(check_has_card(legal_moves, card.suit, highest_cards_left, 1))
            has_highest_suit.append(check_has_card(legal_moves, card.suit, highest_cards_left, 0))
            if has_highest_suit:
                still_in_game.append(0)
            else:
                still_in_game.append(1)
    data.extend([still_in_game, has_second_highest_suit, has_highest_suit])
    
    if len(center) > 0:
        if player == 1:
            has_suit = player_has_suit(round.hascolor2, round.hascolor3, round.hascolor0, center[0].suit)
        else:
            has_suit = player_has_suit(round.hascolor0, round.hascolor1, round.hascolor2, center[0].suit)
        for i in range(3):
            data.append(has_suit[i])
    else:
        player1_suit = []
        player2_suit = []
        player3_suit = []
        for card in legal_moves:
            if player == 1:
                has_suit = player_has_suit(round.hascolor2, round.hascolor3, round.hascolor0, card.suit)
            else:
                has_suit = player_has_suit(round.hascolor0, round.hascolor1, round.hascolor2, card.suit)
            player1_suit.append(has_suit[0])
            player2_suit.append(has_suit[1])
            player3_suit.append(has_suit[2])
        data.extend([player1_suit, player2_suit, player3_suit])

    if player == 1:
        has_trump = player_has_suit(round.hascolor2, round.hascolor3, round.hascolor0, trump)
    else:
        has_trump = player_has_suit(round.hascolor0, round.hascolor1, round.hascolor2, trump)
    for i in range(3):
        data.append(has_trump[i])

    if len(center) > 0:
        higher_cards, has_higher = check_has_higher(highest_card, legal_moves, center[0].suit, trump)
    else:
        has_higher = 1
        higher_cards = legal_moves.copy()

    no_moves = len(legal_moves)
    
    if len(center) > 1:
        winner = trick.winner(trump)
        if winner %2 == 1:
            teammate_winning = 1
        else:
            teammate_winning = 0
        teammate_played = 1
    else:
        teammate_winning = 0
        teammate_played = 0
    data.extend([has_higher, no_moves, teammate_winning, teammate_played])
    
    if len(center) > 1:
        can_create_street, cards_to_create_street = check_can_create_street(center, legal_moves)
    else:
        can_create_street = 0
        cards_to_create_street = []        
    data.append(can_create_street)

    if len(center) > 0:
        player_suit = get_player_suit(center, legal_moves[0], trump)
    else:
        player_suit = [1, 0, 0]
    for i in range(3):
        data.append(player_suit[i])

    turn = get_turn(center)
    for i in range(4):
        data.append(turn[i])
    
    index = [x for x in range(no_moves)]
    data.append(index)

    dataframe = pd.DataFrame([data], columns = ['empty_center', 'trump_asked', 'other_suit_asked', 'Still_in_game', 'Has_second_highest_suit', 
    'Has_highest_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 'Player2_has_trump',
    'Player3_has_trump', 'Has_higher', 'No_playable_cards', 'Teammate_winning', 'Teammate_played', 'Can_create_street', 'p_none', 'p_s', 'p_t', 'first_turn', 'second_turn', 
    'third_turn', 'last_turn', 'index'])
    

    dataframe = dataframe.set_index(['empty_center', 'trump_asked', 'other_suit_asked', 'Player1_has_trump', 'Player2_has_trump',
    'Player3_has_trump', 'Has_higher', 'No_playable_cards', 'Teammate_winning', 'Teammate_played', 'first_turn', 'second_turn', 
    'third_turn', 'last_turn', 'Can_create_street']).apply(pd.Series.explode).reset_index()

    
    is_higher = []
    is_highest = []
    is_second_highest = []
    lowest_value = 21
    highest_value = 0
    creates_street_all = []
    for index, card in enumerate(legal_moves):
        if card in higher_cards:
            is_higher.append(1)
        else:
            is_higher.append(0)

        if dataframe['Has_highest_suit'][index] == 1:
            is_highest.append(check_is_card(highest_cards_left, card, 0))
        else:
            is_highest.append(0)
        
        
        if dataframe['Has_second_highest_suit'][index] == 1:
            is_second_highest.append(check_is_card(highest_cards_left, card, 1))
        else:
            is_second_highest.append(0)

        points = card.points(trump)
        if points < lowest_value:
            lowest_card = index
            lowest_value = points

        if points > highest_value:
            highest_card = index
            highest_value = points

        creates_street = 0
        if dataframe['Can_create_street'][index] == 1:
            if card in cards_to_create_street:
                creates_street = 1
        creates_street_all.append(creates_street)

    dataframe['Is_higher'] = is_higher
    dataframe['Is_highest_suit'] = is_highest
    dataframe['Is_second_highest_suit'] = is_second_highest
    is_lowest_value = [1 if x == lowest_card else 0 for x in range(no_moves)]
    is_highest_value = [1 if x == highest_card else 0 for x in range(no_moves)]    
    dataframe['Is_lowest_value'] = is_lowest_value
    dataframe['Is_highest_value'] = is_highest_value
    dataframe['Creates_street'] = creates_street_all
    dataframe.drop('index', inplace=True, axis=1)
    dataframe = dataframe[['empty_center', 'trump_asked', 'other_suit_asked', 'Still_in_game', 'Is_second_highest_suit', 'Is_highest_suit', 'Has_second_highest_suit', 'Has_highest_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 'Player2_has_trump','Player3_has_trump', 'Is_higher', 'Has_higher', 'No_playable_cards', 'Is_lowest_value', 'Is_highest_value', 'Teammate_winning', 'Teammate_played', 'Can_create_street', 'Creates_street', 'p_none', 'p_s', 'p_t', 'first_turn', 'second_turn', 'third_turn', 'last_turn']]
    predictions = random_forest.predict_proba(dataframe)
    highest_prob = 0
    for index, prediction in enumerate(predictions):
        if prediction[1] > highest_prob:
            highest_prob = prediction[1]
            best_card = legal_moves[index]
    return best_card










