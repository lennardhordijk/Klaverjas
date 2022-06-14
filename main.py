from email import header
from rounds import Round
from deck import Deck
from Played_card_Prediction2 import Main

import pandas as pd
import random
import joblib
import time

class Game:
    def __init__(self):
        self.rounds = []
        self.score = [0,0]

    def deal(self):
        deck = Deck()
        deck.shuffle()
        self.cards = [deck.cards[0:8], deck.cards[8:16], deck.cards[16:24], deck.cards[24:32]]
        self.cards_good_player = [0, deck.cards[8:16], 0, deck.cards[24:32]]

    def start_new_round(self):
        if self.rounds:
            last_round = self.rounds[-1]
            if not last_round.is_complete():
                return        
        trump_suit = random.choice(['k', 'h', 'r', 's'])
        self.rounds.append(Round(len(self.rounds) % 4, trump_suit))
        self.deal()
    
    def play_game(self):
        for no_rounds in range(1):
            self.start_new_round()
            round = self.rounds[-1]
            starting_player = round.starting_player
            for i in range(8):
                for j in range(4):
                    current_player = (j + starting_player) % 4
                    played_card = self.get_card(current_player)
                    round.play_card(played_card, current_player)
                    # self.get_representation(starting_player)
                self.rounds[-1].complete_trick()
               
            self.score[0] += self.rounds[-1].points[0]
            self.score[1] += self.rounds[-1].points[1]
            
    def get_card(self, player):
        if player == 1 or player == 3:
            position_card = self.card_to_play(player)
            played_card = self.cards_good_player[player][position_card]
            self.cards_good_player[player][position_card] = '.' 
        else:
            round = self.rounds[-1]
            moves = round.legal_moves(self.cards[player], player)
            played_card = random.choice(moves)
        self.cards[player].remove(played_card)
        return played_card

    def card_to_play(self, player):
        round = self.rounds[-1]
        trick = round.tricks[-1]
        cards = self.transform_cards(self.cards_good_player[player])
        center = self.transform_cards(trick.cards)
        cardsplayed0 = self.transform_cards(round.cardsplayed0)
        cardsplayed1 = self.transform_cards(round.cardsplayed1)
        cardsplayed2 = self.transform_cards(round.cardsplayed2)
        cardsplayed3 = self.transform_cards(round.cardsplayed3)
        hascolor0 = self.list_to_string_no_space(round.hascolor0)
        hascolor1 = self.list_to_string_no_space(round.hascolor1)
        hascolor2 = self.list_to_string_no_space(round.hascolor2)
        hascolor3 = self.list_to_string_no_space(round.hascolor3)
        trump = round.trump_suit
        moves = round.legal_moves(self.cards[player], player)
        moves = self.transform_cards(moves)
        playablecardbits = self.get_playable_bits(moves, cards)

        dataframe2 =  pd.DataFrame({'Cards' : [cards], 'Center' : [center], 'CardsPlayed0' : [cardsplayed0], 'CardsPlayed1' : [cardsplayed1], 'CardsPlayed2' : [cardsplayed2], 'CardsPlayed3' : [cardsplayed3], 'HasColor0' : [hascolor0], 'HasColor1' : [hascolor1], 'HasColor2' : [hascolor2], 'HasColor3' : [hascolor3], 'Troef' : [trump], 'PlayableCardBits' : [playablecardbits], 'PlayCard' : ['k3']})
        dataframe2 = pd.concat([header, dataframe2], ignore_index = True, axis = 0)
        attributes = Main(dataframe2)
        # print(attributes)
        predictions = randomforest.predict_proba(attributes)
        highest_probability = 0
        
        for i in range(len(predictions)):
            if predictions[i][1] > highest_probability:
                highest_probability = predictions[i][1]
                highest_card = i
        
        return self.get_position_card(playablecardbits, highest_card)
        
    def get_position_card(self, playablecardbits, card):
        count = 0
        for index, bit in enumerate(playablecardbits):
            if bit == '1':
                if count == card:
                    return index
                count += 1

    def get_playable_bits(self, moves, hand):
        bits = []
        for card in hand:
            if card in moves:
                bits.append('1')
            else:
                bits.append('0')
        return bits
        
    def transform_cards(self, cards):
        transformed_cards = []
        for card in cards:
            if card == '.':
                transformed_cards.append('.')
            else:
                transformed_card = card.suit + str(card.value)
                transformed_cards.append(transformed_card)
        return transformed_cards

    def list_to_string(self, list):
        string = ''
        for element in list:
            string += str(element) + ' '
        if string == '':
            string = float('NaN')
        else:
            string = string [:-1]
        return string
    
    def list_to_string_no_space(self, list):
        string = ''
        for element in list:
            string += str(element)
        return string

start_time = time.time()
wins = 0

randomforest = joblib.load("./played_card_prediction.joblib")
columns = ['Cards', 'Center', 'CardsPlayed0', 'CardsPlayed1', 'CardsPlayed2', 'CardsPlayed3', 'HasColor0', 'HasColor1', 'HasColor2', 'HasColor3', 'Troef', 'PlayableCardBits', 'PlayCard']
header = pd.DataFrame(columns = columns)


for i in range(1000):
    game = Game()
    game.play_game()
    if game.score[0] > game.score[1]:
        wins += 1
        print(i)
    if i % 5 == 1:
        print(time.time() - start_time)

print(wins)