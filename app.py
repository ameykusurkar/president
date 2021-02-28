from flask import Flask, jsonify, make_response, request
from flask_inputs import Inputs # type: ignore
from flask_inputs.validators import JsonSchema # type: ignore
from flask_cors import CORS # type: ignore

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

class PlayTurnInputs(Inputs):
    json = [JsonSchema(schema=PLAY_TURN_SCHEMA)]

player_ids = ["player1", "player2", "player3"]
game = Game(player_ids)

def resource_not_found(resource, resource_id):
    response = {
        "error": f"No {resource} found with id: {resource_id}",
    }
    return make_response(jsonify(response), 404)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route("/api/game", methods=["GET"])
def get_game():
    return jsonify(game.serialize())

@app.route("/api/game/play", methods=["POST"])
def play_game_turn():
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
    try:
        top_card = game.get_top_card()
        return next(p.serialize_with_playable_cards(top_card) for p in game.players if p.id == player_id)
    except StopIteration:
        return resource_not_found(resource="player", resource_id=player_id)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
