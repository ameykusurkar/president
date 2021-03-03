from flask import Flask, jsonify, make_response, request
from flask_inputs import Inputs # type: ignore
from flask_inputs.validators import JsonSchema # type: ignore
from flask_cors import CORS # type: ignore

from typing import Optional

from game import Game, Move, Card, TurnResult

app = Flask(__name__)
# app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

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

waiting_player_ids: list[str] = []
game: Optional[Game] = None

def resource_not_found(resource, resource_id):
    response = {
        "error": f"No {resource} found with id: {resource_id}",
    }
    return make_response(jsonify(response), 404)

@app.route('/')
@app.route('/game')
def index():
    return app.send_static_file('index.html')

@app.route("/api/game", methods=["GET"])
def get_game():
    if not game:
        return make_response(jsonify({
            "waiting_player_ids": waiting_player_ids,
            "game_status": "waiting",
        }), 200)
    return jsonify(game.serialize())

@app.route("/api/game/join", methods=["POST"])
def join_game():
    inputs = JoinGameInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    if game:
        return { "error": "game_already_started" }, 400

    player_id = request.json["player_id"]

    if player_id in waiting_player_ids:
        return { "error": "player_id_already_joined" }, 400

    waiting_player_ids.append(player_id)
    return make_response(jsonify({}), 200)

@app.route("/api/game/start", methods=["POST"])
def start_game():
    global game
    if game:
        return make_response(jsonify({}), 200)
    if len(waiting_player_ids) < 2:
        return { "error": "need_at_least_two_players" }, 400
    game = Game(waiting_player_ids)
    return make_response(jsonify({}), 200)

@app.route("/api/game/play", methods=["POST"])
def play_game_turn():
    if not game:
        return resource_not_found(resource="game", resource_id="0")

    inputs = PlayTurnInputs(request)
    if not inputs.validate():
        return { "errors": inputs.errors }, 400

    player_id = request.json["player_id"]
    move = request.json["move"]
    card_value = request.json["card_value"]

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

@app.route("/api/players/<player_id>", methods=["GET"])
def get_player(player_id: str):
    if not game:
        return resource_not_found(resource="game", resource_id="0")
    try:
        top_card = game.get_top_card()
        return next(p.serialize_with_playable_cards(top_card) for p in game.players if p.id == player_id)
    except StopIteration:
        return resource_not_found(resource="player", resource_id=player_id)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
