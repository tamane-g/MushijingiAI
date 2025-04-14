import Cards

def showTurn(turnCount: int) -> None:
  print(f"{'先攻' if turnCount % 2 == 0 else '後攻'} {(turnCount//2) + 1}ターン目")

def showCards(cards: list[Cards.Card]) -> None:
  for count,card in enumerate(cards):
    if issubclass(Cards.Insect, type(card)):
      print(f"{count}: {card.name} {card.cost}c {card.color} {card.NowHP}HP")

def requireMannaSet(inputRange: int) -> int:
  while True:
    num = int(input("エサ場にセットするカードの番号を選んでください: "))
    print()
    if -1 <= num and num <= inputRange:
      return num
    else:
      print("値が不正です")

def requirePlayCard(inputtableValues: list[int]) -> int:
  
  while True:
    print(inputtableValues)
    num = int(input("プレイするカードの番号を選んでください: "))
    print()
    
    if num == -1 or num in inputtableValues:
      return num
    else:
      print("このカードはプレイできません")