from flask import Flask, request
import sys
from flask import jsonify
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
import re


app.config.update(
    {'SQLALCHEMY_DATABASE_URI': f'sqlite:///db.sqlite3'}
)

db = SQLAlchemy(app)


class TeamModel(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    shortcut = db.Column(db.String(3))
    name = db.Column(db.String(50), nullable=False)


class GameModel(db.Model):
    __gamename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(3))
    visiting_team = db.Column(db.String(3))
    home_team_score = db.Column(db.Integer)
    visiting_team_score = db.Column(db.Integer)


db.create_all()


def serialize_team_model(datas: TeamModel):
    out = {}
    for data in datas:
        out[data.shortcut] = data.name
    return out


def serialize_game_model(datas: GameModel):
    out = {}
    for data in datas:
        h_team = TeamModel.query.filter_by(shortcut=data.home_team).first()
        v_team = TeamModel.query.filter_by(shortcut=data.visiting_team).first()
        print("HHHHH", data.home_team, data.visiting_team)
        out[data.id] = f"{h_team.name} {data.home_team_score}:{data.visiting_team_score} {v_team.name}"
    return out


@app.route('/api/v1/teams', methods=["GET", "POST"])
def teams():
    if request.method == "GET":
        teams = TeamModel.query.all()
        return jsonify({"success": True, "data": serialize_team_model(teams)}), 200
    else:
        data = request.get_json()
        if re.match("^([A-Z]{3})$", data["shortcut"]):
            new = TeamModel(shortcut=data["shortcut"], name=data["name"])
            db.session.add(new)
            db.session.commit()
            return jsonify({"success": True, "data": "Team added"}), 201
        else:
            return jsonify({"success": False, "data": "Wrong shortcut format"}), 400


@app.route('/api/v1/games', methods=["GET", "POST"])
def games():
    if request.method == "GET":
        games = GameModel.query.all()
        return jsonify({"success": True, "data": serialize_game_model(games)}), 200
    else:
        data = request.get_json()
        if TeamModel.query.filter_by(shortcut=data["visiting_team"]).first() and TeamModel.query.filter_by(shortcut=data["home_team"]).first():
            new = GameModel(home_team=data["home_team"],
                            visiting_team=data["visiting_team"],
                            home_team_score=data["home_team_score"],
                            visiting_team_score=data["visiting_team_score"])
            db.session.add(new)
            db.session.commit()
            return jsonify({"success": True, "data": "Game added"}), 201
        else:
            return jsonify({"success": False, "data": "Wrong team shortcut"}), 400


# GET teams {"success": True, "data": TEAMS} 200
# POST teams {"success": True, "data": "Team was added."} 201
# POST teams {"success": False, "data": "Wrong data format or empty required field."} 400

# GET games {"success": True, "data": TEAMS} 200
# POST teams {"success": True, "data": "Team was added."} 201
# POST teams {"success": False, "data": "Wrong data format or empty required field."} 400


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



#  TEST NAJPIERW PUTSEJ BAZY I BLAD 400 DOPIERO POTEM ZAPELNIAMY

'''

@app.route('/api/v1/team/<string:num>')
def team(num: int):
    return jsonify({"success": True,
                    "data": num}), 200
@app.route('/api/v1/games')  # ONE TEAM!!!!!!!!!!!!!!!!!!!!!!!
def games(team_name: str):
    global GAMES
    if len(GAMES) == 0:
        return jsonify({"success": False,
                        "error": "No data"}), 400
    else:
        return jsonify({"success": True,
                        "error": GAMES}), 200
'''
