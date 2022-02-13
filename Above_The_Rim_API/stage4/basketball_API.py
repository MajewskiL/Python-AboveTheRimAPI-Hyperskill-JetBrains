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
    <p>/api/v2/teams GET all teams</p>
    <p>/api/v2/games GET all games</p>
    <p>/api/v2/games POST to add a game</p>
    ''', 200


@app.route('/api/v1/teams')
def teams():
    global TEAMS
    return jsonify(TEAMS), 200


@app.route('/api/v2/teams')
def teams2():
    global TEAMS, GAMES
    scores = {}
    for team in TEAMS:
        scores[team] = {"name": TEAMS[team]["name"], "wins": 0, "lost": 0}
    for game in GAMES:
        if game["score"][0] > game["score"][1]:
            scores[game["home_team"]]["wins"] += 1
            scores[game["visiting_team"]]["lost"] += 1
        else:
            scores[game["visiting_team"]]["wins"] += 1
            scores[game["home_team"]]["lost"] += 1
    return jsonify(scores), 200


@app.route('/api/v1/games', methods=["GET", "POST"])
def games():
    global TEAMS
    method = request.method
    if method == "GET":
        if len(GAMES) == 0:
            return '', 204
        games = []
        for game in GAMES:
            games.append({"home_team": game["home_team"], "visiting_team": game["visiting_team"], "score": game["score"]})
        return jsonify(games), 200
    else:
        data = request.get_json()
        if any([data["home_team"] not in TEAMS, data["visiting_team"] not in TEAMS]):
            return jsonify({"error": "Wrong team name."})
        data["partial_score"] = []
        GAMES.append(data)
        return jsonify({"status": "OK"}), 201


@app.route('/api/v2/games', methods=["GET", "POST"])
def games2():
    global TEAMS
    method = request.method
    if method == "GET":
        if len(GAMES) == 0:
            return '', 204
        return jsonify(GAMES), 200
    else:
        data = request.get_json()
        if any([data["home_team"] not in TEAMS, data["visiting_team"] not in TEAMS]):
            return jsonify({"error": "Wrong team name."})
        data["score"] = [sum([x[0] for x in data["partial_score"]]), sum([x[1] for x in data["partial_score"]])]
        GAMES.append(data)
        return jsonify({"status": "OK"}), 201


@app.errorhandler(404)
def error(e):
    return jsonify({"error": "Wrong address."}), 404


app.run()


