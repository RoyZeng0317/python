import random
from flask import Flask, jsonify, request, render_template, session
from game_engine import GameManager, ROLES

app = Flask(__name__)
app.secret_key = "game-secret-key-change-in-production"

manager = GameManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/roles")
def get_roles():
    return jsonify([
        {"id": "square", "name": "Square", "color": "#e74c3c", "desc": "Balanced fighter"},
        {"id": "triangle", "name": "Triangle", "color": "#3498db", "desc": "Swift attacker"},
        {"id": "circle", "name": "Circle", "color": "#2ecc71", "desc": "Tough defender"},
        {"id": "rectangle", "name": "Rectangle", "color": "#9b59b6", "desc": "Powerful striker"}
    ])

@app.route("/api/game/start", methods=["POST"])
def start_game():
    data = request.get_json()
    role_id = data.get("role", "square")
    game_id = manager.create_game(role_id)
    session["game_id"] = game_id
    gs = manager.get_game(game_id)
    return jsonify({"gameId": game_id, "state": gs.to_dict()})

@app.route("/api/game/state")
def get_state():
    game_id = session.get("game_id")
    if not game_id:
        return jsonify({"error": "No game"}), 400
    gs = manager.get_game(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(gs.to_dict())

@app.route("/api/game/update", methods=["POST"])
def update_game():
    game_id = session.get("game_id")
    if not game_id:
        return jsonify({"error": "No game"}), 400
    gs = manager.get_game(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json()
    keys = data.get("keys", {})
    gs.update(keys)
    return jsonify(gs.to_dict())

@app.route("/api/game/action", methods=["POST"])
def game_action():
    game_id = session.get("game_id")
    if not game_id:
        return jsonify({"error": "No game"}), 400
    gs = manager.get_game(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json()
    action = data.get("action", "")

    if action == "attack":
        gs.attack(mouse_x=data.get("mouseX"), mouse_y=data.get("mouseY"))
    elif action == "super":
        gs.activate_super()

    return jsonify(gs.to_dict())

@app.route("/api/game/spell", methods=["POST"])
def check_spell():
    game_id = session.get("game_id")
    if not game_id:
        return jsonify({"error": "No game"}), 400
    gs = manager.get_game(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    data = request.get_json()
    given = data.get("word", "")
    result = gs.check_spell(given)

    return jsonify({"correct": result, "state": gs.to_dict()})

@app.route("/api/game/word")
def get_word():
    return jsonify({"word": random.choice(manager.games[next(iter(manager.games))].words) if manager.games else "apple"})

if __name__ == "__main__":
    app.run(debug=True)
