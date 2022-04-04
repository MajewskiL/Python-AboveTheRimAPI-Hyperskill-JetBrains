from flask import Flask, jsonify

TEAMS = {"PRE": {"name": "Prague Eagles"},
         "PTK": {"name": "Petersburg Kings"},
         "STW": {"name": "Sitno Wolves"}}

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    ''', 200


@app.errorhandler(404)
def error(e):
    return jsonify({"success": False,
                    "error": "Wrong address."}), 404


app.run()
