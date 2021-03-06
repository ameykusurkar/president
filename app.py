from typing import Optional
import logging
import os

from flask import Flask, jsonify, make_response, request
from flask_inputs import Inputs # type: ignore
from flask_inputs.validators import JsonSchema # type: ignore
from flask_cors import CORS # type: ignore

from models import db
import models
from game import Game, Move, Card, TurnResult

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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

pending_games: dict[str, list[str]] = {}
games: dict[str, Game] = {}

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
        if game:
            player_ids = list(p.user_id for p in game.players)
            return jsonify({
                "player_ids": player_ids,
                "status": game.status,
            })
    if game_id in games:
        return jsonify(games[game_id].serialize())

    return resource_not_found(resource="game", resource_id=game_id)

@app.route("/api/games", methods=["POST"])
def create_game():
    inputs = CreateGameInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    response = {}
    with app.app_context():
        game = models.Game()
        db.session.add(game)
        db.session.flush()
        response["game_id"] = game.id
        player = models.Player(user_id=request.json["player_id"], game_id=game.id)
        db.session.add(player)
        db.session.commit()
    return jsonify(response), 201

@app.route("/api/games/<game_id>/join", methods=["POST"])
def join_game(game_id: str):
    if game_id in games:
        return { "error": "game_already_started" }, 400
    if game_id not in pending_games:
        return resource_not_found(resource="game", resource_id=game_id)

    inputs = JoinGameInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    player_id = request.json["player_id"]

    if player_id in pending_games[game_id]:
        return { "error": "player_id_already_joined" }, 400

    pending_games[game_id].append(player_id)
    return jsonify(""), 200

# TODO: Only game leader can start the game
@app.route("/api/games/<game_id>/start", methods=["POST"])
def start_game(game_id: str):
    if game_id in games:
        return jsonify(""), 200
    if game_id not in pending_games:
        return resource_not_found(resource="game", resource_id=game_id)
    if len(pending_games[game_id]) < 2:
        return { "error": "need_at_least_two_players" }, 400

    player_ids = pending_games[game_id]
    pending_games.pop(game_id)
    games[game_id] = Game(player_ids)
    return jsonify(""), 200

@app.route("/api/games/<game_id>/play", methods=["POST"])
def play_game_turn(game_id: str):
    if game_id in pending_games:
        return { "error": "game_not_started" }, 400
    if game_id not in games:
        return resource_not_found(resource="game", resource_id=game_id)

    inputs = PlayTurnInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    player_id = request.json["player_id"]
    move = request.json["move"]
    card_value = request.json["card_value"]

    game = games[game_id]
    try:
        player_no = next(i for i, p in enumerate(game.players) if p.id == player_id)
    except StopIteration:
        return { "error": f"Invalid player_id: {player_id}" }, 400

    result, events = game.play_turn(
        player_no,
        move=Move[move],
        card=Card(card_value),
    )

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
    if game_id in pending_games:
        return { "error": "game_not_started" }, 400
    if game_id not in games:
        return resource_not_found(resource="game", resource_id=game_id)

    game = games[game_id]
    try:
        top_card = game.get_top_card()
        return next(p.serialize_with_playable_cards(top_card) for p in game.players if p.id == player_id)
    except StopIteration:
        return resource_not_found(resource="player", resource_id=player_id)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
