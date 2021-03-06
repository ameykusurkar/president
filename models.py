from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy import Column, Integer, Text, ForeignKey # type: ignore
from sqlalchemy.types import ARRAY # type: ignore
from sqlalchemy.orm import relationship # type: ignore

from game import PlayerStatus

db = SQLAlchemy()

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

class Player(db.Model): # type: ignore
    id = Column(Integer, primary_key=True)
    user_id = Column(Text, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    status = Column(Text, nullable=False)
    hand = Column(ARRAY(Integer), nullable=True)

    def __init__(self, user_id: str, game_id: int):
        self.user_id = user_id
        self.game_id = game_id
        self.status = PlayerStatus.ACTIVE.name
