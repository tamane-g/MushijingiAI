from abc import ABC

class Card(ABC):
    def __init__(self, name: str, cost: int) -> None:
        self.name = name
        self.cost = cost

class Insect(Card):
    def __init__(self, name: str, cost: int, hp: int, color: str, atkList: list[tuple[str,int]]) -> None:
        super().__init__(name, cost)
        self._BaseHP   = hp
        self.NowHP     = hp
        self.color     = color
        self.atkList   = atkList
        self.isAttacked = False
    
    def reset(self):
        self.NowHP      = self._BaseHP
        self.isAttacked = False