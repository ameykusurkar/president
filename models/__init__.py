from typing import Any
from random import shuffle

from sqlalchemy import Column, Integer, Text, ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore

from models.base import db
from models.player import Player
import card as Card

class Game(db.Model): # type: ignore
    id = Column(Integer, primary_key=True)
    status = Column(Text, nullable=False)
    turn_number = Column(Integer, nullable=False)
    current_player_index = Column(Integer, nullable=True)
    last_card = Column(Integer, nullable=True)
    last_card_player_index = Column(Integer, nullable=True)
    players = relationship("Player", backref="game", lazy=True)

    def __init__(self):
        self.status = "waiting"
        self.turn_number = 0

    def start(self):
        player_count = self.player_count()
        hands = deal_hands(player_count)
        for player, hand in zip(self.players, hands):
            if 0 in hand:
                # Player with 3 of diamonds starts
                self.current_player_index = player.game_player_index
                self.last_card_player_index = player.game_player_index
            player.hand = hand
        self.status = "playing"

    def is_waiting(self) -> bool:
        return self.status == "waiting"

    def player_count(self) -> int:
        return Player.query.filter_by(game_id=self.id).count()

    def serialize(self) -> dict[str, Any]:
        current_player = Player.query.\
            filter_by(game_id=self.id, game_player_index=self.current_player_index).first()
        player_ids = list(p.user_id for p in self.players)
        return {
            "id": self.id,
            "turn_number": self.turn_number,
            "current_player_index": self.current_player_index,
            "current_player_id": current_player.user_id if current_player else None,
            "last_card": Card.serialize(self.last_card) if self.last_card else None,
            "player_ids": player_ids,
            "status": self.status,
        }

def deal_hands(n: int) -> list[list[int]]:
    deck = [i for i in range(52)]
    shuffle(deck)
    hands: list[list[int]] = [[] for _ in range(n)]
    counter = 0
    while deck:
      hands[counter].append(deck.pop())
      counter = (counter + 1) % n
    return hands
