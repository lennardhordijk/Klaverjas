from tricks import Trick

def team(player):
    return player % 2

def other_team(player):
    return (player + 1) % 2

class Round:
    def __init__(self, starting_player, trump_suit):
        self.starting_player = starting_player
        self.trump_suit = trump_suit
        self.tricks = [Trick(starting_player)]
        self.points = [0,0]
        self.meld = [0, 0]
        self.cardsplayed0 = []
        self.cardsplayed1 = []
        self.cardsplayed2 = []
        self.cardsplayed3 = []
        self.hascolor0 = [1,1,1,1]
        self.hascolor1 = [1,1,1,1]
        self.hascolor2 = [1,1,1,1]
        self.hascolor3 = [1,1,1,1]
        self.cardsleft = [[i for i in range(7,15)] for j in range(4)]
        for i in range(4):
            if ['k', 'h', 'r', 's'][i] == self.trump_suit:
                order = [8, 9, 14, 12, 15, 10, 11, 13]
            else:
                order = [0, 1, 2, 6, 3, 4, 5, 7]
            ordered_list = [i for _, i in sorted(zip(order, self.cardsleft[i]))]
            self.cardsleft[i] = ordered_list
    
    def legal_moves(self, hand, player):
        trick = self.tricks[-1]
        leading_suit = trick.leading_suit()

        if leading_suit is None:
            return hand

        follow = []
        trump = []
        trump_higher = []
        highest_trump_value = trick.highest_trump(
            self.trump_suit).order(self.trump_suit)
        current_winner = trick.winner(self.trump_suit)
        for card in hand:
            if card.suit == leading_suit:
                follow.append(card)
            if card.suit == self.trump_suit:
                trump.append(card)
                if card.order(self.trump_suit) > highest_trump_value:
                    trump_higher.append(card)

        if follow and leading_suit != self.trump_suit:
            return follow

        
        
        if player == 0:
            self.hascolor0[['k', 'h', 'r', 's'].index(leading_suit)] = 0
        elif player == 1:
            self.hascolor1[['k', 'h', 'r', 's'].index(leading_suit)] = 0
        elif player == 2:
            self.hascolor2[['k', 'h', 'r', 's'].index(leading_suit)] = 0
        else:
            self.hascolor3[['k', 'h', 'r', 's'].index(leading_suit)] = 0
        if (current_winner + player) % 2 == 0:
            return hand

        return trump_higher or trump or hand   
    
    def is_complete(self):
        return len(self.tricks) == 8 and self.tricks[-1].is_complete()

    def play_card(self, card, player):
        self.tricks[-1].add_card(card)
        if player == 0:
            self.cardsplayed0.append(card)
        elif player == 1:
            self.cardsplayed1.append(card)
        elif player == 2:
            self.cardsplayed2.append(card)
        else:
            self.cardsplayed3.append(card)


    def to_play(self):
        return self.tricks[-1].to_play()
    
    def complete_trick(self):
        trick = self.tricks[-1]
        if trick.is_complete():
            for card in trick.cards:
                self.cardsleft[['k', 'h', 'r', 's'].index(card.suit)].remove(card.value)
            winner = trick.winner(self.trump_suit)
            points = trick.points(self.trump_suit)
            meld = trick.meld(self.trump_suit)
            self.points[team(winner)] += points
            self.meld[team(winner)] += meld

            if len(self.tricks) == 8:
                self.points[team(winner)] += 10
                us = team(self.starting_player)
                them = other_team(self.starting_player)

                if (self.points[us] + self.meld[us] <=
                        self.points[them] + self.meld[them]):
                    self.points[them] = 162
                    self.meld[them] += self.meld[us]
                    self.points[us] = 0
                    self.meld[us] = 0
                elif self.is_pit():
                    self.meld[us] += 100
            else:
                self.tricks.append(Trick(winner))
            return True
        return False

    def is_pit(self):
        for trick in self.tricks:
            if team(self.starting_player) != team(trick.winner(self.trump_suit)):
                return False
        return True

    def get_highest_card(self, suit):
        return self.cardsleft[['k', 'h', 'r', 's'].index(suit)][-1]
    
    def get_number_of_cards_suit(self, suit):
        return len(self.cardsleft[['k', 'h', 'r', 's'].index(suit)])
