import Cards

def showTurn(turnCount: int) -> None:
  print(f"{'先攻' if turnCount % 2 == 0 else '後攻'} {(turnCount//2) + 1}ターン目")

def showCards(cards: list[Cards.Card]) -> None:
  for count,card in enumerate(cards):
    if issubclass(Cards.Insect, type(card)):
      print(f"{count}: {card.name} {card.cost}c {card.color} {card.hp}HP")

def requireManaSet(inputRange: int) -> None:
  while True:
    num = int(input("エサ場にセットするカードの番号を選んでください: "))
    if num <= inputRange:
      return num
    else:
      print("値が不正です")