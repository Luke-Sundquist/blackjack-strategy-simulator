"""A blackjack hand (player or dealer)."""


class Hand:
    cards = []
    deck = None
    double = False
    hasBeenSplit = False
    isSoft = False
    isInsured = False
    def __init__(self,cards=[],deck=None,hasBeenSplit = False):
        self.cards = cards
        self.deck = deck
        self.double = False
        self.hasBeenSplit = hasBeenSplit
        self.isSoft = False
        self.isInsured = False
    # Returns blackjack value of the hand
    def val(self):
        v=0
        hasAce = False
        for x in self.cards:
            v += x.val()
            if x.val()==1:
                hasAce = True
        if hasAce and v<=11:
            v+=10
            self.isSoft = True
        else:
          self.isSoft = False
        return v
    # Adds a card to the hand. Use for hit, double, and split
    def addCard(self,fromTop):
        self.cards.append(self.deck.deal(fromTop))
    def copy(self):
      return Hand(cards=self.cards.copy(),deck=self.deck,hasBeenSplit=self.hasBeenSplit)
    def __str__(self) -> str:
       return '['+', '.join(str(x) for x in self.cards)+']'
