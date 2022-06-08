from flask import Flask
import sys
from flask import jsonify
app = Flask(__name__)


from flask_sqlalchemy import SQLAlchemy

app.config.update(
    {'SQLALCHEMY_DATABASE_URI': f'sqlite:///db.sqlite3'}
)

db = SQLAlchemy(app)

class ReModel(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(3))
    name = db.Column(db.String(50), nullable=False)


db.create_all()


@app.route('/')
def home():
    return '''
    <h1>Welcome to the "Above the Rim" API!</h1>
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
