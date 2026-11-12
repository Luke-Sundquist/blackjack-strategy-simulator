"""Playing card with blackjack value."""

class Card:
    rank = ''
    suit = ''
    # Initializer. First slot is rank, second slot is suit. Suit will not be important until our stretch goals.
    # Write the rank as 1 character, not as a number. For 2-9, write '2', '3',..., or '9'
    # For Ace, write 'A'
    # For Jack, Queen, King, I would prefer that you write 'J', 'Q', 'K'
    # For 10, I would prefer that you write 'T'
    # Use 'C' for cut card
    def __init__(self, r, s=''):
        self.rank = r
        self.suit = s
    def __str__(self):
        return str(self.rank) + str(self.suit)
    # Use this to get the card's value for blackjack. Just call this function, it's called in Hand
    def val(self):
        match(self.rank):
            # Tens
            case 'T'|'J'|'Q'|'K':
                return 10
            # Ace is yielded as 1, 11 case handled in hand.val()
            case 'A':
                return 1
            case '2':
                return 2
            case '3':
                return 3
            case '4':
                return 4
            case '5':
                return 5
            case '6':
                return 6
            case '7':
                return 7
            case '8':
                return 8
            case '9':
                return 9
            case _:
                return 0
