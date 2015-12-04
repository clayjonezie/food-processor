from flask import Blueprint, render_template, abort, flash, redirect, request, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user

from forms import *
from models import *
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
    results = nlp.nearby_food_descriptions(query) + \
        nlp.search_food_descriptions(query)
    return render_template('food_search.html', results=results, query=query)


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return home()
    else:
        return render_template('index.html')


def home():
    create_form = CreateRawEntryForm()
    create_form.content.data = ''
    week_entries = get_week_hist(current_user)
    week = get_week_days(current_user)
    return render_template('home.html', week=zip(week, week_entries),
                           create_form=create_form, day_goals=get_day_goals(current_user))


@main.route('/raw_entries/add', methods=['POST'])
@login_required
def create_raw_entry():
    create_form = CreateRawEntryForm()
    if create_form.validate_on_submit():
        entry = RawEntry(content=create_form.content.data,
                         at=datetime.utcnow())
        entry.user = current_user
        db.session.add(entry)
        tags = nlp.tag_raw_entry(entry)
        if len(tags) > 0:
            db.session.add_all(tags)
            db.session.commit()
            flash('added %s' % create_form.content.data)
        else:
            flash('there was nothing parseable there :( this is an issue!')
    return redirect(url_for('main.index'))


@main.route('/raw_entries/<int:id>', methods=['GET', 'POST'])
@login_required
def raw_entry(id):
    entry = RawEntry.query.get(id)
    if entry is None:
        abort(404)
    elif entry.user != current_user:
        abort(403)
    else:
        create_tag_form = CreateTag()
        if request.method == 'POST':
            if (request.form.has_key("measurement")):
                measurement = MeasurementWeight.query.get(
                        int(request.form["measurement"]))
                tag = Tag.query.get(int(request.form["tag_id"]))
                tag.measurement = measurement
                db.session.commit()
            elif (request.form.has_key("count")):
                tag = Tag.query.get(int(request.form["tag_id"]))
                tag.count = float(request.form["count"])
                db.session.commit()
            elif create_tag_form.validate():
                food = FoodDescription.query.get(int(create_tag_form.food_id.data))
                if food is not None:
                    tag = Tag()
                    tag.food_description = food
                    tag.measurement = food.best_measurement()
                    tag.count = 1.0
                    tag.raw_entry = entry
                    db.session.add(tag)
                    db.session.commit()
                    create_tag_form.food_id.data = ''

        return render_template('raw_entry.html', 
                entry=entry, 
                create_tag_form=create_tag_form)


@main.route('/raw_entries/<int:id>/delete')
@login_required
def raw_entry_delete(id):
    entry = RawEntry.query.get(id)
    if entry is None:
        abort(404)
    elif entry.user != current_user:
        abort(403)
    else:
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for('main.index'))


@main.route('/tag/<int:id>/delete')
@login_required
def tag_delete(id):
    tag = Tag.query.get(id)
    if tag is None:
        abort(404)
    elif tag.raw_entry.user != current_user:
        abort(403)
    else:
        entry = tag.raw_entry
        db.session.delete(tag)
        db.session.commit()
        return redirect(url_for('main.raw_entry', id=entry.id))


@main.route('/short_preferences', methods=['GET', 'POST'])
@login_required
def short_preferences():
    form = AddShortPreference()
    if form.validate_on_submit():
        short = form.food_short.data
        fs = FoodShort.get_or_create(short)
        sp = ShortPreference.query.filter(
            ShortPreference.food_short_id == fs.id,
            ShortPreference.user_id == current_user.id).first()
        if sp is None:
            sp = ShortPreference(food_short=fs, user=current_user)

        sp.food_description = FoodDescription.query.get(int(form.food_id.data))
        db.session.add(sp)
        db.session.commit()

    return render_template('short_preferences.html', form=form)


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
        goal = NutrientGoal(amount, current_user, nutrient)
        db.session.add(goal)
        db.session.commit()
    return redirect(url_for('main.goals'))



@main.route('/short_preferences/<int:id>')
@login_required
def short_preference(id):
    pref = ShortPreference.query.get(id)
    if pref is None:
        abort(404)
    elif pref.user != current_user:
        abort(403)
    else:
        return render_template('short_preference.html', pref=pref)

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


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('main.index'))


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
