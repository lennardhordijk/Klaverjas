from deck import Deck, Card
from meld import meld_points

class Trick:
    def __init__(self, starting_player):
        self.cards = []
        self.starting_player = starting_player

    def add_card(self, card):
        self.cards.append(card)
        # print(card.suit + str(card.value))
        cards = []
        # for card in self.cards:
        #     cards.append(card.suit + str(card.value))
        # print(cards)

    def is_complete(self):
        return len(self.cards) == 4

    def leading_suit(self):
        if self.cards:
            return self.cards[0].suit

    def winner(self, trump_suit):
        highest = self.cards[0] 
        for card in self.cards:
            if (card.order(trump_suit) > highest.order(trump_suit) and
                (card.suit == self.leading_suit() or
                 card.suit == trump_suit)):
                highest = card        
        return (self.starting_player + self.cards.index(highest)) % 4

    def highest_card(self, trump_suit):
        highest = self.cards[0] 
        for card in self.cards:
            if (card.order(trump_suit) > highest.order(trump_suit) and
                (card.suit == self.leading_suit() or
                 card.suit == trump_suit)):
                highest = card 
        return highest

    def to_play(self):
        return (self.starting_player + len(self.cards)) % 4

    def points(self, trump_suit):
        return sum(card.points(trump_suit) for card in self.cards)
        
    def highest_trump(self, trump_suit):
        return max(self.cards,
                   default=Card(7, trump_suit).order(trump_suit),
                   key=lambda card: card.order(trump_suit))

    def meld(self, trump_suit):
        return meld_points(self.cards, trump_suit)