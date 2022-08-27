from flask import Flask, request
import sys
from flask import jsonify
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
import re
from sqlalchemy import text

app.config.update(
    {'SQLALCHEMY_DATABASE_URI': f'sqlite:///db.sqlite3'}
)

db = SQLAlchemy(app)


class TeamModel(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)


class GameModel(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(3))
    visiting_team = db.Column(db.String(3))
    home_team_score = db.Column(db.Integer)
    visiting_team_score = db.Column(db.Integer)


class QuartersModel(db.Model):
    __tablename__ = "quarters"
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    quarters = db.Column(db.String(100))


db.create_all()

#  db.create_all()


def serialize_team_model(datas: TeamModel):
    out = {}
    for data in datas:
        out[data.short] = data.name
    return out


def serialize_game_model(datas: GameModel, mode=""):
    out = {}
    for data in datas:
        h_team = TeamModel.query.filter_by(short=data.home_team).first()
        v_team = TeamModel.query.filter_by(short=data.visiting_team).first()
        out[data.id] = f"{h_team.name} {data.home_team_score}:{data.visiting_team_score} {v_team.name}"
        if mode == "q":
            game = QuartersModel.query.filter_by(game_id=data.id).first()
            if game is not None:
                out[data.id] += f" ({game.quarters})"
    return out




@app.route('/api/v1/teams', methods=["GET", "POST"])
def teams():
    if request.method == "GET":
        teams = TeamModel.query.all()
        return jsonify({"success": True, "data": serialize_team_model(teams)}), 200
    else:
        data = request.get_json()
        if re.match("^([A-Z]{3})$", data["short"]):
            new = TeamModel(short=data["short"], name=data["name"])
            db.session.add(new)
            db.session.commit()
            return jsonify({"success": True, "data": "Team added"}), 201
        else:
            return jsonify({"success": False, "data": "Wrong short format"}), 400


@app.route('/api/v1/games', methods=["GET", "POST"])
def quarters():
    if request.method == "GET":
        games = GameModel.query.all()
        return jsonify({"success": True, "data": serialize_game_model(games)}), 200
    else:
        data = request.get_json()
        if any([d not in [da for da in data.keys()] for d in ["visiting_team", "home_team", "home_team_score", "visiting_team_score"]]):
            return jsonify({"success": False, "data": "All fields are required"}), 400
        if TeamModel.query.filter_by(short=data["visiting_team"]).first() and TeamModel.query.filter_by(short=data["home_team"]).first():
            new = GameModel(home_team=data["home_team"],
                            visiting_team=data["visiting_team"],
                            home_team_score=data["home_team_score"],
                            visiting_team_score=data["visiting_team_score"])
            db.session.add(new)
            db.session.commit()
            return jsonify({"success": True, "data": "Game added"}), 201
        else:
            return jsonify({"success": False, "data": "Wrong team short"}), 400


@app.route('/api/v2/games', methods=["GET", "POST"])
def games():
    if request.method == "GET":
        games = GameModel.query.all()
        return jsonify({"success": True, "data": serialize_game_model(games, "q")}), 200
    else:
        data = request.get_json()
        if TeamModel.query.filter_by(short=data["visiting_team"]).first() and TeamModel.query.filter_by(short=data["home_team"]).first():
            new = GameModel(home_team=data["home_team"],
                            visiting_team=data["visiting_team"])
            db.session.add(new)
            db.session.commit()
            return jsonify({"success": True, "data": new.id}), 201
        else:
            return jsonify({"success": False, "data": "Wrong team short"}), 400


@app.route('/api/v2/games', methods=["PUT"])
def add_quarter():
    data = request.get_json()
    game = GameModel.query.filter_by(id=data["id"]).first()
    if game is None:
        return jsonify({"success": False, "data": f"There is no game with id {data['id']}"}), 400
    if game.home_team_score is None:
        quarter = QuartersModel(game_id=data["id"], quarters=data["quarters"])
        db.session.add(quarter)
        data = data["quarters"].split(":")
        game.home_team_score = data[0]
        game.visiting_team_score = data[1]
        db.session.commit()
    else:
        last_score = QuartersModel.query.filter_by(game_id=data["id"]).first()
        last_score.quarters = last_score.quarters + "," + data["quarters"]
        data = data["quarters"].split(":")
        game.home_team_score = game.home_team_score + int(data[0])
        game.visiting_team_score = game.visiting_team_score + int(data[1])
        db.session.commit()
    return jsonify({"success": True, "data": "Score updated"}), 200



@app.route('/api/v1/team/<name>')
def team(name):
    team = TeamModel.query.filter_by(short=name).first()
    if team:
        all = db.engine.execute(f"SELECT COUNT (*) FROM games WHERE (home_team = '{team.short}' or visiting_team = '{team.short}');")
        win = db.engine.execute(f"SELECT COUNT (*) FROM games WHERE (home_team = '{team.short}' and home_team_score > visiting_team_score) "
                                f"or (visiting_team = '{team.short}' and home_team_score < visiting_team_score);")
        all = all.first()[0]
        win = win.first()[0]
        return jsonify({"success": True, "data": {"short": team.short, "name": team.name, "win": win, "lost": all - win}}), 200
    else:
        return jsonify({"success": False, "data": f"There is no team {name}"}), 400


# Stage 2
# GET teams {"success": True, "data": TEAMS} 200
# POST teams {"success": True, "data": "Team was added"} 201

# Stage 3
# POST teams {"success": False, "data": "All fields are required"} 400
# POST teams {"success": False, "data": "Wrong data format or empty required field"} 400
# POST teams {"success": True, "data": "Team was added"} 201

# GET games {"success": True, "data": TEAMS} 200


# Stage 4
# GET team/<name> {"success": True, "data": {name: , short: , win: , lost: }}, 200
# GET team/<name> {"success": False, "data": "There is no team {name}"}, 400

# Stage 5
# ????


@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
    <p>/api/v1/teams GET all teams</p>
    <p>/api/v1/teams POST add team</p>
    <p>/api/v1/games GET all games</p>
    <p>/api/v1/games POST add game</p>    
    <p>/api/v1/team/%SHORT% GET a team statistics</p>
    <p>/api/v2/games POST add game</p>
    <p>/api/v2/games GET all games</p>
    <p>/api/v1/games PUT updated game</p>
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
