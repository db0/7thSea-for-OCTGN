    # Python Scripts for the 7th Sea CCG definition for OCTGN
    # Copyright (C) 2012  Konstantine Thoukydides

    # This python script is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this script.  If not, see <http://www.gnu.org/licenses/>.


#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
import re

phases = [
    '{} is currently in the Pre-game Setup Phase'.format(me),
    "Phase 1: Determine Your Turn Order.",
    "Phase 2: Actions.",
    "Phase 3: Draw Cards.",
    "Phase 4: Untack."]

### Misc ###

loud = 'loud' # So that I don't have to use the quotes all the time in my function calls
silent = 'silent' # Same as above
Xaxis = 'x'  # Same as above
Yaxis = 'y'	 # Same as above

#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is
playerFaction = None # Variable to keep track of the player's Faction.
PlayerColor = "#" # Variable with the player's unique colour.

#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------
   
def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   if playerside == None:  # Has the player selected a side yet? If not, then...
      if len(players) < 3:
         playeraxis = Xaxis
         if confirm("Will you play on the right side?"): # Ask which side they want
            playerside = 1 # This is used to swap between the two halves of the X axis of the play field. Positive is on the left.
         else:
            playerside = -1 # Negative is on the right.
      else:
         askside = askInteger("On which side do you want to setup?: 1 = Right, 2 = Left, 3 = Bottom, 4 = Top, 0 = None (All your cards will be put in the middle of the table and you'll have to arrange them yourself", 1) # Ask which axis they want,
         if askside == 1:
            playeraxis = Xaxis
            playerside = 1
         elif askside == 2:
            playeraxis = Xaxis
            playerside = -1
         elif askside == 3:
            playeraxis = Yaxis
            playerside = 1
         elif askside == 4:
            playeraxis = Yaxis
            playerside = -1
         else:
            playeraxis = None  
            playerside = 0
         
def num (s): 
# This function reads the value of a card and returns an integer. For some reason integer values of cards are not processed correctly
# see bug 373 https://octgn.16bugs.com/projects/3602/bugs/188805
# This function will also return 0 if a non-integer or an empty value is provided to it as it is required to avoid crashing your functions.
#   if s == '+*' or s == '*': return 0
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0

def defPlayerColor():
# Provide a random highlight colour for the player which we use to simulate ownership
   global PlayerColor
   if len(PlayerColor) == 7 : return
   RGB = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
   for i in range(6): PlayerColor += RGB[rnd(0,15)]

def cwidth(card, divisor = 10): 
# This function is used to always return the width of the card plus an offset that is based on the percentage of the width of the card used.
# The smaller the number given, the less the card is divided into pieces and thus the larger the offset added.
# For example if a card is 80px wide, a divisor of 4 will means that we will offset the card's size by 80/4 = 20.
# In other words, we will return 1 + 1/4 of the card width. 
# Thus, no matter what the size of the table and cards becomes, the distances used will be relatively the same.
# The default is to return an offset equal to 1/10 of the card width. A divisor of 0 means no offset.
   if divisor == 0: offset = 0
   else: offset = card.width() / divisor
   return (card.width() + offset)

def cheight(card, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = card.height() / divisor
   return (card.height() + offset)
   
def download_o8c(group,x=0,y=0):
   openUrl("http://dbzer0.com/pub/7thSea/sets/7thSea-Sets-Bundle.o8c")
#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def showCurrentPhase(): # Just say a nice notification about which phase you're on.
   notify(phases[shared.Phase].format(me))
   
def nextPhase(group, x = 0, y = 0):  
# Function to take you to the next phase. 
   mute()
   if shared.Phase == 4: 
      shared.Phase = 1 # In case we're on the last phase , go back to the first game phase
   else: shared.Phase += 1 # Otherwise, just move up one phase
   showCurrentPhase()
	
def goToPhase1(group, x = 0, y = 0): 
   mute()
   shared.Phase = 1
   showCurrentPhase()

def goToPhase2(group, x = 0, y = 0): 
   mute()
   shared.Phase = 2
   showCurrentPhase()
	
def goToPhase3(group, x = 0, y = 0): 
   mute()
   shared.Phase = 3
   showCurrentPhase()

def goToPhase4(group, x = 0, y = 0):  
   mute()
   shared.Phase = 4
   showCurrentPhase()   

def Pass(group, x = 0, y = 0): # Player says pass. A very common action.
   notify('{} Passes.'.format(me))

def tack(card, x = 0, y = 0): # Boot or Unboot a card. I.e. turn it 90 degrees sideways or set it straight.
   mute()
   card.orientation ^= Rot90 # This function rotates the card +90 or -90 degrees depending on where it was.
   if card.orientation & Rot90 == Rot90: # if the card is now at 90 degrees, then announce the card was booted
      notify('{} tacks {}'.format(me, card))
   else: # if the card is now at 0 degrees (i.e. straight up), then announce the card was unbooted
      notify('{} untacks {}'.format(me, card))
		
def sink(cards, x = 0, y = 0): # Sink a card. I.e. kill it and send it to the Sunk Pile (i.e.graveyard)
   mute()
   for card in cards:
      cardowner = card.owner 
      card.moveTo(cardowner.piles['Sunk Pile']) 
      notify("{} has sunk {}.".format(me, card))

def discard(cards, x = 0, y = 0): # Discard a card.
   mute()
   for card in cards:	# Can be done at more than one card at the same time, since attached cards follow their parent always.
      cardowner = card.owner
      notify("{} has discarded {}.".format(me, card))
      card.moveTo(cardowner.piles['Discard Pile']) # Cards aced need to be sent to their owner's discard pile
    
def inspectCard(card, x = 0, y = 0): # This function shows the player the card text, to allow for easy reading until High Quality scans are procured.
   confirm("{}".format(card.text)) 
   

#---------------------------------------------------------------------------
# Marker functions
#---------------------------------------------------------------------------

 
#---------------------------------------------------------------------------
# Hand and Deck actions
#---------------------------------------------------------------------------



def shuffle(group): # A simple function to shuffle piles
   group.shuffle()

def reshuffle(group = me.piles['Discard Pile']): # This function reshuffles the player's discard pile into their deck.
   mute()
   Deck = me.Deck # Just to save us some repetition
   for card in group: card.moveTo(Deck) # Move the player's cards from the discard to their deck one-by-one.
   random = rnd(100, 10000) # Bug 105 workaround. This delays the next action until all animation is done. 
                           # see https://octgn.16bugs.com/projects/3602/bugs/102681
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled their {} into their Deck.".format(me, group.name)) # And inform everyone.

def draw(group = me.Deck): # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0: # In case the deck is empty, invoke the reshuffle function.
      notify("{}'s Deck empty. Will reshuffle discard pile".format(me))
      reshuffle()
   group.top().moveTo(me.hand)
   notify("{} draws a card.".format(me))   
   
def drawMany(group, count = None, notification = loud): # This function draws a variable number cards into the player's hand.
   mute()
   if count == None: count = askInteger("Draw how many cards to your Hand?", 3) # Ask the player how many cards they want.
   for i in range(0, count): 
      if len(group) == 0: reshuffle() # If before moving a card the deck is empty, reshuffle.
      group.top().moveTo(me.hand) # Then move them one by one into their play hand.
   if notification == loud : notify("{} draws {} cards to their hand.".format(me, count)) # And if we're "loud", notify what happened.   
   
def handDiscard(card, x = 0, y = 0): # Discard a card from your hand.
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {}.".format(me, card))  

def randomDiscard(group): # Discard a card from your hand randomly.
   mute()
   card = group.random() # Select a random card
   if card == None: return # If hand is empty, do nothing.
   notify("{} randomly discards a card.".format(me)) # Inform that a random card was discarded
   card.moveTo(me.piles['Discard Pile']) # Move the card in the discard pile.
	
def permRemove(card): # Takes a card from the boot hill and moves it to the shared "removed from play" pile.
   mute()
   card.moveTo(shared.piles['Removed from Play'])
   notify("{} has permanently removed {} from play".format(me, card))
   
def setup(group):
# This function is usually the first one the player does. It will setup their ship and captain on the top or bottom of the playfield 
   if shared.Phase == 0: # First check if we're on the pre-setup game phase. 
                         # As this function will play your whole hand and wipe your counters, we don't want any accidents.
      global playerside, playerFaction # Import some necessary variables we're using around the game.
      mute()
      chooseSide() # The classic place where the players choose their side.
      concat_captain = '' # A string to remember our Captain's name
      concat_ship = '' # A string to remember our ship's name
      me.Deck.shuffle() # First let's shuffle our deck now that we have the chance.
      defPlayerColor() # Randomize the player's unique colour.       
      if len(table) == 0: # Only setup the Seas tokens if nobody has setup their side yet.
         TradeSea = table.create("7a5eea90-fbf1-428b-8a77-276f9595c895", 0, 0, 1, True)
         TradeSea.moveToTable(0, -3 * cheight(TradeSea,0) ,0) # Move it to the far top
         FrothingSea = table.create("9b8f6f87-20b9-4ef3-b2e8-9073ac23f4e8", 0, 0, 1, True)
         FrothingSea.moveToTable(0, -(3 / 2) * cheight(FrothingSea,3) ,0) # Move it to the top
         LaBoca = table.create("aa019c17-0c60-4d80-be22-88a1356ea71f", 0, 0, 1, True)
         LaBoca.moveToTable(0, -2 / cheight(LaBoca,0) ,0) # Move it to the middle
         ForbiddenSea = table.create("130ec464-b05d-4dfc-91fe-b880432b38dd", 0, 0, 1, True)
         ForbiddenSea.moveToTable(0, (3 / 2) * cheight(ForbiddenSea,3) ,0) # Move it to the bot
         TheMirror = table.create("99fc650e-522b-402d-b776-18ec9ce8514d", 0, 0, 1, True)
         TheMirror.moveToTable(0, 3 * cheight(TheMirror,0) ,0) # Move it to the far bot
      for card in group: # For every card in the player's hand... (which should be a ship and a Captain usually)
         if card.type == "ships" :  # If it's the Ship
            card.moveToTable(shipDistance(card), 0)
            playerFaction = card.Faction # We make a note of the faction the player is playing today.
            concat_ship += card.name # And we save the name.
         elif card.type == "captains" : # If it's a Captain...
            card.moveToTable(shipDistance(card) + cardDistance(card), 0) 
            concat_captain += card.name 
      drawMany(me.Deck, 7, silent)
      notify("{} is playing {}. They are sailing the {} with {} as their Captain.".format(me, playerFaction, concat_ship, concat_captain))  
   else: whisper('You can only setup your starting cards during the Pre-Game setup phase') # If this function was called outside the pre-game setup phase
                                                                                           # We assume a mistake and stop.
                                                                                           
def shipDistance(card):
# This function retusn the distance from the middle each player's home will be setup towards their playerSide. 
# This makes the code more readable and allows me to tweak these values from one place
   if playeraxis == Xaxis:
      return (playerside * cwidth(card) * 3) # players on the X axis, are placed 5 times a card's width towards their side (left or right)
   elif playeraxis == Yaxis:
      return (playerside * cheight(card) * 5) # players on the Y axis, are placed 3 times a card's height towards their side (top or bottom)

def cardDistance(card):
# This function returns the size of the card towards a player's side. 
# This is useful when playing cards on the table, as you can always manipulate the location
#   by multiples of the card distance towards your side
# So for example, if a player is playing on the bottom side. This function will always return a positive cardheight.
#   Thus by adding this in a moveToTable's y integer, the card being placed will be moved towards your side by one multiple of card height
#   While if you remove it from the y integer, the card being placed will be moved towards the centre of the table by one multiple of card height.
   if playeraxis == Xaxis:
      return (playerside * cwidth(card))
   elif playeraxis == Yaxis:
      return (playerside * cheight(card))                                                                                           