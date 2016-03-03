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


@api.route('/api/food/<int:food_id>', methods=['GET', 'POST'])
def food(food_id):
    """
    :param food_id: the id of the food item to be returned, 0 if requesting a new item
    :param: POST data is the same as GET return
    :return: on GET, a representation of the food item in json
    {food: {
        id: <food id>
        description: <food description>
        measures: [{id: <measure id>
                    description: <measure description>
                    weight: <measure weight>}
                    ...]
        nutrients: [{id: <nutrient data id>
                     nutrient_id: <nutrient definition id>
                     description: <nutrient description>
                     value: <nutrient value (in 100g)>
                     unit: <nutrient unit>}
                     ...]
        }
    }
    :return: on POST, Yp
    """
    food = None
    if request.method == 'GET':
        if food_id == 0:
            food = FoodDescription()
        else:
            food = FoodDescription.query.get(food_id)
        return jsonify({'food': food.serializable()})
    elif request.method == 'POST':
        if food_id == 0:
            food = FoodDescription()
        else:
            food = FoodDescription.query.get(food_id)

        json = request.get_json
        if json is not None:
            food.from_serializable(request.get_json()["food"])
            db.session.add(food)
            db.session.commit()
            return jsonify({'success': True,
                            'food': food.serializable()})
        else:
            return jsonify({'success': False,
                            'reason': 'malformed json'})


@api.route('/api/food/<int:food_id>/nutrients')
def food_nutrients(food_id):
    food = FoodDescription.query.get(food_id)
    return jsonify({'nutrients': [nd.serializable() for nd in food.nutrients]})


@api.route('/api/food/<int:food_id>/measures')
def food_measures(food_id):
    food = FoodDescription.query.get(food_id)
    return jsonify({'measures':
                    [{'description': measure.description,
                      'id': measure.id} for measure in food.measurements]})


@api.route('/api/food/<int:food_id>/measures/<int:measure_id>/delete')
def delete_food_measure(food_id, measure_id):
    measure = MeasurementWeight.get(measure_id)
    db.session.delete(measure)
    db.session.commit()


@login_required
@api.route('/api/entry', methods=['POST'])
def create_entry():
    t = Tag()
    t.user = current_user
    t.count = float(request.form['count'])
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
    goals = get_day_goals(current_user, graph_only=True)

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
@api.route('/api/graphs/day_macros', methods=['GET'])
def day_macros_graph():
    day = datetime.now().date()
    tags = Tag.get_day(current_user, day)
    nuts = FoodDescription.sum_nutrients(tags, group=1)
    carbs = NutrientDefinition.query.filter(NutrientDefinition.tagname == "CHOCDF").first()
    protein = NutrientDefinition.query.filter(NutrientDefinition.tagname == "PROCNT").first()
    fat = NutrientDefinition.query.filter(NutrientDefinition.tagname == "FAT").first()

    carbs_amount, protein_amount, fat_amount = 0.0, 0.0, 0.0

    for ndef, amount in nuts:
        if ndef is carbs:
            carbs_amount = amount
        if ndef is protein:
            protein_amount = amount
        if ndef is fat:
            fat_amount = amount

    data = {
        'carbohydrate': {
            'grams': carbs_amount,
            'calories': carbs_amount * 4
        },
        'protein': {
            'grams': protein_amount,
            'calories': protein_amount * 4
        },
        'fat': {
            'grams': fat_amount,
            'calories': fat_amount * 9
        },
        'total': {
            'grams': carbs_amount + protein_amount + fat_amount,
            'calories': (carbs_amount * 4) + (protein_amount * 4) + (fat_amount * 9)
        }
    }

    return jsonify({'data': data})


@login_required
@api.route('/api/suggestions')
def get_suggestions():
    suggestions = current_user.get_suggestions()
    return jsonify({'suggestions': suggestions})


@login_required
@api.route('/api/plan')
def get_plan():
    plan = current_user.get_plan()
    return jsonify({'plan': [p.serializable() for p in plan]})


@login_required
@api.route('/api/plan/add', methods=["POST"])
def add_plan():
    plan = MealPlan()
    plan.user_id = current_user.id
    plan.meal_time = request.form['mealTime']
    plan.weekdays = [Weekday.query.get(int(id)) for id in request.form.getlist("weekdays[]")]
    plan.food_id = request.form['food[id]']
    plan.measure_id = request.form['measure_id']
    plan.count = float(request.form['count'])

    db.session.add(plan)
    db.session.commit()

    return jsonify({'success': True})

