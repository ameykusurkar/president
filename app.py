from flask import Flask, jsonify, make_response
from game import Game

app = Flask(__name__)

player_ids = ["player1", "player2", "player3"]
game = Game(player_ids)

def resource_not_found(resource, resource_id):
    response = {
        "error": f"No {resource} found with id: {resource_id}",
    }
    return make_response(jsonify(response), 404)

@app.route('/')
def index():
    return "Hello, World!"

@app.route("/api/game", methods=["GET"])
def get_game():
    return jsonify(game.serialize())

@app.route("/api/players/<player_id>", methods=["GET"])
def get_player(player_id: str):
    try:
        return next(p.serialize() for p in game.players if p.id == player_id)
    except StopIteration:
        return resource_not_found(resource="player", resource_id=player_id)

if __name__ == '__main__':
    app.run(debug=True)
