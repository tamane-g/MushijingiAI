from Main import *

def makeSampleDeck():
  sampleDeckID = []
  for _ in range(7):
    sampleDeckID.append(1030)
    sampleDeckID.append(1063)
    sampleDeckID.append(1091)
  sampleDeckID.pop(0)
  
  return sampleDeckID

p1 = Player(makeSampleDeck(), name="User")
p2 = Player(makeSampleDeck(), name="AI", isAI=True)
game = GameMaster(p1, p2)
game.runGame()