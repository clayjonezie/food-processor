from flask import Blueprint, jsonify, request
from flask.ext.login import current_user, login_required
from datetime import datetime

from models import *
from fplib import nlp

api = Blueprint('api', 'api')


@login_required
@api.route('/api/week')
def week():
    weeks_tags = Tag.get_week(current_user)
    serializable = [{'date': day['date'].isoformat(),
                     'tags': [t.serializable() for t in day['tags']]}
                    for day in weeks_tags]
    return jsonify({'week': serializable})


@api.route('/api/food_lookup', methods=['GET', 'POST'])
def food_lookup():
    query = request.form['query']
    return jsonify(nlp.food_parse(db, query))


@api.route('/api/food/<int:food_id>/measures')
def food_measures(food_id):
    food = FoodDescription.query.get(food_id)
    return jsonify({'measures':
                    [{'description': measure.description,
                      'id': measure.id} for measure in food.measurements]})


@login_required
@api.route('/api/entry', methods=['POST'])
def create_entry():
    t = Tag()
    t.user = current_user
    t.count = int(request.form['count'])
    t.measurement_weight_id = int(request.form['measure_id'])
    t.food_description_id = int(request.form['food[id]'])
    t.at = datetime.now()
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True})


@login_required
@api.route('/api/entry/delete', methods=['POST'])
def delete_entry():
    print request.form
    tag_id = int(request.form['id'])
    tag = Tag.query.get(tag_id)
    if tag is not None:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@login_required
@api.route('/api/graphs/day_nutrients', methods=['GET'])
def day_nutrients_graph():
    # list of (NutrDef, percent complete, current amount, goal amount)
    goals = get_day_goals(current_user)

    data = []
    for g in goals:
        data.append({'value': g[1],
                     'current': g[2],
                     'total': g[3],
                     'label': g[0].desc,
                     'unit': g[0].units})

    print 'data', data

    return jsonify({'data': data})


@login_required
@api.route('/api/suggestions')
def get_suggestions():
    suggestions = [t.serializable() for t in current_user.get_suggestions()]
    return jsonify({'suggestions': suggestions})
    



















