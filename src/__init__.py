import os

from flask import Flask,session
from flask_session import Session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    SESSION_TYPE='redis'
    app.config.from_object(__name__)
    Session(app)

    @app.route('/login.html')
    def login():
        return render_template("login.html")

    return app
