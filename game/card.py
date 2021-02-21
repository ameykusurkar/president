from typing import Union

FACE_RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
FACE_SUITS = ["DIAMONDS", "CLUBS", "HEARTS", "SPADES"]

class Card:
    def __init__(self, value: int):
        if not 0 <= value < 52:
            raise ValueError(f"Cannot build Card from value: {value}")
        self.value = value
        self.rank = self.value % 13
        self.suit = self.value // 13

    def __repr__(self):
        return f"Card({self.value})"

    def __str__(self):
        return f"{FACE_RANKS[self.rank]} OF {FACE_SUITS[self.suit]}"

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value

    def serialize(self) -> dict[str, Union[str, int]]:
        return { "value": self.value, "rank": self.rank, "suit": self.suit }
