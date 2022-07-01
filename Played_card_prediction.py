import pandas as pd
import numpy as np
import time
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from matplotlib import pyplot as plt

class Card:
    def __init__(self, card):
        self.suit = card[0]
        self.value = int(card[1:])

    def order(self, trump_suit):
        if self.suit == trump_suit:
            return [8, 9, 14, 12, 15, 10, 11, 13][self.value - 7]
        return [0, 1, 2, 6, 3, 4, 5, 7][self.value - 7]

    def points(self, trump_suit):
        if self.suit == trump_suit:
            return [0, 0, 14, 10, 20, 3, 4, 11][self.value - 7]
        return [0, 0, 0, 10, 2, 3, 4, 11][self.value - 7]

suits = ['k', 'h', 'r', 's']
values = [7, 8, 9, 10, 11, 12, 13, 14]
possible_street = []
for suit in suits:
    for idx in range(7,13):
        cards = {suit + str(idx), suit + str(idx + 1), suit + str(idx + 2)}
        possible_street.append(cards)  

def transform_cards(cards):
    #Creat class instance of each card
    if type(cards) == float:
        return cards
    transformed_cards = []
    for card in cards:
        transformed_cards.append(Card(card))
    return transformed_cards

def transform_back(cards):
    #Create normal cards from class instances
    transformed_cards = []
    if type(cards) == float:
        return cards
    try:
        for card in cards:
            transformed_cards.append(card.suit + str(card.value))
        return transformed_cards
    except:
        return [cards.suit + str(cards.value)]

def get_asked_suit(center, trump):
    #Return the asked suit based on the first card of center.
    if type(center) == float:
        return np.nan
    if center[0].suit == trump:
        return '1'
    return '2'

def player_has_trump(hascolor, suit):
    #Checks whether a player still has trump suit
    suit_index = suits.index(suit)
    return int(hascolor[suit_index])

def len_center(center):
    #Returns the length of the center
    if type(center) == float:
        return 0
    return len(center)

def get_playable_cards(cards, bits):
    #Returns the cards that are allowed to be played.
    playable_cards = []
    for index, bit in enumerate(bits[0]):
        if bit == '1':
            playable_cards.append(cards[index])
    return playable_cards

def check_has_higher(center, cards, trump):
    #Returns whether there is a card that is higher than the cards in center and the card that are higher.
    has_higher = 0
    higher_cards = []
    if type(center) != float:
        highest = center[0]
        leading_suit = center[0].suit
        for card in center:
            if (card.order(trump) > highest.order(trump) and
                (card.suit == leading_suit or
                    card.suit == trump)):
                highest = card
        highest_value = highest.order(trump)
        for card in cards:
            if (card.order(trump) > highest_value and
                (card.suit == leading_suit or 
                    card.suit == trump)):
                has_higher = 1
                higher_cards.append(card)
        return has_higher, higher_cards
    else:
        return 1, cards 
     
def teammate_winning(center, trump, center_length):
    #Checks whether teammate is winning
    leading_suit = center[0].suit
    highest_card = center[0]
    for card in center:
        if (card.order(trump) > highest_card.order(trump) and
            (card.suit == leading_suit or 
                card.suit == trump)):
            highest_card = card
    card_index = center.index(highest_card)

    if center_length == 2 and card_index == 0:
        return 1
    elif center_length == 3 and card_index == 1:
        return 1
    return 0

def get_highest_cards(cardsplayed0, cardsplayed1, cardsplayed2, cardsplayed3):
    #Get for each suit the two highest cards that are still in game
    played_cards = get_played_cards(cardsplayed0, cardsplayed1, cardsplayed2, cardsplayed3)
    highest_cards = []
    for i in range(4):
        cards_played = [card.value for card in played_cards[i]]
        cards_left = [x for x in range(7,15) if x not in cards_played]
        if len(cards_left) > 1:
            highest_cards.append([cards_left[-1], cards_left[-2]])
        elif len(cards_left) > 0:
            highest_cards.append([cards_left[-1]])
        else:
            highest_cards.append([])
    return highest_cards

def get_played_cards(cardsplayed0, cardsplayed1, cardsplayed2, cardsplayed3):
    #Creates a list of lists of all cards that are played sorted by suit.
    dictionary = {'cardsplayed0': cardsplayed0, 'cardsplayed1': cardsplayed1, 'cardsplayed2': cardsplayed2, 'cardsplayed3': cardsplayed3}
    played_cards = [[],[],[],[]]
    for i in range(4):
        if type(dictionary['cardsplayed{}'.format(i)]) != float:
            for card in dictionary['cardsplayed{}'.format(i)]:
                index = suits.index(card.suit)
                played_cards[index].append(card)
    return played_cards

def check_has_card(cards, center, highest_cards, order):
    #Checks whether player has the highest (order = 0) or second highest card (order = 1).
    if len_center(center) > 0:
        suit = center[0].suit
        index = suits.index(suit)
        #The second highest card sometimes does not exist.
        try:
            for card in cards:
                if card.value == highest_cards[index][order] and card.suit == suit:
                    return 1
            return 0
        except:
            return 0
    else:
        return np.nan

def check_can_create_street(center, cards):
    #Gets cards that can creeate a street
    cards_to_create_street = []
    for card in cards:
        possible_street = check_possible_street(center, card)
        if possible_street:
            cards_to_create_street.append(card)
    return cards_to_create_street

def check_possible_street(center, card):
    #Checks whether there is a street in the combination of center with card.
    cards = []
    for center_card in center:
        cards.append(center_card.suit + str(center_card.value))
    cards.append(card.suit + str(card.value))
    for meld in possible_street:
        if meld.issubset(set(cards)):
            return 1
    return 0

def still_in_game(center, highest_cards, has_highest):
    #Checks whether the highest card of a suit in still in the game and not in the center
    if has_highest == 1:
        return 0
    if len_center(center) == 0:
        return 1
    try:
        index = suits.index(center[0].suit)
        for card in center:
            if card.suit == center[0].suit:
                if card.value == highest_cards[index][0]:
                    return 0
        return 1
    except:
        return 1

def player_has_suit(len_center, center, hascolor):
    #Checks whether the player has a asked suit
    if len_center == 0:
        return np.nan
    suit_index = suits.index(center[0].suit)
    return int(hascolor[suit_index])

def check_has_card_empty_center(card, highest_cards, order):
    #Checks whether the player has the highest or second highest card given a empty center.
    index = suits.index(card.suit)
    try:
        if card.value == highest_cards[index][order]:
            return 1
        return 0
    except:
        return 0
    
def check_is_card(card, highest_cards, order):
    #Checks whether this card is the highest or second highest card
    try:
        index_suit = suits.index(card.suit)
        if card.value == highest_cards[index_suit][order]:
            return 1
        return 0
    except:
        return 0

def get_lowest_value(cards, trump):
    #Get lowest value of all cards in hand
    lowest_value = 21
    for card in cards:
        if card.points(trump) < lowest_value:
            lowest_value = card.points(trump)
    return lowest_value

def get_highest_value(cards, trump):
    #Get highest value of all cards in hand
    highest_value = 0
    for card in cards:
        if card.points(trump) > highest_value:
            highest_value = card.points(trump)
    return highest_value

def get_player_suit(center, card, trump):
    #Returns the suit of the current card
    if card.suit == trump:
        return '2'
    if len_center(center) > 0:
        if center[0].suit == card.suit:
            return '1'
    return '0'

def player_has_suit_no_center(card, hascolor):
    #Checks whether an opponent has a certain suit given the suit of the card
    suit_index = suits.index(card.suit)
    return int(hascolor[suit_index])

def get_second_element(row):
    return row[1]

def current_player_has_suit(cards, suit):
    for card in cards:
        if card.suit == suit:
            return 1
    return 0

def get_suit_center(center, trump):
    dictionary = {'card1' : np.nan, 'card2' : np.nan}
    for i in range(1, len(center)):
        if center[i].suit == center[0].suit:
            dictionary['card{}'.format(i)] = '1'
        elif center[i].suit == trump:
            dictionary['card{}'.format(i)] = '2'
        else:
            dictionary['card{}'.format(i)] = '0'
    return [dictionary['card1'], dictionary['card2']]

start_time = time.time()

print('start')

play_data = pd.read_csv('Play.csv', usecols=['Cards', 'Center', 'CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'PlayCard', 'Troef', 'Variant', 'PlayableCardBits'], dtype={'HasColor0' : str, 'HasColor1' : str, 'HasColor2' : str, 'HasColor3' : str})

#Filter out Rotterdam Version
rotterdam_data = play_data[play_data['Variant'] == 'Rotterdams'].loc[:, ['Cards', 'Center', 'CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'Troef', 'PlayableCardBits', 'PlayCard' ]].reset_index(drop=True)

del play_data

#Save the original hand for debugging purposes
rotterdam_data['Original_hand'] = rotterdam_data['Cards']

#Create classes from given cards
rotterdam_data['Cards'] = rotterdam_data['Cards'].str.replace('.', '', regex=True).str.split().map(lambda x: transform_cards(x))
rotterdam_data['Center'] = rotterdam_data['Center'].str.replace('.', '', regex=True).str.split().map(lambda x: transform_cards(x))
for i in range(4):
    rotterdam_data['CardsPlayed{}'.format(i)] = rotterdam_data['CardsPlayed{}'.format(i)].str.split().map(lambda x: transform_cards(x))

#Filter not already played cards and split it into a list
rotterdam_data['PlayableCardBits'] = rotterdam_data['PlayableCardBits'].str.replace('.', '', regex=True).str.split()

print('1')
#Filter out only playable cards
rotterdam_data['Cards'] = rotterdam_data.apply(lambda x: get_playable_cards(x['Cards'], x['PlayableCardBits']), axis = 1)

#Filter out suit of Trump
rotterdam_data['Troef'] = rotterdam_data['Troef'].str[0]

#Get the suit of the first played card. 0 if no card in center. 1 if suit is equal to trump, 2 otherwise.
rotterdam_data['Asked_suit'] = rotterdam_data.apply(lambda x: get_asked_suit(x['Center'], x['Troef']), axis = 1)
print('2')

#Get number of playable cards
rotterdam_data['No_playable_cards'] = rotterdam_data.apply(lambda x: len(x['Cards']), axis = 1)

#Get length of center. Used as input for other functions
rotterdam_data['len_center'] = rotterdam_data.apply(lambda x: len_center(x['Center']), axis = 1)

#Get player turn
rotterdam_data['Player_turn'] = rotterdam_data['len_center'].astype(str)
print('3')

#Check whether teammate has played
rotterdam_data['Teammate_played'] = rotterdam_data.apply(lambda x: 1 if x['len_center'] > 1 else 0, axis = 1)

#Check whether opponnents could still have a trump card
for i in range(1,4):
    rotterdam_data['Player{}_has_trump'.format(i)] = rotterdam_data.apply(lambda x: player_has_trump(x['HasColor{}'.format(i)], x['Troef']), axis = 1)

#Check whether current player can play a card which is higher than th current played cards
rotterdam_data['Has_higher'] = rotterdam_data.apply(lambda x: check_has_higher(x['Center'], x['Cards'], x['Troef'])[0], axis = 1)
print('4')

#Get the cards that are higher
rotterdam_data['Higher_cards'] = rotterdam_data.apply(lambda x: check_has_higher(x['Center'], x['Cards'], x['Troef'])[1], axis = 1)

#Check whether teammate is winning
rotterdam_data['Teammate_winning']  = rotterdam_data.apply(lambda x: teammate_winning(x['Center'], x['Troef'], x['len_center']) if x['Teammate_played'] == 1 else 0, axis = 1)
print('5')

#Get the two highest cards of each suit still in game
rotterdam_data['Highest_cards'] = rotterdam_data.apply(lambda x: get_highest_cards(x['CardsPlayed0'], x['CardsPlayed1'], x['CardsPlayed2'], x['CardsPlayed3']), axis = 1)

#Check whether current player has one of the highest cards of the asked suit
rotterdam_data['Has_highest_suit'] = rotterdam_data.apply(lambda x: check_has_card(x['Cards'], x['Center'], x['Highest_cards'], 0), axis = 1)
rotterdam_data['Has_second_highest_suit'] = rotterdam_data.apply(lambda x: check_has_card(x['Cards'], x['Center'], x['Highest_cards'], 1), axis = 1)
print('6')

#Check whether the highest card is still in game or already played in the center
rotterdam_data['Still_in_game'] = rotterdam_data.apply(lambda x: still_in_game(x['Center'], x['Highest_cards'], x['Has_highest_suit']), axis = 1)

#Check whether with the current center and cards in hand a street can be made and get those cards
rotterdam_data['Cards_to_create_street'] = rotterdam_data.apply(lambda x: check_can_create_street(x['Center'], x['Cards']) if x['len_center'] > 1 else [], axis = 1)
rotterdam_data['Can_create_street'] = rotterdam_data.apply(lambda x: 1 if int(len(x['Cards_to_create_street']) > 0) else 0, axis = 1)
print('7')

#Get lowest and highest value of cards in the hand of current player
rotterdam_data['Lowest_value'] = rotterdam_data.apply(lambda x: get_lowest_value(x['Cards'], x['Troef']), axis = 1)
rotterdam_data['Highest_value'] = rotterdam_data.apply(lambda x: get_highest_value(x['Cards'], x['Troef']), axis = 1)

rotterdam_data['Has_trump'] = rotterdam_data.apply(lambda x: current_player_has_suit(x['Cards'], x['Troef']), axis = 1)
rotterdam_data['Has_suit'] = rotterdam_data.apply(lambda x: current_player_has_suit(x['Cards'], x['Center'][0].suit) if x['Asked_suit'] == '1' or x['Asked_suit'] == '2' else 1, axis = 1)
 
rotterdam_data['Suit_cards'] = rotterdam_data.apply(lambda x: get_suit_center(x['Center'], x['Troef']) if x['len_center'] != 0 else [np.nan, np.nan], axis = 1)
rotterdam_data[['Suit_card2', 'Suit_card3']] = pd.DataFrame(rotterdam_data.Suit_cards.to_list())
#Checks whether all players have the suit of the first card played
for i in range(4):
    rotterdam_data['Player{}_has_suit'.format(i)] = rotterdam_data.apply(lambda x: player_has_suit(x['len_center'], x['Center'], x['HasColor{}'.format(i)]), axis = 1)
print('8')
#Create a dummie to transform turns
turn_dummie = pd.get_dummies(rotterdam_data['Player_turn']).rename(columns = {'0': 't1', '1': 't2', '2': 't3', '3': 't4'})
asked_suit_dummie = pd.get_dummies(rotterdam_data['Asked_suit']).rename(columns = {'1' : '1_t', '2' : '1_nt'})
card2_dummie = pd.get_dummies(rotterdam_data['Suit_card2']).rename(columns = {'0' : '2_n', '1' : '2_s', '2' : '2_t'})
card3_dummie = pd.get_dummies(rotterdam_data['Suit_card3']).rename(columns = {'0' : '3_n', '1' : '3_s', '2' : '3_t'})

rotterdam_data = pd.concat([rotterdam_data, asked_suit_dummie, turn_dummie, card2_dummie, card3_dummie], axis = 1)

print('9')

for i in range(1,4):
    rotterdam_data['Rank_card{}'.format(i)] = rotterdam_data.apply(lambda x: x['Center'][i-1].order(x['Troef']) if x['len_center'] > i-1 else 0, axis = 1)

#Split the database for each card in hand
rotterdam_data = rotterdam_data.explode('Cards').reset_index()

#If center is empty, check for each card if it is the highest of the suit
rotterdam_data['Has_highest_suit'] = rotterdam_data.apply(lambda x: check_has_card_empty_center(x['Cards'], x['Highest_cards'], 0) if np.isnan(x['Has_highest_suit']) else x['Has_highest_suit'], axis = 1)
rotterdam_data['Has_second_highest_suit'] = rotterdam_data.apply(lambda x: check_has_card_empty_center(x['Cards'], x['Highest_cards'], 1) if np.isnan(x['Has_second_highest_suit']) else x['Has_second_highest_suit'], axis = 1)

rotterdam_data['Still_in_game'] = rotterdam_data.apply(lambda x: 0 if x['Has_highest_suit'] == 1 else x['Still_in_game'], axis = 1)

#Checks whether this card is the highest or second highest card
rotterdam_data['Is_highest_suit'] = rotterdam_data.apply(lambda x: check_is_card(x['Cards'], x['Highest_cards'], 0) if x['Has_highest_suit'] == 1 else 0, axis = 1)
rotterdam_data['Is_second_highest_suit'] = rotterdam_data.apply(lambda x: check_is_card(x['Cards'], x['Highest_cards'], 1) if x['Has_second_highest_suit'] == 1 else 0, axis = 1)
print('10')
#Checks whether this card is higher than all cards in center
rotterdam_data['Is_higher'] = rotterdam_data.apply(lambda x: int(x['Cards'] in x['Higher_cards']) if x['Has_higher'] == 1 else 0, axis = 1)

#Checks whether this card is lowest or highest value
rotterdam_data['Is_lowest_value'] = rotterdam_data.apply(lambda x: 1 if x['Cards'].points(x['Troef']) == x['Lowest_value'] else 0, axis = 1)
rotterdam_data['Is_highest_value'] = rotterdam_data.apply(lambda x: 1 if x['Cards'].points(x['Troef']) == x['Highest_value'] else 0, axis = 1)
print('11')
#Checks whether this card creates a street
rotterdam_data['Creates_street'] = rotterdam_data.apply(lambda x: 1 if x['Cards'] in x['Cards_to_create_street'] else 0, axis = 1)

#Gets the suit of the card. 2 if card is trump, 1 if card is asked suit, 0 otherwise
rotterdam_data['Player_suit'] = rotterdam_data.apply(lambda x: get_player_suit(x['Center'], x['Cards'], x['Troef']), axis = 1)

#Check whether the current card is the played card. This is the target
rotterdam_data['Is_played_card'] = rotterdam_data.apply(lambda x: 1 if x['Cards'].suit + str(x['Cards'].value) == x['PlayCard'] else 0, axis = 1)
print('12')
#Check if the center is empty, whether opponents have the suit of the current card
for i in range(4):
    rotterdam_data['Player{}_has_suit'.format(i)] = rotterdam_data.apply(lambda x: player_has_suit_no_center(x['Cards'], x['HasColor{}'.format(i)]) if np.isnan(x['Player{}_has_suit'.format(i)]) else x['Player{}_has_suit'.format(i)], axis = 1)

rotterdam_data['rank_player_card'] = rotterdam_data.apply(lambda x: x['Cards'].order(x['Troef']), axis = 1)
 
player_suit_dummie = pd.get_dummies(rotterdam_data['Player_suit']).rename(columns = {'0': 'p_none', '1' : 'p_s', '2' : 'p_t'})

rotterdam_data = pd.concat([rotterdam_data, player_suit_dummie], axis = 1)
print('13')
#Transform the cards back from classes to normal cards. For debugging purposes
rotterdam_data['Cards'] = rotterdam_data.apply(lambda x: transform_back(x['Cards']), axis = 1)
rotterdam_data['Center'] = rotterdam_data.apply(lambda x: transform_back(x['Center']), axis = 1)
for i in range(4):
    rotterdam_data['CardsPlayed{}'.format(i)] = rotterdam_data.apply(lambda x: transform_back(x['CardsPlayed{}'.format(i)]), axis = 1)
print('14')

#Create set of features and target
attributes = rotterdam_data[['rank_player_card', 'Rank_card1', 'Rank_card2', 'Rank_card3', 'Has_trump', '2_n', '2_s', '2_t', '3_n', '3_s', 
'3_t', 'Has_suit', '1_t', '1_nt', 'Still_in_game', 'Is_second_highest_suit', 'Is_highest_suit', 
'Has_second_highest_suit', 'Has_highest_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 
'Player2_has_trump','Player3_has_trump', 'Is_higher', 'Has_higher', 'No_playable_cards', 'Is_lowest_value', 'Is_highest_value', 
'Teammate_winning', 'Teammate_played', 'Can_create_street', 'Creates_street', 'p_none', 'p_s', 'p_t', 't1', 't2', 
't3', 't4']]
target = rotterdam_data['Is_played_card']

mean_percentages = [0 for i in range(8)]

attributes = rotterdam_data[['rank_player_card', 'Rank_card1', 'Rank_card2', 'Rank_card3', 'Has_trump', '2_n', '2_s', '2_t', '3_n', '3_s', '3_t', 'Has_suit', '1_t', '1_nt', 'Still_in_game', 'Is_second_highest_suit', 'Is_highest_suit', 
'Has_second_highest_suit', 'Has_highest_suit', 'Player1_has_suit', 'Player2_has_suit', 'Player3_has_suit', 'Player1_has_trump', 
'Player2_has_trump','Player3_has_trump', 'Is_higher', 'Has_higher', 'No_playable_cards', 'Is_lowest_value', 'Is_highest_value', 
'Teammate_winning', 'Teammate_played', 'Can_create_street', 'Creates_street', 'p_none', 'p_s', 'p_t', 'first_turn', 'second_turn', 
'third_turn', 'last_turn']]
target = rotterdam_data['Is_played_card']

mean_percentages = [0 for i in range(8)]

for i in range(1):
    print(i)
    #Split the dataset into 
    attributes_train, attributes_test, target_train, target_test = train_test_split(attributes, target, test_size=0.25)

    #Train a classifier on the dataset
    rf = RandomForestClassifier()
    rf = rf.fit(attributes_train, target_train)
    predictions = rf.predict_proba(attributes)

    predictions = list(map(get_second_element, predictions))

    rotterdam_data['Prediction'] = predictions

    already_checked = [False for i in rotterdam_data.index]

    percentages = {}
    for i in range(1,9):
        percentages['playable_cards{}'.format(i)] = 0
        percentages['playable_cards{}_good'.format(i)] = 0

    rotterdam_data['Chosen_card'] = np.nan

    for index in rotterdam_data.index:
        checked = already_checked[index]

        if checked:
            continue
        
        no_cards = rotterdam_data['No_playable_cards'][index]
        
        #Get the card with the highest probability of being played for each hand
        highest_prediction = 0
        for i in range(no_cards):
            already_checked[index + i] = True
            prediction = rotterdam_data['Prediction'][index + i]
            if prediction > highest_prediction:
                highest_prediction = prediction
                best_card = rotterdam_data['Cards'][index + i][0]
        rotterdam_data.at[index, 'Chosen_card'] = best_card
        percentages['playable_cards{}'.format(no_cards)] += 1
        
        if rotterdam_data['PlayCard'][index] == rotterdam_data['Chosen_card'][index]:
            percentages['playable_cards{}_good'.format(no_cards)] += 1
        # else:
        #     for i in range(no_cards):
        #         print(rotterdam_data.loc[index + i])
    no_cards = 0
    no_good_cards = 0
    for i in range(1,9):
        percentage = (percentages['playable_cards{}_good'.format(i)]/percentages['playable_cards{}'.format(i)]) * 100
        mean_percentages[i- 1] += percentage
        no_cards += percentages['playable_cards{}'.format(i)]
        no_good_cards += percentages['playable_cards{}_good'.format(i)]

for i in range(8):
    mean_percentages[i] = mean_percentages[i]/1
    print('Aantal keer dezelfde kaart bij {} kaarten: %.2f'.format(i + 1) % mean_percentages[i], '%')

joblib.dump(rf, "./played_card_prediction.joblib")
print(time.time() - start_time)

print(no_good_cards/no_cards)
