from rounds_rotterdam import Round
from deck import Deck
from Transformation import get_best_card

import random
import time

class Game:
    def __init__(self, starting_player):
        self.rounds = []
        self.score = [0,0]
        self.starting_player = starting_player

    #Gives each player 8 cards to play with
    def deal(self):
        deck = Deck()
        deck.shuffle()
        self.cards = [deck.cards[0:8], deck.cards[8:16], deck.cards[16:24], deck.cards[24:32]]

    #Starts a new round
    def start_new_round(self):
        if self.rounds:
            last_round = self.rounds[-1]
            if not last_round.is_complete():
                return        
        trump_suit = random.choice(['k', 'h', 'r', 's'])
        self.rounds.append(Round(self.starting_player, trump_suit))
        self.deal()
    
    #Plays a game of Klaverjas. Currently a game conists of 1 round
    def play_game(self):
        for no_rounds in range(1):
            self.start_new_round()
            round = self.rounds[-1]
            starting_player = round.starting_player
            for i in range(8):
                if round.tricks:
                    starting_player = round.tricks[-1].starting_player
                for j in range(4):
                    current_player = (j + starting_player) % 4
                    played_card = self.get_card(current_player)
                    round.play_card(played_card, current_player)
                self.rounds[-1].complete_trick()
               
            self.score[0] += self.rounds[-1].points[0]
            self.score[1] += self.rounds[-1].points[1]
    
    #Determines the card to play for a player based on the strategy of that player
    def get_card(self, player):
        if player == 1 or player == 3:
            played_card = get_best_card(self.rounds[-1], player, self.cards[player])
        else:
            played_card = self.get_card_good_player(player)
        self.cards[player].remove(played_card)
        return played_card

    #Returns the card for the rule-based player
    def get_card_good_player(self, player):
        round = self.rounds[-1]
        trick = round.tricks[-1]
        trump = round.trump_suit
        legal_moves = round.legal_moves(self.cards[player], player)
        cant_follow = 0
        if len(trick.cards) == 0:
            for card in legal_moves:
                if card.value == round.get_highest_card(card.suit):
                    return card
            return self.get_lowest_card(legal_moves, trump)

        if legal_moves[0].suit == trick.cards[0].suit:
            cant_follow = 1
            
        if len(trick.cards) == 1:
            for card in legal_moves:
                if card.value == round.get_highest_card(trick.cards[0].suit):
                    return card
            return self.get_lowest_card(legal_moves, trump)
                

        if len(trick.cards) == 2:
            if cant_follow:
                return self.get_lowest_card(legal_moves, trump)

            if trick.cards[0].value == round.get_highest_card(trick.cards[0].suit):
                return self.get_highest_card(legal_moves, trump)


            for card in legal_moves:
                if card.value == round.get_highest_card(trick.cards[0].suit):
                    return card

            return self.get_lowest_card(legal_moves, trump)

        else:
            
            if trick.winner(trump) %2 == 1:
                return self.get_highest_card(legal_moves, trump)

            highest = trick.highest_card(trump)
            for card in legal_moves:
                if card.order(trump) > highest.order(trump):
                    return card

            return self.get_lowest_card(legal_moves, trump)
    
    def get_lowest_card(self, legal_moves, trump):
        lowest_points = 21
        for card in legal_moves:
            if card.points(trump) < lowest_points:
                lowest_card = card
                lowest_points = card.points(trump)
        return lowest_card

    def get_highest_card(self, legal_moves, trump):
        highest_points = -1
        for card in legal_moves:
            if card.points(trump) > highest_points:
                highest_card = card
                highest_points = card.points(trump)
        return highest_card

    def has_trump_cards(cards, trump):
        no_of_trumps = 0
        for card in cards:
            if card.suit == trump:
                no_of_trumps += 1
        return no_of_trumps

games = [0,0]
games_won = [0,0]

rounds = pd.read_csv('Rounds.csv')
points = []
#Simulates the 10000 pre-generated games
for index in rounds.index:
    game = Game(rounds['0'].iloc[index], rounds['1'].iloc[index], rounds['2'].iloc[index])
    game.play_game()
    starting_player = game.starting_player
    if game.score[1] > game.score[0]:
        games_won[starting_player] += 1
    games[starting_player % 2] += 1
    points.append(game.score)
    if index%10 == 0:
        print(index/5000, (games_won[0] + games_won[1]) / (index + 1))
    
print('Games won when started: ', games_won[1]/games[1])
print('Games won when not started: ', games_won[0]/games[0])    
print(games_won)