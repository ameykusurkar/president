from flask import Flask, jsonify
from game import Game

app = Flask(__name__)

player_ids = ["player1", "player2", "player3"]
game = Game(player_ids)

@app.route('/')
def index():
    return "Hello, World!"

@app.route("/api/game", methods=["GET"])
def get_game():
    return jsonify(game.turn_details())

if __name__ == '__main__':
    app.run(debug=True)
