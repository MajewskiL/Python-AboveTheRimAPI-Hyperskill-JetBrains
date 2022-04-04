from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def welcome():
    return '''<h1>Welcome to the Above the Rim API</h1>
            <p>/api/v1/teams</p>
            <p>/api/v1/teams/&lt;team name&gt;</p>
            <p>/api/v1/games</p>
            <p>/api/v1/games/&lt;game_id&gt;</p>'''


app.run()
