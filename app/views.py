from flask import Blueprint, render_template, abort, flash, redirect, request, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user

from forms import *
from models import *
import fpdb
from fplib import nlp
from datetime import datetime

main = Blueprint('main', 'main',
                 template_folder='templates')

@main.route('/food/<int:id>')
def food(id):
  food = FoodDescription.query.filter_by(id=id).first()
  if food is None:
    abort(404)
  return render_template('food.html', food=food)


@main.route('/food/search/<query>')
def food_search(query):
  results = search_food_descriptions(query)
  return render_template('food_search.html', results=results, query=query)


@main.route('/')
def home():
  if current_user.is_authenticated:
    return render_template('home_authenticated.html')
  else: 
    return render_template('home.html')


@main.route('/raw_entries', methods=['GET', 'POST'])
@login_required
def raw_entries():
  create_form = CreateRawEntryForm()
  if create_form.validate_on_submit():
    entry = RawEntry(content=create_form.content.data, 
        at=datetime.utcnow())
    entry.user = current_user
    db.session.add(entry)
    db.session.commit()
  return render_template('raw_entries.html', create_form=create_form)


@main.route('/raw_entries/historgram')
@login_required
def raw_entries_histogram():
  badwords = [w.word for w in BadWord.query.all()]
  texts = [re.content for re in current_user.raw_entries]
  return render_template('raw_entries_histogram.html', hist=nlp.histogram(texts, badwords))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user is not None and user.verify_password(form.password.data):
        login_user(user, False)
        return redirect(request.args.get('next') or url_for('main.home'))
      flash('Invalid email or password')
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
  logout_user()
  flash('You were logged out.')
  return redirect(url_for('main.home'))


@main.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404
