from flask import Flask
import sys
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config.update(
    {'SQLALCHEMY_DATABASE_URI': f'sqlite:///db.sqlite3'}
)

db = SQLAlchemy(app)


class ReModel(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)





@app.route('/')
def home():
    return '''
    <H1>Welcome to the "Above the Rim" API!</h1>
    ''', 200


@app.errorhandler(404)
def error(e):
    return jsonify({"success": False,
                    "data": "Wrong address"}), 404


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        with app.app_context():
            db.create_all()
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        with app.app_context():
            db.create_all()
        app.run(debug=True)
