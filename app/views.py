from flask import Blueprint, render_template, abort, flash, redirect, request, url_for, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user

from forms import *
from models import *
from fplib import nlp

main = Blueprint('main', 'main',
                 template_folder='templates')


@main.route('/food/add', methods=['GET', 'POST'])
@login_required
def create_food():
    return render_template('create_food.html')


@main.route('/food')
@login_required
def food():
    return render_template('food.html')


@main.route('/canvas')
def canvas():
    return render_template("canvas.html")


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return home()
    else:
        return render_template('index.html')


@main.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


def home():
    return render_template('home2.html')


@login_required
@main.route('/plan')
def plan():
    return render_template('plan.html')


@main.route('/goals')
@login_required
def goals():
    goals = current_user.get_all_goals()
    return render_template('goals.html', goals=goals)


@main.route('/goals/add', methods=['POST'])
@login_required
def create_goal():
    """
    This is a a bit of a misnomer because the same endpoint adds
    a new goal and updates an existing goal
    """
#    ImmutableMultiDict([('nutrient_id', u'209'), ('amount', u'0.0')])
    if request.form.has_key('nutrient_id') and request.form.has_key('amount'):
        nutrient = NutrientDefinition.query.get(
            int(request.form.get('nutrient_id')))
        amount = request.form.get('amount')

        existing_goal = NutrientGoal.query.filter(
                NutrientGoal.nutrient_id==int(request.form.get('nutrient_id')),
                NutrientGoal.user==current_user).first()

        if existing_goal is None:
            goal = NutrientGoal(amount, current_user, nutrient)
        else:
            goal = existing_goal
            goal.amount = amount

        goal.show_on_graph = 'show_on_graph' in request.form.keys()

        db.session.add(goal)
        db.session.commit()
    return redirect(url_for('main.goals'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if len(User.query.filter(User.email==form.email.data).all()) != 0:
            flash("email %s exists." % form.email.data)
        else:
            user = User()
            user.email =  form.email.data
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Signed up!')
            return redirect(url_for('main.index'))
    return render_template('signup.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)


@main.route('/parse', methods=['POST', 'GET'])
def parse():
    query = request.form['query']
    return jsonify(nlp.realtime_parse(query))


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('main.index'))


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
