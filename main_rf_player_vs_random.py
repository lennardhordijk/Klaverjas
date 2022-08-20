import random
import time

from rounds_rotterdam import Round
from deck import Deck
from Transformation import get_best_card

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
        self.rounds.append(Round(len(self.rounds) % 4, trump_suit))
        self.deal()
    
    #Plays a game of Klaverjas. Currently a game conists of 1 round
    def play_game(self):
        for no_rounds in range(1):
            self.start_new_round()
            round = self.rounds[-1]
            starting_player = self.starting_player
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
            round = self.rounds[-1]
            moves = round.legal_moves(self.cards[player], player)
            played_card = random.choice(moves)
        self.cards[player].remove(played_card)
        return played_card

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