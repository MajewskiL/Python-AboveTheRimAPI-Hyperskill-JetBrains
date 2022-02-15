from flask import Flask, jsonify, request


TEAMS = {"PRE": {"name": "Prague Eagles"},
         "PTK": {"name": "Petersburg Kings"},
         "STW": {"name": "Sitno Wolves"}}

GAMES = []
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    <p>/api/v1/teams GET all teams</p>
    <p>/api/v1/games GET all games</p>
    <p>/api/v1/games POST to add a game</p>
    ''', 200


@app.route('/api/v1/teams')
def teams():
    global TEAMS
    return jsonify(TEAMS), 200


@app.route('/api/v1/games', methods=["GET", "POST"])
def games():
    global TEAMS
    method = request.method
    if method == "GET":
        if len(GAMES) == 0:
            return '', 204
        print(GAMES)
        return_games = []
        for g in GAMES:
            return_games.append({TEAMS[g["home_team"]]["name"]: g["score"][0], TEAMS[g["visiting_team"]]["name"]: g["score"][1]})
        print(return_games)
        return jsonify(return_games), 200
    else:
        data = request.get_json()
        if any([data["home_team"] not in TEAMS, data["visiting_team"] not in TEAMS]):
            return jsonify({"error": "Wrong team name."}), 400
        GAMES.append(data)
        return jsonify({"status": "OK"}), 201

@app.errorhandler(404)
def error(e):
    return jsonify({"error": "Wrong address."}), 404


app.run()


