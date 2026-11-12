"""Blackjack bots, from a random player up to an exact-EV \"perfect\" bot."""
import random

from .card import Card
from .hand import Hand


# Superclass for all bots
class Bot:
  def __init__(self):
    pass
  # Always plays 1 hand by default
  def handNum(self, cards):
    return 1
  # Not very good at making decisions, very bad strategy
  def decision(self, options, hand, dealerHand, deck):
    return random.choice(options)

  def insurance(self, deck):
    return random.randint(1, 13) <= 4

# Bot that plays like the dealer. Not much better than random
class H17DealerBot(Bot):
  def __init__(self):
    super().__init__()

  def handNum(self, cards):
    return 1

  def decision(self, options, hand, dealerHand, deck):
    return 'h' if hand.val() < 17 or (hand.val()==17 and hand.isSoft) else 's'

  def insurance(self, deck):
    return False

# Plays "basic strategy". Slightly losing but pretty decent
class BasicStrategyH17Bot(Bot):
  def __init__(self, das):
     # Covers hard totals between 9 and 16. Unless it's a double/split, above is a stand and everything below is a hit
     # I'm sure there are better ways to compress this but oh well. Maybe a 2D array
     self.HardChart = {
     (16,2):'s',(16,3):'s',(16,4):'s',(16,5):'s',(16,6):'s',(16,7):'h',(16,8):'h',(16,9):'h',(16,10):'h',(16,11):'h',
     (15,2):'s',(15,3):'s',(15,4):'s',(15,5):'s',(15,6):'s',(15,7):'h',(15,8):'h',(15,9):'h',(15,10):'h',(15,11):'h',
     (14,2):'s',(14,3):'s',(14,4):'s',(14,5):'s',(14,6):'s',(14,7):'h',(14,8):'h',(14,9):'h',(14,10):'h',(14,11):'h',
     (13,2):'s',(13,3):'s',(13,4):'s',(13,5):'s',(13,6):'s',(13,7):'h',(13,8):'h',(13,9):'h',(13,10):'h',(13,11):'h',
     (12,2):'h',(12,3):'h',(12,4):'s',(12,5):'s',(12,6):'s',(12,7):'h',(12,8):'h',(12,9):'h',(12,10):'h',(12,11):'h',
     (12,2):'h',(12,3):'h',(12,4):'s',(12,5):'s',(12,6):'s',(12,7):'h',(12,8):'h',(12,9):'h',(12,10):'h',(12,11):'h',
     (11,2):'d',(11,3):'d',(11,4):'d',(11,5):'d',(11,6):'d',(11,7):'d',(11,8):'d',(11,9):'d',(11,10):'d',(11,11):'d',
     (10,2):'d',(10,3):'d',(10,4):'d',(10,5):'d',(10,6):'d',(10,7):'d',(10,8):'d',(10,9):'d',(10,10):'h',(10,11):'h',
     (9,2):'h',(9,3):'d',(9,4):'d',(9,5):'d',(9,6):'d',(9,7):'h',(9,8):'h',(9,9):'h',(9,10):'h',(9,11):'h'}
     # Covers soft totals between 13 and 19
     self.SoftChart = {
     (19,2):'s',(19,3):'s',(19,4):'s',(19,5):'s',(19,6):'D',(19,7):'s',(19,8):'s',(19,9):'s',(19,10):'s',(19,11):'s',
     (18,2):'D',(18,3):'D',(18,4):'D',(18,5):'D',(18,6):'D',(18,7):'s',(18,8):'s',(18,9):'h',(18,10):'h',(18,11):'h',
     (17,2):'h',(17,3):'d',(17,4):'d',(17,5):'d',(17,6):'d',(17,7):'h',(17,8):'h',(17,9):'h',(17,10):'h',(17,11):'h',
     (16,2):'h',(16,3):'h',(16,4):'d',(16,5):'d',(16,6):'d',(16,7):'h',(16,8):'h',(16,9):'h',(16,10):'h',(16,11):'h',
     (15,2):'h',(15,3):'h',(15,4):'d',(15,5):'d',(15,6):'d',(15,7):'h',(15,8):'h',(15,9):'h',(15,10):'h',(15,11):'h',
     (14,2):'h',(14,3):'h',(14,4):'h',(14,5):'d',(14,6):'d',(14,7):'h',(14,8):'h',(14,9):'h',(14,10):'h',(14,11):'h',
     (13,2):'h',(13,3):'h',(13,4):'h',(13,5):'d',(13,6):'d',(13,7):'h',(13,8):'h',(13,9):'h',(13,10):'h',(13,11):'h',}
     # Always splitting Aces and 8s, represented in decision
     self.SplitHands = {(18,2),(18,3),(18,4),(18,5),(18,6),(18,8),(18,9), (14,2),(14,3),(14,4),(14,5),(14,6),(14,7), (12,3),(12,4),(12,5),(12,6), (6,4),(6,5),(6,6),(6,7), (4,4),(4,5),(4,6),(4,7)}
     if(das):
       # If game allows DAS, add a few more hands to split that only split with DAS allowed
       self.SplitHands = self.SplitHands.union({(12,2),(8,5),(8,6),(6,2),(6,3),(4,2),(4,3)})
       # Surrender on these hands
     self.SurHands = {(16,9),(16,10),(16,11),(15,10)}

  def handNum(self, cards):
    return 1

  def decision(self, options, hand, dealerHand, deck):
    # Source: https://www.blackjackapprenticeship.com/blackjack-strategy-charts/
    if (not hand.isSoft):
      hardTuple = (hand.val(), dealerHand.val())
      # If it's in surrenderHands, then surrender
      if hardTuple in self.SurHands and 'l' in options:
        return 'l'
      # If it's a split hand, split
      if 'v' in options:
        if hand.val()==16 or hardTuple in self.SplitHands:
          return 'v'
      # Otherwise stand on 17 or more
      if hand.val()>16:
        return 's'
      # Otherwise hit on 8 or less
      if hand.val()<9:
        return 'h'
      # Otherwise find the play in the HardChart
      p = self.HardChart[hardTuple]
      if p == 'd':
        if 'd' in options:
          return 'd'
        else:
          return 'h'
      return p

    else:
      # Stand on soft 20
      if(hand.val()==20):
        return 's'
      # Split Aces, otherwise hit if not available to split (RSA off or something)
      if(hand.val()==12):
        if 'v' in options:
          return 'v'
        else:
          return 'h'
      p = self.SoftChart[(hand.val(),dealerHand.val())]
      match(p):
        case 'D':
          if 'd' in options:
            return 'd'
          else:
            return 's'
        case 'd':
          if 'd' in options:
            return 'd'
          else:
            return 'h'
        case _:
          return p

  def insurance(self, deck):
    return False

# A trained card counter could reasonably do this to potentially a small profit
class SimpleHiLoCountingNoDev(BasicStrategyH17Bot):
  def __init__(self, das, maxHands):
    super().__init__(das)
    self.maxHands = maxHands
# Plays as many hands as possible at a true count of 1 or more (true count = running Count/decks remaining)
  def handNum(self, cards):
    rCount = 0
    for c in cards:
      if c.val()==1 or c.val()==10:
        rCount +=1
      elif c.val()>1 and c.val()<7:
        rCount -=1
    return self.maxHands if rCount*52>=len(cards) else 1

  def insurance(self, deck):
    rCount = 0
    for c in deck:
      if c.val()==1 or c.val()==10:
        rCount +=1
      elif c.val()>1 and c.val()<7:
        rCount -=1
    return rCount*2.5>=len(deck)

class WongHalvesBot(BasicStrategyH17Bot):
  def __init__(self, das, maxHands):
    super().__init__(das)
    self.maxHands = maxHands

  def handNum(self, cards):
    rCount = 0
    # Counting the cards still in the deck (because our computer is a beast and it knows this)
    # In reality, a real counter would invert the values of the cards and count the ones that came out
    for c in cards:
      match c.val():
        case 1|10:
          rCount +=1
        case 3|4|6:
          rCount -=1
        case 2|7:
          rCount -=0.5
        case 5:
          rCount -=1.5
        case 9:
          rCount +=0.5
    return self.maxHands if rCount*52>=len(cards) else 1

  def insurance(self, deck):
    rCount = 0
    # Counting the cards still in the deck (because our computer is a beast and it knows this)
    # In reality, a real counter would invert the values of the cards and count the ones that came out
    for c in deck:
      match c.val():
        case 1|10:
          rCount +=1
        case 3|4|6:
          rCount -=1
        case 2|7:
          rCount -=0.5
        case 5:
          rCount -=1.5
        case 9:
          rCount +=0.5
    return rCount*2.5>=len(deck)

# A bot that hopefully plays robotically perfect blackjack
class PerfectBot(Bot):
  def __init__(self, das, maxHands):
    super().__init__()
    self.das = das
    self.maxHands = maxHands
    self.pwinCache = {}
    self.calcHitEVCache = {}

  def handNum(self, cards):
    # Finally, after the bottom 4 tasks have been completed,
    rCount = 0
    # Counting the cards still in the deck (because our computer is a beast and it knows this)
    # In reality, a real counter would invert the values of the cards and count the ones that came out
    for c in cards:
      match c.val():
        case 1|10:
          rCount +=1
        case 3|4|6:
          rCount -=1
        case 2|7:
          rCount -=0.5
        case 5:
          rCount -=1.5
        case 9:
          rCount +=0.5
    # print("Running count: "+str(rCount))
    return self.maxHands if rCount*52>=len(cards) else 1

  def insurance(self, deck):
    tens=0
    for c in deck:
      if c.val() == 10:
        tens += 1
    return tens*3 > len(deck)

  def deckFromCounts(self, counts):
    testDeck = type('', (), {})
    testDeck.shoe = []

    # Creates test deck from card counts
    for i in range(10):
      for _ in range(counts[i]):
        if i == 0:
          testDeck.shoe.append(Card('A'))
        elif i == 9:
          testDeck.shoe.append(Card('T'))
        else:
          testDeck.shoe.append(Card(str(i + 1)))
    return testDeck

  def calcHitEv(self, hand, dealerHand, deck, depth=0):
    # Get counts of remaining cards
    counts = self.getCounts(deck)

    # Memoize the result for better performance
    key = (
    hand.val(),
    hand.isSoft,
    len(hand.cards),
    dealerHand.val(),
    dealerHand.isSoft,
    tuple(counts)
    )
    if key in self.calcHitEVCache:
      return self.calcHitEVCache[key]
    # Cutoff recursion after certain limit
    MAX_DEPTH = 9
    # Only stand after 15 hits
    if depth > MAX_DEPTH:
      counts = self.getCounts(deck)
      return self.pWin(hand.val(),dealerHand,counts, depth)

    # Find amount of all remaining cards
    totalCards = sum(counts)
    # Expected value to be returned
    val = 0
    # Loop through all possible cards that could come next
    for i in range(10):
      if counts[i] == 0:
        continue
      # Probability of drawing the current card
      drawProb = counts[i] / totalCards
      # Copy counts for card removal test
      tempCounts = counts.copy()
      tempCounts[i] -= 1
      # Copy the card and hand for testing
      if i == 0:
        testCard = Card('A')
      elif i == 9:
        testCard = Card('T')
      else:
        testCard = Card(str(i+1))
      testHand = Hand(cards=hand.cards.copy(), deck=deck)
      testHand.cards.append(testCard)
      # Bust Case (don't add to val. 0 ev means always lose 1 bet)
      if testHand.val() > 21:
        val += drawProb * (-1)
        continue
      # No Bust Case
      standEV = self.pWin(testHand.val(), dealerHand, tempCounts, depth+1) # EV if we Stand
      hitEV = self.calcHitEv(testHand, dealerHand, self.deckFromCounts(tempCounts), depth+1) # EV if we hit
      # Next best action
      val += drawProb * max(standEV, hitEV)
    self.calcHitEVCache[key] = val
    return val

  def splitEv(self, hand, dealerHand, deck, das):
    # Counts of remaining cards
    counts = self.getCounts(deck)
    # Total of remaining cards
    totalCards = sum(counts)
    # Expected value for one split hand
    val = 0
    for i in range(10):
      # Probability of drawing this card
      drawProb = counts[i] / totalCards
      # Copy counts for test
      tempCounts = counts.copy()
      tempCounts[i] -= 1
      # Copy the card and hand for testing
      if i == 0:
        testCard = Card('A')
      elif i == 9:
        testCard = Card('T')
      else:
        testCard = Card(str(i+1))
      testHand = Hand(cards=[hand.cards[0], testCard], deck=deck)
      # Remove drawn card for test deck
      testDeck = self.deckFromCounts(tempCounts)
      # Find EV of optimal play
      dubEV = self.calcDoubleEv(hand=testHand, dealerHand=dealerHand, deck=deck) if das else -2
      handEV = max(self.calcHitEv(testHand, dealerHand, testDeck, 1),self.pWin(testHand.val(),dealerHand,tempCounts, 1),dubEV)
      # Add to val
      val += drawProb *handEV
    # Two hands created by splitting, so double EV
    return 2 * val

  # pWin recursively calculates the probability of winning on a stand
  # handVal is hand value, dealerHand is dealer's hand
  # counts is an array containing the number of cards in the deck with value at its index + 1
  # So first index is number of aces, second is number of 2s, all the way up to number of 10s
  def pWin(self, handVal, dealerHand, counts, depth=0):
    if handVal > 21:
      return -1
    if dealerHand.val() > 21:
      return 1

  # Memoize the result for better performance
    key = (
    handVal,
    dealerHand.val(),
    dealerHand.isSoft,
    len(dealerHand.cards),
    tuple(counts)
    )
    if key in self.pwinCache:
      return self.pwinCache[key]
    # Cutoff recursion after certain limit
    MAX_DEPTH = 9
    # Terminate path with no affect on value
    if depth > MAX_DEPTH:
      return 0

    # Counts total outcomes and outcomes where the player wins. Counts pushes as half of a win
    winOutcomes = 0
    outcomes = 0
    for v in range(0,10):
      if counts[v]==0:
        continue
      # If the dealer had natural 21, this wouldn't have happened. Discount possibility of dealer having a ten and ace
      if (len(dealerHand.cards)==1) and ((v==0 and dealerHand.val()==10) or (v==9 and dealerHand.val()==11)):
        continue
      # Add to possible outcomes
      outcomes += counts[v]
      # Add win percentage for the percentage of time dealer busts
      newDealerHand = dealerHand.copy()
      newDealerHand.cards.append(Card(str(v+1)))
      if newDealerHand.val() > 21:
        winOutcomes += counts[v]
        continue
      # If the dealer would stop hitting
      if newDealerHand.val() > 16 and not (newDealerHand.isSoft and newDealerHand.val()==17):
        # If the player has more, add to winOutcomes
        if handVal > newDealerHand.val():
          winOutcomes += counts[v]
        # If the dealer has more subtract from winOutcomes
        elif handVal < newDealerHand.val():
          winOutcomes += counts[v] * (-1)
        # Regardless of result, stop
        continue
        # Recursively call winOutcomes to see what would happen then
      newCounts = counts.copy()
      newCounts[v] -= 1
      winOutcomes += self.pWin(handVal, newDealerHand, newCounts, depth+1)*counts[v]
    # If the deck somehow runs out of cards then return 0
    output = (winOutcomes/outcomes) if outcomes > 0 else 0
    self.pwinCache[key] = output
    return output

  def calcDoubleEv(self, hand, dealerHand, deck):
    counts = self.getCounts(deck)
    # Starts at 0
    ev = 0
    # Total number of cards in deck is t
    t = sum(counts)
    for i in range(0,10):
      if counts[i] == 0:
        continue
      newCounts = counts.copy()
      newCounts[i] -= 1
      # Add double the probability of winning for each possible card to be doubled, since the bet is double
      standEv = self.pWin(hand.val()+i+1,dealerHand,newCounts)
      ev += (counts[i] / t) * (2 * standEv)
    return ev
  # Helper function to get counts array
  def getCounts(self, deck):
    counts = [0,0,0,0,0,0,0,0,0,0]
    for c in deck.shoe:
      counts[c.val()-1] += 1
    return counts

  def decision(self, options, hand, dealerHand, deck):
    ev = [-3,-3,-3,-3,-3]
    allOp = 'hsdvl'
    # If surrender is an option, the EV of surrender is known (lose half a bet)
    if 'l' in options:
      # Reset cache on each new hand
      self.pwinCache.clear()
      self.calcHitEVCache.clear()
      ev[4] = -0.5
    # If hit is an option (always should be) set index 0 to the probability the player's hand + a random card beats the dealer's hand. (do this third)
    if 'h' in options:
      # Calculate the hit EV
      ev[0] = self.calcHitEv(hand, dealerHand, deck)
    # If stand is an option (always should be) set index 1 to the probability the player's hand as is beats the dealer's hand. (do this first)
    if 's' in options:
      # EV is the probability of winning this hand
      ev[1] = self.pWin(hand.val(),dealerHand,self.getCounts(deck))
    # If double is an option, set index 2 to (the probability the player wins if they take a random card then beat the dealer's hand) times 2 minus 1. (do this second)
    if 'd' in options:
      # Instead of certain loss being 0 and certain victory being 1, due to double, certain loss is now -0.5 and certain victory is now 1.5. I think.
      ev[2] = self.calcDoubleEv(hand, dealerHand, deck)
    # If split is an option, set index 3 to (the expected value of the probability the player wins with the card they split with and another random card) times 2 minus 1. (hardest one, do this last)
    if 'v' in options:
      ev[3] = self.splitEv(hand, dealerHand, deck, das=self.das)

    # print(str(options)+": "+str(ev))
    return allOp[ev.index(max(ev))]
