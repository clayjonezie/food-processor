from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.bcrypt import Bcrypt
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////var/www/foodprocessor/foodprocessor/foodprocessor.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foodprocessor.db"
app.config["DEBUG"] = True
app.secret_key = 'dogfood'

db = SQLAlchemy(app)
my_bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

from forms import *
from models import *
import fpdb
from fplib import nlp

@app.route("/food/<int:id>")
def food(id):
  food = FoodDescription.query.filter_by(id=id).first()
  if food is None:
    abort(404)
  return render_template("food.html", food=food)


@app.route("/food/search/<query>")
def food_search(query):
  results = search_food_descriptions(query)
  return render_template("food_search.html", results=results, query=query)


@app.route("/")
def home():
  return render_template('home.html')


@app.route('/raw_entries')
@login_required
def raw_entries():
  import_form = ImportFromTwitterForm()
  return render_template('raw_entries.html', import_form=import_form)


@app.route('/raw_entries/import_from_twitter', methods=["POST"])
@login_required
def import_from_twitter():
  form = ImportFromTwitterForm()
  if form.validate_on_submit():
    ntweets = fpdb.save_tweets(db, current_user, form.screen_name.data)
    if (ntweets > 0):
      flash('downloaded %s tweets' % ntweets)
  else:
    flash('form did not validate')
  return redirect(url_for('raw_entries'))


@app.route('/raw_entries/historgram')
@login_required
def raw_entries_histogram():
  badwords = [w.word for w in BadWord.query.all()]
  texts = [re.content for re in current_user.raw_entries]
  return render_template('raw_entries_histogram.html', hist=nlp.histogram(texts, badwords))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user is not None and user.verify_password(form.password.data):
        login_user(user, False)
        return redirect(request.args.get('next') or url_for('home'))
      flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash('You were logged out.')
  return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404
