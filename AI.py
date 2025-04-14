import Cards
import random

def requireMannaSet(cards: list[Cards.Card]) -> int:
    return random.randint(-1, len(cards)-1)

def requirePlayCard(inputtableValues:list[int], playableCards: list[Cards.Card]) -> int:
    values = inputtableValues
    values.append(-1)
    return random.choice(values)