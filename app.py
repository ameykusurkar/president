from typing import Optional
import logging
import os

from flask import Flask, jsonify, make_response, request
from flask_inputs import Inputs # type: ignore
from flask_inputs.validators import JsonSchema # type: ignore
from flask_cors import CORS # type: ignore

from models import db
import models
from logic import play_turn, Move, TurnResult

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://" +
        os.environ["PGUSER"] + ":" +
        os.environ.get("PGPASSWORD", "") + "@" +
        os.environ.get("PGHOST", "localhost") + "/" +
        os.environ["PGDATABASE"]
    )

db.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

PLAY_TURN_SCHEMA = {
    "type": "object",
    "properties": {
        "player_id": {
            "type": "string",
        },
        "move": {
            "type": "string",
            "enum": list(m.name for m in Move),
        },
        "card_value": {
            "type": "integer",
            "minimum": 0,
            "exclusiveMaximum": 52,
        },
    },
    "required": ["player_id", "card_value", "move"]
}

CREATE_GAME_SCHEMA = {
    "type": "object",
    "properties": {
        "player_id": {
            "type": "string",
            "minLength": 1,
        },
    },
    "required": ["player_id"]
}

JOIN_GAME_SCHEMA = {
    "type": "object",
    "properties": {
        "player_id": {
            "type": "string",
            "minLength": 1,
        },
    },
    "required": ["player_id"]
}

class PlayTurnInputs(Inputs):
    json = [JsonSchema(schema=PLAY_TURN_SCHEMA)]

class JoinGameInputs(Inputs):
    json = [JsonSchema(schema=JOIN_GAME_SCHEMA)]

class CreateGameInputs(Inputs):
    json = [JsonSchema(schema=CREATE_GAME_SCHEMA)]

def resource_not_found(resource, resource_id):
    response = {
        "error": f"No {resource} found with id: {resource_id}",
    }
    return make_response(jsonify(response), 404)

@app.route('/')
def index():
    return jsonify({ "status": "healthy" })

@app.route("/api/games/<game_id>", methods=["GET"])
def get_game(game_id: str):
    with app.app_context():
        game = models.Game.query.get(game_id)
        if not game:
            return resource_not_found(resource="game", resource_id=game_id)
        return jsonify(game.serialize())

@app.route("/api/games", methods=["POST"])
def create_game():
    inputs = CreateGameInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    with app.app_context():
        game = models.Game()
        db.session.add(game)
        db.session.flush()
        player = models.Player(user_id=request.json["player_id"],
                               game_id=game.id,
                               game_player_index=game.player_count())
        db.session.add(player)
        db.session.commit()
        return jsonify(game.serialize()), 201

@app.route("/api/games/<int:game_id>/join", methods=["POST"])
def join_game(game_id: int):
    inputs = JoinGameInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    with app.app_context():
        game = models.Game.query.get(game_id)
        if not game:
            return resource_not_found(resource="game", resource_id=game_id)
        if not game.is_waiting():
            return { "error": "game_already_started" }, 400

        player_id = request.json["player_id"]
        player_exists = db.session.query(models.Player.id).\
            filter_by(user_id=player_id, game_id=game_id).first()
        if player_exists:
            return { "error": "player_id_already_joined" }, 400

        player = models.Player(user_id=player_id,
                               game_id=game_id,
                               game_player_index=game.player_count())
        db.session.add(player)
        db.session.commit()
        return jsonify(player.serialize()), 201

# TODO: Only game leader can start the game
@app.route("/api/games/<game_id>/start", methods=["POST"])
def start_game(game_id: str):
    with app.app_context():
        game = models.Game.query.get(game_id)
        if not game:
            return resource_not_found(resource="game", resource_id=game_id)
        if not game.is_waiting():
            return {}, 200
        if game.player_count() < 2:
            return { "error": "need_at_least_two_players" }, 400

        game.start()
        db.session.commit()
        return {}, 200

@app.route("/api/games/<game_id>/play", methods=["POST"])
def play_game_turn(game_id: str):
    inputs = PlayTurnInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    with app.app_context():
        game = models.Game.query.get(game_id)
        if not game:
            return resource_not_found(resource="game", resource_id=game_id)
        if game.is_waiting():
            return { "error": "game_not_started" }, 400

        player_id = request.json["player_id"]
        player = models.Player.query.filter_by(user_id=player_id, game_id=game_id).first()
        if not player:
            return resource_not_found(resource="player", resource_id=player_id)

        move = request.json["move"]
        card_value = request.json["card_value"]

        result, events = play_turn(
            game,
            player,
            move=Move[move],
            card=card_value,
        )
        db.session.commit()

        if result == TurnResult.SUCCESS:
            return jsonify({
                "game": game.serialize(),
                "result": result.name,
                "events": list(ev.name for ev in events),
            })
        else:
            return { "error": result.name, "result": result.name }, 400

@app.route("/api/games/<game_id>/players/<player_id>", methods=["GET"])
def get_player(game_id: str, player_id: str):
    with app.app_context():
        game = models.Game.query.get(game_id)
        if not game:
            return resource_not_found(resource="game", resource_id=game_id)

        player = models.Player.query.filter_by(user_id=player_id, game_id=game_id).first()
        if not player:
            return resource_not_found(resource="player", resource_id=player_id)

        return player.serialize_with_playable_cards(game.last_card), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
