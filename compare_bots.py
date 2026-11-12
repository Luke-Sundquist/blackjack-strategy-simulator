"""Simulate every counting/strategy bot on the same game and plot bankroll over time.

Default game: double deck, dealer hits soft 17, blackjack pays 3:2,
re-split aces and double after split allowed, no surrender, 70-75% penetration.

Usage:
    python compare_bots.py                 # 100,000 shoes per bot
    python compare_bots.py --shoes 20000   # faster run
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blackjack import (Bot, H17DealerBot, BasicStrategyH17Bot,
                       SimpleHiLoCountingNoDev, WongHalvesBot, Game)

BOTS = [
    ("Wong Halves count", lambda: WongHalvesBot(das=True, maxHands=3), "#0088dd"),
    ("Hi-Lo count", lambda: SimpleHiLoCountingNoDev(das=True, maxHands=3), "#88cc00"),
    ("Basic strategy", lambda: BasicStrategyH17Bot(das=True), "#ffaa00"),
    ("Mimic the dealer", lambda: H17DealerBot(), "#cc3333"),
    ("Random", lambda: Bot(), "#880000"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shoes", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out", default="results/bot_comparison.png")
    args = parser.parse_args()

    if args.seed is not None:
        import random
        random.seed(args.seed)

    game = Game(h17=True, blackjack=1.5, rsa=True, das=True, surrender=False)
    plt.figure(figsize=(10, 6))
    for name, make_bot, color in BOTS:
        print(f"--- {name} ---")
        history = game.simPlay(decks=2, shuffle=True, cards=None, penMin=.7,
                               penMax=.75, bot=make_bot(), shoes=args.shoes)
        plt.plot(history, color=color, label=name)

    plt.title("Bankroll by strategy (starting bankroll: 1,000 units, double deck, 3:2)")
    plt.xlabel("Shoes played")
    plt.ylabel("Bankroll (betting units)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(args.out, dpi=150)
    print(f"Saved chart to {args.out}")


if __name__ == "__main__":
    main()
