import pandas as pd
import Cards

df = pd.read_csv("./Cards.csv",index_col=0,
                 dtype={"ID": int,
                        "Category": str,
                        "Name": str,
                        "Cost": int,
                        "HP": int,
                        "Color": str,
                        "Atk_1_method": str,
                        "Atk_1_int": int,
                        "Atk_2_method": str,
                        "Atk_2_int": int,
                        })
print(df.dtypes)

def CardDefine(id: str) -> Cards.Card:
    card_data = df[df["ID"].str.contains(id)]
    match card_data["Category"]:
        case "Insect":
            return Cards.Insect(card_data["Name"],
                                card_data["Cost"],
                                card_data["HP"],
                                card_data["Color"],
                                [(card_data["Atk_1_method"],
                                  card_data["Atk_1_int"]),
                                 (card_data["Atk_2_method"],
                                  card_data["Atk_2_int"])])

class Player:
    def __init__(self, DeckIDList: list[str]) -> None:
        self.DeckIDList = DeckIDList

class GameMaster:
    def __init__(self, p1: Player, p2: Player) -> None:
        self.PlayerA = p1
        self.PlayerB = p2