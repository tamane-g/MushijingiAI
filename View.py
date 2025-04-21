import Cards
from math import isnan

def showTurn(turnCount: int) -> None:
  print(f"{'先攻' if turnCount % 2 == 0 else '後攻'} {(turnCount//2) + 1}ターン目")

def showText(text: str) -> None:
  print(text)

def showCards(cards: list[Cards.Card], addend: int = 0) -> None:
  for index,card in enumerate(cards):
    if issubclass(Cards.Insect, type(card)):
      print(f"{index + addend}: {card.name} {card.cost}c {card.color} {card.NowHP}HP")

def requireMannaSet(inputRange: int) -> int:
  while True:
    num = int(input("エサ場にセットするカードの番号を選んでください: "))
    print()
    if -1 <= num and num <= inputRange:
      return num
    else:
      print("値が不正です")

def requireAction(inputtableValues: list[int]) -> int:
  while True:
    print(inputtableValues)
    num = int(input("プレイするカードの番号を選んでください: "))
    print()
    
    if num == -1 or num in inputtableValues:
      return num
    else:
      print("このカードはプレイできません")
      
def requireTargetInsect(inputtableValues: list[int]) -> int:
  while True:
    num = int(input("攻撃対象の番号を選んでください: "))
    print()
    
    if num == -1 or num in inputtableValues:
      return num
    else:
      print("このカードはプレイできません")
      
def requireSelectAttack(inputtable: list[int]) -> int:
  while True:
    num = int(input("使用する攻撃を選んでください: "))
    print()
    if num == -1 or num in inputtable:
      return num
    else:
      print("値が不正です")