from flask import Blueprint, jsonify
from flask.ext.login import current_user, login_required

from models import *

api = Blueprint('api', 'api')

@api.route('/api/week')
def week():
    week_hist = get_week_hist(current_user)
    serializable = [{'date': str(d[0]),
                     'entries': [re.serializable() for re in d[1]]}
                    for d in week_hist]
    return jsonify({'week': serializable})
