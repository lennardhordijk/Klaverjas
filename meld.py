from deck import Card


meld_20 = []
meld_50 = []
meld_100 = []
suits = ['k', 'h', 'r', 's']
values = [7, 8, 9, 10, 11, 12, 13, 14]
for suit in suits:
    for idx in range(7,13):
        meld_20.append({Card(value, suit)
                        for value in range(idx, idx + 3)})
    for idx in range(7,12):
        meld_50.append({Card(value, suit)
                        for value in range(idx, idx + 4)})
for value in values:
    meld_100.append({Card(value, suit) for suit in suits})


def meld_points(trick, trump_suit):
    for meld in meld_100:
        if meld <= set(trick):
            return 100

    points = 0
    royal = {Card(trump_suit, 12), Card(trump_suit, 13)}
    if royal <= set(trick):
        points = 20

    for meld in meld_50:
        if meld <= set(trick):
            return points + 50
    for meld in meld_20:
        if meld <= set(trick):
            return points + 20
    return points