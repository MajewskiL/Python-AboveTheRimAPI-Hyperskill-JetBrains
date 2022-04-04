from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True

TEAMS = {"PRE": {"name": "Prague Eagles"},
         "PTK": {"name": "Petersburg Kings"},
         "SPW": {"name": "Sitno Wolves"}}
GAMES = []

@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    <p>/api/v1/teams GET all teams</p>
    <p>/api/v1/games GET all games</p>
    ''', 200


@app.route('/api/v1/teams')
def teams():
    global TEAMS
    return jsonify(TEAMS), 200


@app.route('/api/v1/games')
def games():
    global TEAMS
    if len(GAMES) == 0:
        return '', 204


@app.errorhandler(404)
def error(e):
    return jsonify({"success": False,
                    "error": "Wrong address."}), 404


app.run()


