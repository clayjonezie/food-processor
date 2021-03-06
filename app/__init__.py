from flask import Flask, render_template, redirect, url_for, flash, request
from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager, login_user, logout_user
from flask.ext.login import login_required, current_user
from flask.ext.moment import Moment
from flask_wtf.csrf import CsrfProtect
from fplib import keys

app = Flask(__name__, static_folder="../static")
db = SQLAlchemy()
my_bcrypt = Bcrypt()
moment = Moment()
login_manager = LoginManager()


def create_app(config):
    """
    :param config: a string specifying the configuration environment
    :return: a Flask instance properly configured
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = keys.db_uri
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = 'dogfood'

    bootstrap = Bootstrap()

    db.init_app(app)
    my_bcrypt.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    from views import main
    app.register_blueprint(main)
    from api import api
    app.register_blueprint(api)
    return app
