from flask_sqlalchemy import SQLAlchemy # type: ignore

db = SQLAlchemy()

class Game(db.Model): # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=False)
    turn_number = db.Column(db.Integer, nullable=False)
    current_player_index = db.Column(db.Integer, nullable=False)
    last_card = db.Column(db.Integer, nullable=True)
    last_card_player_index = db.Column(db.Integer, nullable=True)
