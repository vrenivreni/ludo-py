from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory storage for simplicity
games = {}
players = {}

# Define a class for the Ludo game
class LudoGame:
    def __init__(self, game_id):
        self.game_id = game_id
        self.board = [[None for _ in range(15)] for _ in range(15)]  # Placeholder for a 15x15 board
        self.players = {}
        self.turn_order = []
        self.current_turn = 0
        self.status = "waiting"  # waiting, in_progress, finished

    def add_player(self, player_id):
        if self.status != "waiting":
            return False
        self.players[player_id] = {"pieces": [0, 0, 0, 0], "home": 0, "goal": 0}  # Simplified pieces
        self.turn_order.append(player_id)
        if len(self.players) == 4:
            self.status = "in_progress"
        return True

    def make_move(self, player_id, piece_index, steps):
        if self.status != "in_progress":
            return {"error": "Game is not in progress"}
        if self.turn_order[self.current_turn] != player_id:
            return {"error": "Not your turn"}

        # Simplified logic: Move piece
        pieces = self.players[player_id]["pieces"]
        if piece_index < 0 or piece_index >= len(pieces):
            return {"error": "Invalid piece"}
        pieces[piece_index] += steps
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        return {"success": True, "new_position": pieces[piece_index]}

    def get_state(self):
        return {
            "game_id": self.game_id,
            "players": list(self.players.keys()),
            "status": self.status,
            "current_turn": self.turn_order[self.current_turn] if self.status == "in_progress" else None
        }

# API Endpoints

@app.route('/create_game', methods=['POST'])
def create_game():
    game_id = str(uuid.uuid4())
    games[game_id] = LudoGame(game_id)
    return jsonify({"game_id": game_id})

@app.route('/join_game/<game_id>', methods=['POST'])
def join_game(game_id):
    player_id = str(uuid.uuid4())
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
    success = games[game_id].add_player(player_id)
    if not success:
        return jsonify({"error": "Unable to join game"}), 400
    players[player_id] = game_id
    return jsonify({"player_id": player_id})

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    player_id = data.get("player_id")
    piece_index = data.get("piece_index")
    steps = data.get("steps")

    if player_id not in players:
        return jsonify({"error": "Player not found"}), 404

    game_id = players[player_id]
    game = games[game_id]
    result = game.make_move(player_id, piece_index, steps)
    return jsonify(result)

@app.route('/game_state/<game_id>', methods=['GET'])
def game_state(game_id):
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(games[game_id].get_state())

if __name__ == '__main__':
    app.run(debug=True)
