from enum import Enum
from typing import Any, Optional

from sqlalchemy import Column, Integer, Text, ForeignKey # type: ignore
from sqlalchemy.types import ARRAY # type: ignore

from models.base import db
from serialize import serialize_iterable
import card as Card

class PlayerStatus(str, Enum):
    ACTIVE   = "ACTIVE"
    PASSED   = "PASSED"
    FINISHED = "FINISHED"

class Player(db.Model): # type: ignore
    id = Column(Integer, primary_key=True)
    user_id = Column(Text, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game_player_index = Column(Integer, nullable=False)
    status = Column(Text, nullable=False)
    hand = Column(ARRAY(Integer), nullable=True)

    def __init__(self, user_id: str, game_id: int, game_player_index: int):
        self.user_id = user_id
        self.game_id = game_id
        self.game_player_index = game_player_index
        self.status = PlayerStatus.ACTIVE.name

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "game_id": self.game_id,
            "game_player_index": self.game_player_index,
            "user_id": self.user_id,
            "hand": [Card.serialize(c) for c in self.hand] if self.hand else self.hand,
            "status": self.status,
        }

    def serialize_with_playable_cards(self, top_card: Optional[int]) -> dict[str, Any]:
        serialized = self.serialize()
        for card in serialized["hand"]:
            card["playable"] = (top_card is None) or Card.is_playable(card["value"], top_card)
        return serialized
