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
    self.currentPlayerOrder = 0
  
  def runGame(self) -> None:
    self.setAllPlayerCards() # 縄張りや手札をセットアップ
    self.setPlayerOrder() # 先攻後攻を決める
    
    while not self.gameEnd:
      for currentPlayer in self.playerOrder:
        if self.gameEnd:
          break
        self.refreshBattleZone()
        self.executeTurn(currentPlayer)
        self.currentPlayerOrder = not self.currentPlayerOrder
  
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

  def refreshBattleZone(self) -> None:
    for player in self.playerOrder:
      for insect in player.BattleZone:
        insect.reset()

  def userTurnExecution(self, executorPlayer: Player) -> None:
    View.showTurn(self.turnCount)
    View.showCards(executorPlayer.Hands)
    num = View.requireMannaSet(len(executorPlayer.Hands)-1)
    if num != -1:
      self.PlayerPutCardToMannaZone(executorPlayer, num)
    self.PlayerCountMannas(executorPlayer)
    
    while(True):
      self.userShowCards(executorPlayer)
      num = View.requireAction(self.userGetInputtableKeys(executorPlayer))
      if num == -1:
        break
      self.userActionFromKey(executorPlayer, num)
    print()
  
  def userShowCards(self, executorPlayer: Player) -> None:
    View.showText("Battle zone: ")
    View.showCards(executorPlayer.BattleZone)
    View.showText("Hand: ")
    View.showCards(executorPlayer.Hands, 20)
  
  def userGetInputtableKeys(self, executorPlayer: Player) -> list[int]:
    playable = self.getPlayableCardAndKeys(executorPlayer)[0]
    attackable = self.getAttackableInsectAndKeys(executorPlayer)[0]
    
    result = []
    for index,_ in enumerate(attackable):
      result.append(index)
    for index,_ in enumerate(playable):
      result.append(index + 20)
    
    return result
  
  def userActionFromKey(self, executorPlayer: Player, key: int) -> None:
    if key >= 20:
      self.PlayerPlayCardFromHand(executorPlayer, key-20)
    else:
      selectedInsect = self.getAttackableInsectAndKeys(executorPlayer)[1][key]
      inputtableValue, inputtableAtk = self.getSelectableAttackAndKeys(selectedInsect)
      selectedAtkIndex = View.requireSelectAttack(inputtableValue)
      if selectedAtkIndex == -1:
        return
      atkMethod, atkValue = inputtableAtk[selectedAtkIndex]
      opponentPlayer = self.getOpponentPlayer()
      targettables = self.getTargettableInsectAndKeys(opponentPlayer)
      View.showCards(targettables[1])
      
      if len(opponentPlayer.BattleZone) == 0:
        self.PlayerBeDamaged(opponentPlayer, isDirect=True)
      else:
        targetInsectNum = View.requireTargetInsect(targettables[0])
        if targetInsectNum == -1:
          return
        self.InsectAttack(opponentPlayer, targetInsectNum, atkMethod, atkValue)
        
      selectedInsect.isAttacked = True
    
  def AI_TurnExecution(self, executorPlayer: Player) -> None:
    View.showTurn(self.turnCount)
    num = AI.requireMannaSet(executorPlayer.Hands)
    if num != -1:
      self.PlayerPutCardToMannaZone(executorPlayer, num)
    self.PlayerCountMannas(executorPlayer)
    
    while(True):
      buf = self.getPlayableCardAndKeys(executorPlayer)
      num = AI.requireAction(buf[0], buf[1])
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
  
  def InsectAttack(self, targetPlayer: Player, targetInsectNum: int, atkMethod: str, atkValue: int):
    match atkMethod:
      case "Simple":
        self.InsectOnBattleZoneBeDamaged(targetPlayer, targetInsectNum, atkValue)
        
  def InsectOnBattleZoneBeDamaged(self, owner: Player, BattleZoneOrder: int, value: int, isEffectDamage: bool = False):
    insect = owner.BattleZone[BattleZoneOrder]
    insect.NowHP -= value
    View.showText(f"{insect.name}に{value}のダメージ！")
    if insect.NowHP <= 0:
      View.showText(f"{insect.name}は破壊された！")
      owner.BattleZone.pop(BattleZoneOrder)
      owner.Trash.append(insect)
      if not isEffectDamage:
        self.PlayerBeDamaged(owner)

  def PlayerDrawDeck(self, executorPlayer: Player) -> None:
    # ライブラリアウト時
    if not executorPlayer.Deck:
      self.libraryOutJudgment()
      return
    executorPlayer.Hands.append(executorPlayer.Deck.pop(0))

  def PlayerBeDamaged(self, beDamagedPlayer: Player, isDirect: bool = False) -> None:
    if len(beDamagedPlayer.Shields) == 0 and isDirect:
      self.gameEnd = True
      return
    elif len(beDamagedPlayer.Shields) == 0:
      return
    View.showText(f"{beDamagedPlayer.Name}の縄張りが一枚破壊された！")
    card = beDamagedPlayer.Shields.pop(0)
    beDamagedPlayer.Hands.append(card)


  def PlayerPutCardToMannaZone(self, executorPlayer: Player, handNum: int) -> None:
    card = executorPlayer.Hands.pop(handNum)
    View.showText(f"{executorPlayer.Name}が{card.name}をエサ場に置きました")
    executorPlayer.MannaZone.append(card)

  def PlayerPlayCardFromHand(self, executorPlayer: Player, handNum: int) -> None:
    card = executorPlayer.Hands.pop(handNum)
    if not self.isCardPlayable(executorPlayer, card):
      executorPlayer.Hands.insert(handNum, card)
      return
    
    View.showText(f"{executorPlayer.Name}が{card.name}をプレイしました")
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
    for index,card in enumerate(executorPlayer.Hands):
      if self.isCardPlayable(executorPlayer, card):
        resultIndex.append(index)
        resultCards.append(card)
    return resultIndex, resultCards
  
  def getAttackableInsectAndKeys(self, executorPlayer: Player) -> tuple[list[int], list[Cards.Insect]]:
    resultIndex = []
    resultCards = []
    for index,insect in enumerate(executorPlayer.BattleZone):
      if not insect.isAttacked:
        resultIndex.append(index)
        resultCards.append(insect)
    return resultIndex, resultCards
  
  def getTargettableInsectAndKeys(self, targetPlayer: Player) -> tuple[list[int], list[Cards.Insect]]:
    resultIndex = []
    resultCards = []
    for index,insect in enumerate(targetPlayer.BattleZone):
      resultIndex.append(index)
      resultCards.append(insect)
    return resultIndex, resultCards
  
  def getSelectableAttackAndKeys(self, insect: Cards.Insect) -> tuple[list[int], list[tuple[str, int]]]:
    inputtableIndex = []
    inputtableAtk = []
    for index,atk in enumerate(insect.atkList):
      if str(atk[0]) != "nan":
        print(f"{index}: {atk[0]} {atk[1]}")
        inputtableIndex.append(index)
        inputtableAtk.append(atk)
    return inputtableIndex, inputtableAtk
  
  def getOpponentPlayer(self) -> Player:
    return self.playerOrder[not self.currentPlayerOrder]
  
  def libraryOutJudgment(self) -> None:
    if len(self.PlayerA.Shields) > len(self.PlayerB.Shields):
      print("PlayerAの勝ち")
    elif len(self.PlayerA.Shields) == len(self.PlayerB.Shields):
      print("引き分け")
    else:
      print("PlayerBの勝ち")
    self.gameEnd = True