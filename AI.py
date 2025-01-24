import Cards
import random

def requireManaSet(cards: list[Cards.Card]) -> int:
    return random.randint(-1, len(cards)-1)