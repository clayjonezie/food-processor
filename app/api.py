from flask import Blueprint, jsonify, request
from flask.ext.login import current_user, login_required
from datetime import datetime

from models import *
from fplib import nlp

api = Blueprint('api', 'api')


@api.route('/api/week')
def week():
    weeks_tags = Tag.get_week(current_user)
    serializable = [{'date': day['date'].isoformat(),
                     'tags': [t.serializable() for t in day['tags']]}
                    for day in weeks_tags]
    return jsonify({'week': serializable})


@api.route('/api/food-lookup', methods=['GET', 'POST'])
def food_lookup():
    query = request.form['query']
    return jsonify(nlp.food_parse(db, query))


@api.route('/api/food/<int:food_id>/measures')
def food_measures(food_id):
    food = FoodDescription.query.get(food_id)
    return jsonify({'measures':
                    [{'description': measure.description,
                      'id': measure.id} for measure in food.measurements]})


@api.route('/api/entry', methods=['POST'])
def entry():
    t = Tag()
    t.user = current_user
    t.count = int(request.form['count'])
    t.measurement_weight_id = int(request.form['measure_id'])
    t.food_description_id = int(request.form['food[id]'])
    t.at = datetime.now()
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True})

