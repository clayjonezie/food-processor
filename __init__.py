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

app = Flask(__name__)
db = SQLAlchemy()
my_bcrypt = Bcrypt()
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()


def create_app(config):
    """Creates, configure, and returns a Flask() instance"""
    app.config["SQLALCHEMY_DATABASE_URI"] = keys.db_uri
    app.config["DEBUG"] = True
    app.secret_key = 'dogfood'

    db.init_app(app)
    my_bcrypt.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    from views import main
    app.register_blueprint(main)
    return app
