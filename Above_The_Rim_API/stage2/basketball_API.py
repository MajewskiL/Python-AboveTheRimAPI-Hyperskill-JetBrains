from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)

app.config.update(
    {'SQLALCHEMY_DATABASE_URI': f'sqlite:///db.sqlite3'}
)

db = SQLAlchemy(app)


class TeamModel(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    shortcut = db.Column(db.String(3))
    name = db.Column(db.String(50), nullable=False)


db.create_all()


def serialize_team_model(datas: TeamModel):
    out = {}
    for data in datas:
        out[data.shortcut] = data.name
    return out


@app.route('/api/v1/teams', methods=["GET", "POST"])
def teams():
    if request.method == "GET":
        teams = TeamModel.query.all()
        return jsonify({"success": True, "data": serialize_team_model(teams)}), 200
    else:
        data = request.get_json()
        new = TeamModel(shortcut=data["shortcut"], name=data["name"])
        db.session.add(new)
        db.session.commit()
        return jsonify({"success": True, "data": "Team added"}), 201


# GET teams {"success": True, "data": TEAMS} 200
# POST teams {"success": True, "data": "Team was added."} 201


@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    <p>/api/v1/teams GET all teams</p>
    <p>/api/v1/teams POST add team</p>
    <p>/api/v1/team/<name> GET team <name></p>
    ''', 200


@app.errorhandler(404)
def error(e):
    return jsonify({"success": False,
                    "error": "Wrong address"}), 404


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)

