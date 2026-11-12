"""Play blackjack in the terminal with the PerfectBot suggesting every move.

Key: h = hit, s = stand, d = double, v = split, l = surrender.
Enter 0 when asked how many hands to play to end the session.
"""
from blackjack import Game, PerfectBot

if __name__ == "__main__":
    Game().play(decks=1, shuffle=True, cards=None, penMin=.7, penMax=.8,
                bot=PerfectBot(das=True, maxHands=3))
