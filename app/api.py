from flask import Blueprint, jsonify, request
from flask.ext.login import current_user, login_required

from models import *
import forms

api = Blueprint('api', 'api')

@api.route('/api/week')
def week():
    week_hist = get_week_hist(current_user)
    serializable = [{'date': str(d[0]),
                     'entries': [re.serializable() for re in d[1]]}
                    for d in week_hist]
    return jsonify({'week': serializable})


@api.route('/api/food-lookup')
def food_lookup():
    print request.form
    print request.data
    return 'ok'

@api.route('/api/entry', methods=['POST'])
def entry():
    print request.form
    return 'thanks'



