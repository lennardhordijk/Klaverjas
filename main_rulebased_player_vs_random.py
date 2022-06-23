from rounds import Round
from deck import Deck

import random
import time

class Game:
    def __init__(self):
        self.rounds = []
        self.score = [0,0]

    def deal(self):
        deck = Deck()
        deck.shuffle()
        self.cards = [deck.cards[0:8], deck.cards[8:16], deck.cards[16:24], deck.cards[24:32]]

    def start_new_round(self):
        if self.rounds:
            last_round = self.rounds[-1]
            if not last_round.is_complete():
                return        
        trump_suit = random.choice(['k', 'h', 'r', 's'])
        self.rounds.append(Round(len(self.rounds) % 4, trump_suit))
        self.deal()
    
    def play_game(self):
        for no_rounds in range(16):
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
            
    def get_card(self, player):
        if player == 1 or player == 3:
            played_card = self.get_card_good_player(player, self.rounds[-1])
        else:
            round = self.rounds[-1]
            moves = round.legal_moves(self.cards[player], player)
            played_card = random.choice(moves)
        self.cards[player].remove(played_card)
        return played_card

    def get_card_good_player(self, player, round):
        trick = round.tricks[-1]
        trump = round.trump_suit
        for card in self.cards[player]:
            if card.order(trump) == 7 or card.order(trump) == 15:
                return card
        if len(trick.cards) == 0 or len(trick.cards) == 1:
            return self.get_lowest_card(player, trump)

        elif len(trick.cards) == 2:
            if trick.cards[0].order(trump) == 7 or trick.cards[0].order(round.trump_suit) == 15:
                return self.get_highest_card(player, trump)

            return self.get_lowest_card(player, trump)

        else:
            if trick.winner(trump) %2 == 1:
                return self.get_highest_card(player, trump)
            return self.get_lowest_card(player, trump)
    
    def get_lowest_card(self, player, trump):
        lowest_points = 21
        for card in self.cards[player]:
            if card.points(trump) < lowest_points:
                lowest_card = card
                lowest_points = card.points(trump)
        return lowest_card

    def get_highest_card(self, player, trump):
        highest_points = -1
        for card in self.cards[player]:
            if card.points(trump) > highest_points:
                highest_card = card
                highest_points = card.points(trump)
        return highest_card

wins = 0

overall_start_time = time.time()
print('start')

for i in range(500):
    game = Game()
    game.play_game()
    if game.score[1] > game.score[0]:
        wins += 1
        
    if i%10 == 0:
        print(i)

    
print('average time:', (time.time() - overall_start_time) / 500)       
    

print(wins)
print(wins/500)
