from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def welcome():
    return '''<h1>Welcome to the Above the Rim API</h1>
            <p>API_v1</p>'''


app.run()

