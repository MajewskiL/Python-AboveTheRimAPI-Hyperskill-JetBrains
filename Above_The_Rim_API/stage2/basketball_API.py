from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True

TEAMS = {"PRE": {"name": "Prague Eagles"},
         "PTK": {"name": "Petersburg Kings"},
         "SPW": {"name": "Sitno Wolves"}}

@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    <p>/api/v1/teams GET all teams</p>
    ''', 200

@app.route('/api/v1/teams')
def teams():
    global TEAMS
    return jsonify(TEAMS), 200


@app.errorhandler(404)
def error(e):
    return jsonify({"error": "Wrong address."}), 404


app.run()


