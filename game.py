"""Game engine: interactive play() and bot simulation simPlay()."""
import matplotlib.pyplot as plt

from .shoe import Shoe
from .hand import Hand
from .bots import Bot, PerfectBot


class Game:
  # Number of bets "brought" to the casino
  sbalance = 1000
  balance = 1000
  # True if the dealer hits on soft 17, False if stands on soft 17
  h17=True
  # By default blackjack pays 3:2
  blackjack=1.5
  # Re-Split Aces
  rsa=True
  # Double after split
  das=True
  surrender=True
  # For a 6:5 sim, set blackjack to 1.2
  def __init__(self, balance=1000,h17=True,blackjack=1.5,rsa=True,das=True,surrender=True):
    self.sbalance = balance
    self.balance = balance
    self.h17 = h17
    self.blackjack=blackjack
    self.rsa=rsa
    self.das=das
    self.surrender=surrender

  # Call this to play in the terminal
  def play(self, decks=1, shuffle=True, cards=None, penMin=.7, penMax=.8, bot=None):
    balHistory = [self.balance]
    while(True):
      print("\n\nNew shoe starting\n\n")
      shoe = Shoe(decks=decks, shuffle=shuffle, cards=cards,penMin=penMin, penMax=penMax)
      print(shoe)
      # Place bets
      while(shoe.play and self.balance > 1):
        print("Balance: "+ str(self.balance)+"\n")
        print("How many hands to play?")
        if bot is not None:
          print("Bot says "+str(bot.handNum(shoe.shoe))+"\n")
        h = input()
        while(not h.isnumeric or self.balance < int(h) or int(h)<0):
          h = input()
        h = int(h)
        # Enter 0 to end session or "Wong out"
        if h==0:
          print("\n\nSession over. Total profit: "+str(self.balance-self.sbalance))
          plt.plot(balHistory)
          plt.show()
          return
        self.balance -= h

        # Deal cards
        hands = []
        dealerHand = Hand(deck=shoe,cards=[])
        for i in range(int(h)):
          hands.append(Hand(deck=shoe,cards=[]))
          hands[i].addCard(0)
        dealerHand.addCard(0)
        for i in range(int(h)):
          hands[i].addCard(0)
          print("Hand "+str(i+1)+": "+str(hands[i])+"\n")
        print("Dealer: ",str(dealerHand)+"\n")

        # On dealer blackjack, with a ten face up, end the hand
        if(dealerHand.val()==10):
          if(shoe.shoe[0].val()==1):
            print(str(shoe.deal(0))+"\n",)
            print("\nDealer blackjack\n")
            for x in hands:
            # If player doesn't also have blackjack, they receive nothing, but if they do, they get their money back
              if(x.val()==21):
                self.balance +=1
            continue

        # On dealer blackjack with an ace face up, end the hand
        elif(dealerHand.val()==11):
          if(shoe.shoe[0].val()==10):
            # Insurance Implementation (stretch goal) would go here
            print(str(shoe.deal(0))+"\n",)
            print("\nDealer blackjack\n")
            for x in hands:
              if(x.val()==21):
                self.balance +=1
            continue

        # Otherwise, start playing
        print("\nKey\nHit: h\nStand: s\nDouble: d\nSplit: v\nSurrender: l\n")
        # Play each hand
        i=0
        # This stores preemptively ended hands
        p = 0
        while i< len(hands):
          # Handles case where cards can be split
          if(len(hands[i].cards)==1):
            hands[i].addCard(1)
          # Initial options are hit, stand, and double (unless it's a split hand and no double after split)
          options = ['h','s']
          if (self.balance >= 1 and not(self.das and hands[i].hasBeenSplit)):
            options.append('d')
          # If surrender is offered, it is added
          if(self.surrender and not hands[i].hasBeenSplit and len(hands[i].cards)==2):
            options.append('l')
          # If the cards are the same rank, split is added. If they're both aces rsa is disabled
          if(self.balance >= 1 and hands[i].cards[0].rank==hands[i].cards[1].rank and not(not self.rsa and hands[i].cards[1].val()==1)):
            options.append('v')

          # Play each hand, removing hands that bust or make natural 21
          while(len(options)>0):
            print("Hand "+str(i+1+p)+": "+str(hands[i].val())+"\n"+str(hands[i])+"\n")
            if(hands[i].val()>21):
                print("\nBust\n")
                hands.remove(hands[i])
                i -= 1
                p+=1
                options = []
                break

            # If the hand has 21, stop playing
            elif(hands[i].val()==21):
                options = []
                if(len(hands[i].cards)==2):
                  # If it's a natural 21, pay it out immediately (dealer doesn't have blackjack in this branch)
                  print("Blackjack!\n")
                  self.balance += 1 + self.blackjack
                  p += 1
                  hands.remove(hands[i])
                  i -= 1
                # Fixed an issue where getting 21 softlocks you
                break

            # Otherwise, get input
            print("Options are: " + str(options) + "\n")
            if bot is not None:
              print("Bot says "+str(bot.decision(options,hands[i],dealerHand,shoe))+"\n")
            c = input()
            # Failsafe
            while c not in options and len(options)>0:
              c = input()

          # When playing, call addCard(1) since the dealer has the 0 card
            match c:
              # Hit
              case 'h':
                hands[i].addCard(1)
                # print("Hand "+str(i+1)+": "+str(hands[i].val())+"\n")
                options = ['h','s']
              # Stand
              case 's':
                options = []
              # Double (costs 1 bet)
              case 'd':
                hands[i].addCard(1)
                print("Hand "+str(i+1)+": "+str(hands[i].val())+"\n"+str(hands[i])+"\n")
                options = []
                hands[i].double = True
                self.balance -= 1
                if(hands[i].val()>21):
                  print("\nBust\n")
                  hands.remove(hands[i])
                  i-=1
                  p+=1
              # Split (costs 1 bet)
              case 'v':
                hands.insert(i, Hand(deck=shoe,cards=[hands[i].cards.pop(1)]))
                i-=1
                # Plays a new hand, so h is increased
                h += 1
                options = []
                self.balance -= 1
              # Surrender: regain half the bet and end the hand
              case 'l':
                options = []
                self.balance += 0.5
                hands.remove(hands[i])
                i-=1
                p += 1
              # This better not be happening
              case _:
                raise ValueError(f"Unexpected decision: {c}")
          i+=1

        # Reveal second card after all hands have been played
        dealerHand.addCard(0)
        if(len(hands)>0):
          while(dealerHand.val()<=16 or (dealerHand.val()==17 and self.h17 and dealerHand.isSoft)):
            dealerHand.addCard(0)
        print("\nDealer hand: "+str(dealerHand.val())+"\n"+str(dealerHand))
        if(dealerHand.val()>21):
          print("\nDealer bust, all remaining hands win\n")
          for o in range(len(hands)):
            print("Hand "+str(o+1)+ " wins "+str(4 if hands[o].double else 2)+"\n")
            self.balance += (4 if hands[o].double else 2)
        else:
          for h in range(len(hands)):
            print("Hand "+str(h+1)+":")
            if hands[h].val() > dealerHand.val():
              self.balance += 4 if hands[h].double else 2
              print("Win "+ str(4 if hands[h].double else 2)+"\n")
            elif hands[h].val() < dealerHand.val():
              print("Loss\n")
            else:
              print("Push "+str(2 if hands[h].double else 1)+"\n")
              self.balance += 2 if hands[h].double else 1
        print("\n\nNext hand\n\n")
      balHistory.append(self.balance)
    plt.plot(balHistory)
    plt.show()

  def simPlay(self, decks=1, shuffle=True, cards=None, penMin=.7, penMax=.8, bot=Bot(), shoes=100):
    balHistory = [self.balance]
    shoesPlayed = 0
    moneyGambled = 0
    while shoesPlayed != shoes:
      if isinstance(bot,PerfectBot):
        print("New shoe starting: " + str(shoesPlayed) + "\n")
      shoesPlayed += 1
      shoe = Shoe(decks=decks, shuffle=shuffle, cards=cards,penMin=penMin, penMax=penMax)
      # Place bets
      while(shoe.play and self.balance > 1):
        h = min(bot.handNum(shoe.shoe),self.balance)
        # Enter 0 to end session or "Wong out"
        if h==0:
          return
        self.balance -= h
        moneyGambled += h

        # Deal cards
        hands = []
        dealerHand = Hand(deck=shoe,cards=[])
        for i in range(int(h)):
          hands.append(Hand(deck=shoe,cards=[]))
          hands[i].addCard(0)
        dealerHand.addCard(0)
        for i in range(int(h)):
          hands[i].addCard(0)

        # On dealer blackjack, with a ten face up, end the hand
        if(dealerHand.val()==10):
          if(shoe.shoe[0].val()==1):
            shoe.deal(0)
            for x in hands:
            # If player doesn't also have blackjack, they receive nothing, but if they do, they get their money back
              if(x.val()==21):
                self.balance +=1
            continue

        # On dealer blackjack with an ace face up, end the hand
        elif(dealerHand.val()==11):
          # Check for insurance, if yes insurance costs 1/2 a bet per hand
          if (bot.insurance(shoe.shoe)):
            for h in hands:
              h.isInsured = True
              self.balance -= 0.5
              moneyGambled += 0.5

          if(shoe.shoe[0].val()==10):
            shoe.deal(0)
            for x in hands:
              if(x.val()==21):
                self.balance +=1
              # Pay out for insured hands ---Is this correct?---
              # What happens if the hand is insured and you have blackjack? Is that even allowed?
              if (x.isInsured):
                self.balance += 1.5
            continue
        # Play each hand
        i=0
        # This stores preemptively ended hands
        p = 0
        while i< len(hands):
          # Handles case where cards can be split
          if(len(hands[i].cards)==1):
            hands[i].addCard(1)
          # Initial options are hit, stand, and double (unless it's a split hand and no double after split)
          options = ['h','s']
          if (self.balance >= 1 and not(self.das and hands[i].hasBeenSplit)):
            options.append('d')
          # If surrender is offered, it is added
          if(self.surrender and not hands[i].hasBeenSplit and len(hands[i].cards)==2):
            options.append('l')
          # If the cards are the same rank, split is added. If they're both aces rsa is disabled
          if(self.balance >= 1 and hands[i].cards[0].rank==hands[i].cards[1].rank and not(not self.rsa and hands[i].cards[1].val()==1)):
            options.append('v')

          # Play each hand, removing hands that bust or make natural 21
          while(len(options)>0):
            if(hands[i].val()>21):
                hands.remove(hands[i])
                i -= 1
                p+=1
                options = []
                break

            # If the hand has 21, stop playing
            elif(hands[i].val()==21):
                options = []
                if(len(hands[i].cards)==2):
                  # If it's a natural 21, pay it out immediately (dealer doesn't have blackjack in this branch)
                  self.balance += 1+self.blackjack
                  p += 1
                  hands.remove(hands[i])
                  i -= 1
                # Fixed an issue where getting 21 softlocks you
                break
            c = bot.decision(options,hands[i],dealerHand, shoe)
            # Failsafe
            while c not in options and len(options)>0:
              c = input()

          # When playing, call addCard(1) since the dealer has the 0 card
            match c:
              # Hit
              case 'h':
                hands[i].addCard(1)
                options = ['h','s']
              # Stand
              case 's':
                options = []
              # Double (costs 1 bet)
              case 'd':
                hands[i].addCard(1)
                options = []
                hands[i].double = True
                self.balance -= 1
                moneyGambled += 1
                if(hands[i].val()>21):
                  hands.remove(hands[i])
                  i-=1
                  p+=1
              # Split (costs 1 bet)
              case 'v':
                hands.insert(i, Hand(deck=shoe,cards=[hands[i].cards.pop(1)]))
                i-=1
                options = []
                self.balance -= 1
                moneyGambled += 1
              # Surrender: regain half the bet and end the hand
              case 'l':
                options = []
                self.balance += 0.5
                hands.remove(hands[i])
                i-=1
                p += 1
              # This better not be happening
              case _:
                raise ValueError(f"Unexpected decision: {c}")
          i+=1

        # Reveal second card after all hands have been played
        dealerHand.addCard(0)
        if(len(hands)>0):
          while(dealerHand.val()<=16 or (dealerHand.val()==17 and self.h17 and dealerHand.isSoft)):
            dealerHand.addCard(0)
        if(dealerHand.val()>21):
          for o in range(len(hands)):
            self.balance += (4 if hands[o].double else 2)
        else:
          for h in range(len(hands)):
            if hands[h].val() > dealerHand.val():
              self.balance += 4 if hands[h].double else 2
            elif hands[h].val() < dealerHand.val():
              continue
            else:
              self.balance += 2 if hands[h].double else 1
      balHistory.append(self.balance)
      if self.balance <= 1:

        break
    # plt.plot(balHistory)
    # plt.show()
    print("Final balance is " + str(self.balance) + " after " + str(shoesPlayed) + " shoes.\nRTP:" + str(1 + (self.balance - self.sbalance)/moneyGambled) + "\n")
    self.balance = self.sbalance
    return balHistory
