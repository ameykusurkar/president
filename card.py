from typing import Union

FACE_RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
FACE_SUITS = ["DIAMONDS", "CLUBS", "HEARTS", "SPADES"]

def rank(card: int) -> int:
    return card % 13

def suit(card: int) -> int:
    return card // 13

def description(card: int) -> str:
    return f"{FACE_RANKS[rank(card)]} OF {FACE_SUITS[suit(card)]}"

def serialize(card: int) -> dict[str, Union[str, int]]:
    return {
        "value": card,
        "rank": rank(card),
        "suit": suit(card),
        "description": description(card),
    }

def is_playable(card: int, top_card: int) -> bool:
    return rank(card) >= rank(top_card)
