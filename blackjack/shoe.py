"""Shoe of one or more shuffled decks with a cut card."""
import random

from .card import Card


class Shoe:
    # Holds all the cards
    shoe = []
    # Is false when the cut card comes out
    play = True

    def __init__(self, decks=1, shuffle=True, cards=None, penMin=.7, penMax=.8):
        self.play = True
        # If you want to fill with a premade deck (not standard deck), set cards to a specific value when calling
        if cards is not None:
            self.shoe = cards
        else:
            self.shoe = []
        # Otherwise, ignore cards and fill it with standard decks
            for r in ['A','2','3','4','5','6','7','8','9','T','J','Q','K']:
                for s in ['c','d','h','s']:
                    # Puts decks in
                    for x in range(0,decks):
                        c = Card(r,s)
                        self.shoe.append(c)
            # print(str(self))
        # Shuffles the deck by default
        if shuffle:
            random.shuffle(self.shoe)
        l = len(self.shoe)
        # Inserts cut card. When the cut card is drawn, this denotes the last hand
        c = Card('C')
        # Puts it in somewhere between penMin & penMax of the deck.
        # penMax should never be 1, and probably shouldn't be inputted as higher than .9
        # penMin should never be 0, and probably shouldn't be inputted as lower than .5
        self.shoe.insert(random.randrange(int(l*penMin), int(l*penMax)),c)
        # print(str(self))

    # Should work like the standard array toString representation
    def __str__(self):
        return '['+', '.join(str(x) for x in self.shoe)+']'

    def deal(self,fromTop):
        # Deal a card
        c = self.shoe.pop(fromTop)
        # If it's a valid card, return it
        if (c.val() > 0):
            return c
        # If it's not, (cut card), deal the next card
        self.play = False
        return self.deal(fromTop)
