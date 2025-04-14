import pandas as pd
import random
import Cards
import View
import AI

df = pd.read_csv("./Cards.csv",index_col=0,
                 dtype={"ID": int,
                        "Category": str,
                        "Name": str,
                        "Cost": int,
                        "HP": int,
                        "Color": str,
                        "Atk_1_method": str,
                        "Atk_1_value": int,
                        "Atk_2_method": str,
                        "Atk_2_value": int,
                        })
print(df.keys())
print(df)

# idからCardクラスのインスタンスを定義
def CardDefine(id: int) -> Cards.Card:
  card_data = df.loc[id]
  match card_data["Category"]:
    case "Insect":
      return Cards.Insect(card_data["Name"],
                          card_data["Cost"],
                          card_data["HP"],
                          card_data["Color"],
                          [(card_data["Atk_1_method"],
                            card_data["Atk_1_value"]),
                            (card_data["Atk_2_method"],
                            card_data["Atk_2_value"])])

class Player:
  def __init__(self, DeckIDList: list[str], isAI: bool = False, name: str = "NoName") -> None:
    self.DeckIDList = DeckIDList
    self.Name       = name
    
    self.Deck       = []
    self.Hands      = []
    self.Trash      = []
    self.Shields    = []
    self.MannaZone  = []
    self.BattleZone = []
    
    self.mannas     = 0
    self.isAI       = isAI
    
    self.registDeck()
    self.shuffleDeck()
  
  def registDeck(self) -> None:
    for card_id in self.DeckIDList:
      self.Deck.append(CardDefine(card_id))
  
  def shuffleDeck(self) -> None:
    random.shuffle(self.Deck)
  
  def setCards(self) -> None:
    for _ in range(6):
      self.Shields.append(self.Deck.pop(0))
    for _ in range(4):
      self.Hands.append(self.Deck.pop(0))

class GameMaster:
  def __init__(self, p1: Player, p2: Player) -> None:
    self.PlayerA = p1
    self.PlayerB = p2
    self.playerOrder = [self.PlayerA, self.PlayerB]
    self.turnCount = 0
    self.gameEnd = False
  
  def runGame(self) -> None:
    self.setAllPlayerCards() # 縄張りや手札をセットアップ
    self.setPlayerOrder() # 先攻後攻を決める
    
    while not self.gameEnd:
      for currentPlayer in self.playerOrder:
        if self.gameEnd:
          break
        self.executeTurn(currentPlayer)
  
  def executeTurn(self, currentPlayer: Player) -> None:
    # ドロー処理
    if not self.isFirstTurn():
      self.PlayerDrawDeck(currentPlayer)
    
    if self.gameEnd:
      return
    
    # AIか人間かで処理を分ける
    if currentPlayer.isAI:
      self.AI_TurnExecution(currentPlayer)
    else:
      self.userTurnExecution(currentPlayer)
    
    self.turnCount += 1 # ターン数をインクリメント

  def userTurnExecution(self, executorPlayer: Player) -> None:
    View.showTurn(self.turnCount)
    View.showCards(executorPlayer.Hands)
    num = View.requireMannaSet(len(executorPlayer.Hands)-1)
    if num != -1:
      self.PlayerPutCardToMannaZone(executorPlayer, num)
    self.PlayerCountMannas(executorPlayer)
    
    while(True):
      View.showCards(executorPlayer.Hands)
      num = View.requirePlayCard(self.getPlayableCardAndKeys(executorPlayer)[0])
      if num == -1:
        break
      self.PlayerPlayCardFromHand(executorPlayer, num)
  
  def AI_TurnExecution(self, executorPlayer: Player) -> None:
    View.showTurn(self.turnCount)
    num = AI.requireMannaSet(executorPlayer.Hands)
    if num != -1:
      self.PlayerPutCardToMannaZone(executorPlayer, num)
    self.PlayerCountMannas(executorPlayer)
    
    while(True):
      buf = self.getPlayableCardAndKeys(executorPlayer)
      num = AI.requirePlayCard(buf[0], buf[1])
      if num == -1:
        break
      self.PlayerPlayCardFromHand(executorPlayer, num)

  def isFirstTurn(self) -> bool:
    return self.turnCount == 0
  
  def setPlayerOrder(self) -> None:
    random.shuffle(self.playerOrder)

  def setAllPlayerCards(self) -> None:
    for executorPlayer in self.playerOrder:
      executorPlayer.setCards()

  def PlayerDrawDeck(self, executorPlayer: Player) -> None:
    # ライブラリアウト時
    if not executorPlayer.Deck:
      self.libraryOutJudgment()
      return
    executorPlayer.Hands.append(executorPlayer.Deck.pop(0))

  def PlayerPutCardToMannaZone(self, executorPlayer: Player, handNum: int) -> None:
    card = executorPlayer.Hands.pop(handNum)
    print(f"{executorPlayer.Name}が{card.name}をエサ場に置きました")
    executorPlayer.MannaZone.append(card)

  def PlayerPlayCardFromHand(self, executorPlayer: Player, handNum: int) -> None:
    card = executorPlayer.Hands.pop(handNum)
    if not self.isCardPlayable(executorPlayer, card):
      executorPlayer.Hands.insert(handNum, card)
      return
    
    print(f"{executorPlayer.Name}が{card.name}をプレイしました")
    executorPlayer.mannas -= card.cost
    if issubclass(Cards.Insect, type(card)):
      executorPlayer.BattleZone.append(card)
    else:
      raise Exception
  
  def PlayerCountMannas(self, executorPlayer: Player) -> None:
    executorPlayer.mannas = len(executorPlayer.MannaZone)
  
  def isPlayersMannaEnough(self, executorPlayer: Player, card: Cards.Card) -> bool:
    return card.cost <= executorPlayer.mannas
  
  def isCardPlayable(self, executorPlayer: Player, card: Cards.Card) -> bool:
    return self.isPlayersMannaEnough(executorPlayer, card)

  def getPlayableCardAndKeys(self, executorPlayer: Player) -> tuple[list[int], list[Cards.Card]]:
    resultIndex = []
    resultCards = []
    for (index, card) in enumerate(executorPlayer.Hands):
      if self.isCardPlayable(executorPlayer, card):
        resultIndex.append(index)
        resultCards.append(card)
    return resultIndex, resultCards
  
  def libraryOutJudgment(self) -> None:
    if len(self.PlayerA.Shields) > len(self.PlayerB.Shields):
      print("PlayerAの勝ち")
    elif len(self.PlayerA.Shields) == len(self.PlayerB.Shields):
      print("引き分け")
    else:
      print("PlayerBの勝ち")
    self.gameEnd = True

"""  def InsectAtkChoice(executorPlayer: Player, executorInsect: Cards.Insect, atkMethod: str, atkInt: int):
    match atkMethod:
      case "Simple":
        """