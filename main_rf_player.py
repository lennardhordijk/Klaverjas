from rounds import Round
from deck import Deck
from Transformation import get_best_card

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
            played_card = get_best_card(self.rounds[-1], player, self.cards[player])
        else:
            round = self.rounds[-1]
            moves = round.legal_moves(self.cards[player], player)
            played_card = random.choice(moves)
        self.cards[player].remove(played_card)
        return played_card

wins = 0

overall_start_time = time.time()
print('start')

for i in range(100):
    print(i)
    game = Game()
    game.play_game()
    if game.score[1] > game.score[0]:
        wins += 1
    

    
print('average time:', (time.time() - overall_start_time) / 500)       
    

print(wins)
