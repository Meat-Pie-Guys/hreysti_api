import datetime
import uuid
from functools import wraps
import dateparser
import jwt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from src import error_codes
from src.validator import valid_password, valid_ssn

app = Flask(__name__)
app.config['SECRET_KEY'] = '>kz9q>GnW<>~_.7,8cw_-/xA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///..\\db\\fenrir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


participates = db.Table(
    'Participates',
    db.Column('u_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('w_id', db.Integer, db.ForeignKey('workout.id', ondelete='CASCADE'), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    open_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), primary_key=False, nullable=False)
    ssn = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(100), primary_key=False, nullable=False)
    user_role = db.Column(db.String(12), primary_key=False, nullable=False, default='Client')
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    expire_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    workouts = db.relationship('Workout', secondary=participates, lazy='dynamic',
                               backref=db.backref('workouts', lazy='dynamic'))


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_time = db.Column(db.DateTime(), unique=True, nullable=False)
    description = db.Column(db.Text, primary_key=False, nullable=False)


def authenticated(fun):
    @wraps(fun)
    def decorated(*args, **kwargs):
        if 'fenrir-token' not in request.headers:
            return jsonify({'error': error_codes.missing_token}), 401
        token = request.headers['fenrir-token']
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            curr_user = User.query.filter_by(open_id=data['open_id']).first()
            if curr_user:
                return fun(curr_user, *args, **kwargs)
            return jsonify({'error': error_codes.no_such_user}), 402
        except jwt.DecodeError:
            return jsonify({'error': error_codes.invalid_token}), 403
    return decorated


@app.route('/', methods=['GET'])
@authenticated
def home(this_user):
    """
    For testing authentication only!

    :param this_user: The current session user
    :return: A welcome message
    """
    return jsonify({'error': error_codes.no_error, 'message': 'Welcome to Fenrir, {0}'.format(this_user.name)})


@app.route('/user', methods=['POST'])
def create_user():
    """
    Creates a new user in the database given legal data.

    :return: a json object with an error code. 0 for success, > 0 for error
    """
    data = request.get_json()
    if any(k not in data for k in ('name', 'password', 'ssn')):
        return jsonify({'error': error_codes.missing_data}), 404
    name, pw, ssn = data['name'], data['password'], data['ssn']
    if len(name) == 0 or len(pw) == 0 or len(ssn) == 0:
        return jsonify({'error': error_codes.empty_data}), 405
    if not valid_password(pw):
        return jsonify({'error': error_codes.invalid_password}), 406
    if not valid_ssn(ssn):
        return jsonify({'error': error_codes.invalid_ssn}), 407
    if db.session.query(User.id).filter_by(ssn=ssn).scalar() is not None:
        return jsonify({'error': error_codes.user_already_exists}), 408
    pw = generate_password_hash(pw, method='sha256')
    db.session.add(User(open_id=str(uuid.uuid4()), name=name, ssn=ssn, password=pw))
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/login', methods=['GET'])
def login():
    """
    Attempts to log in given value of Authentication header field
    and is returned a token if successful.

    :return: error code and potentially token and role.
    """
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'error': error_codes.missing_header_fields}), 404
    user = User.query.filter_by(ssn=auth.username).first()
    if not user or not check_password_hash(user.password, auth.password):
        return jsonify({'error': error_codes.invalid_credentials}), 405
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=50)
    token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify(
        {
            'error': error_codes.no_error,
            'token': token.decode('UTF-8'),
            'role': user.user_role
        }
    )


@app.route('/user/name/update', methods=['PUT'])
@authenticated
def update_user_name(curr_user):
    """
    Updates the name of the user given legal data.

    :param curr_user: The current session user
    :return: error code (= 0 if none)
    """
    data = request.get_json()
    if 'name' not in data:
        return jsonify({'error': error_codes.missing_data}), 401
    name = data['name']
    if len(name) == 0:
        return jsonify({'error': error_codes.empty_data}), 405
    curr_user.name = name
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/admin/user/delete/<user_id>', methods=['DELETE'])
@authenticated
def remove_user_by_id(curr_user, user_id):
    """
    Tries to remove a specific user. If the session user is
    not an admin it will fail. If the user to delete is an
    admin it will fail.

    :param curr_user: The current session user
    :param user_id: The open_id of the user to remove
    :return: error code (= 0 if none)
    """
    if curr_user.user_role != 'Admin':
        return jsonify({'error': error_codes.access_denied}), 434
    del_user = User.query.filter_by(open_id=user_id).first()
    if not del_user:
        return jsonify({'error': error_codes.no_such_user}), 444
    if del_user.user_role == 'Admin':
        return jsonify({'error': error_codes.access_denied}), 421
    db.session.delete(del_user)
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/get_user', methods=['GET'])
@authenticated
def get_user(curr_user):
    """
    Gets the information of the user that is currently
    logged in. Used for all Roles

    :param curr_user: The current session user
    :return: error code (= 0 if none) and the User information
    """
    return jsonify(
        {
            'error': error_codes.no_error,
            'user': {
                    'id': curr_user.id,
                    'ssn': curr_user.ssn,
                    'name': curr_user.name,
                    'open_id': curr_user.open_id,
                    'start_date': curr_user.start_date,
                    'expire_date': curr_user.expire_date
                }
        })


@app.route('/admin/user/name/update/<user_id>', methods=['PUT'])
@authenticated
def admin_update_user(curr_user, user_id):
    """
    Updates the name of the user given legal data.

    :param curr_user: The current session user
    :return: error code (= 0 if none)
    """
    if curr_user.user_role != 'Admin':
        return jsonify({'error': error_codes.access_denied}), 434
    update_user = User.query.filter_by(open_id=user_id).first()
    if not update_user:
        return jsonify({'error': error_codes.no_such_user}), 444
    data = request.get_json()
    if 'expire_date' not in data and 'role' not in data:
        return jsonify({'error': error_codes.missing_data}), 452
    if 'expire_date' in data:
        if len(data['expire_date']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    if 'role' in data:
        if len(data['role']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    update_user.expire_date = datetime.datetime(*tuple(map(int, list(reversed(data['expire_date'].split('/'))) + ['23', '59'])))
    update_user.user_role = data['role']
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/user/all', methods=['GET'])
@authenticated
def get_all_users(curr_user):
    """
    Gets the information of all of the users in the database
    end returns a jsonobject with their information. Checks
    if the user is a legal user and if the user has the role Admin

    :param curr_user: The current session user
    :return: error code (= 0 if none) and the User information
    for all of the Users in the database
    """
    if curr_user.user_role != 'Admin':
        return jsonify({'error': error_codes.access_denied}), 462
    return jsonify({
        'error': error_codes.no_error,
        'all_users': [{
            'name': user.name,
            'ssn': user.ssn,
            'open_id': user.open_id,
            'user_role': user.user_role,
            'start_date': user.start_date,
            'expire_date': user.expire_date
        } for user in User.query.all()]
    })


@app.route('/workout', methods=['POST'])
@authenticated
def create_workout(curr_user):
    """
    Allows admins and coaches to create a workout at a specific time
    with a specific descritpion and that workout is assigned to a coach

    :param curr_user:
    :return: error code (= 0 if none)
    """
    data = request.get_json()
    if curr_user.user_role == 'Client':
        return jsonify({'error': error_codes.access_denied}), 462
    if 'coach_id' not in data or 'description' not in data or 'date' not in data or 'time' not in data:
        return jsonify({'error': error_codes.missing_data}), 461
    coach_id = data['coach_id']
    desc = data['description']
    if 'coach_id' in data:
        if len(data['coach_id']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    if 'description' in data:
        if len(data['description']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    if 'date' in data:
        if len(data['date']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    if 'time' in data:
        if len(data['time']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
    the_coach = User.query.filter_by(open_id=coach_id).first()
    if the_coach.user_role != 'Coach':
        if the_coach.user_role != 'Admin':
            return jsonify({'error': error_codes.access_denied}), 496
    db.session.add(Workout(coach_id=coach_id, date_time=datetime.datetime(
        *tuple(map(int, list(reversed(data['date'].split('/'))) + data['time'].split(':')))), description=desc))
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/user/coaches', methods=['GET'])
@authenticated
def get_all_none_clientss(curr_user):
    """
    Gets the information of all of the coaches in the database
    end returns a jsonobject with their information. Checks
    if the user is a legal user and if the user has the role Admin
    Admins are also considered to coaches as per request of our client(Fenrir)

    :param curr_user: The current session user
    :return: error code (= 0 if none) and the User information
    for all of the non-Client Users in the database
    """
    if curr_user.user_role != 'Admin' or curr_user.user_role != 'Coach':
        return jsonify({'error': error_codes.access_denied}), 462
    return jsonify({
        'error': error_codes.no_error,
        'all_users': [{
            'name': user.name,
            'ssn': user.ssn,
            'open_id': user.open_id,
            'user_role': user.user_role,
            'start_date': user.start_date,
            'expire_date': user.expire_date
        } for user in User.query.all()
            if user.user_role != 'Client']
    })


@app.route('/workout/today/<workout_date_time>', methods=['GET'])
@authenticated
def get_workout(curr_user, workout_date_time):
    """
    Takes in a parameter workout_date_time that has to be structured
    like for example '2001-09-11-13-00-00' and if there is a workout
    at that time in the database with this date_time then it is sent
    :param curr_user, workout_date_time:
    :return: error code (= 0 if none) and the Workout information
    of the date and time sent in the url
    """
    workout_got = Workout.query.filter_by(date_time=datetime.datetime(
        *tuple(map(int, list((workout_date_time.split('-'))))))).first()
    if workout_got is None:
        return jsonify({'error': error_codes.invalid_date_time}), 487
    return jsonify(
        {
            'error': error_codes.no_error,
            'workout': {
                'id': workout_got.id,
                'coach_id': workout_got.coach_id,
                'description': workout_got.description,
                'date_time': workout_got.date_time
            }
        })


@app.route('/workout/all/<workout_date_time>', methods=['GET'])
@authenticated
def get_workouts_by_date(curr_user, workout_date_time):
    """
    Takes in a parameter workout_date_time that has to be structured
    like for example '2001-09-11' and if there is a workout
    at that time in the database with this date_time then it is sent
    :param curr_user:
    :param workout_date_time:
    :return: error code (= 0 if none) and the Workout information
    of the workouts at the date that was sent in
    """
    return jsonify({
        'error': error_codes.no_error,
        'all_workouts': [{
            'id': workout.id,
            'coach_id': workout.coach_id,
            'description': workout.description,
            'date_time': workout.date_time,
        } for workout in Workout.query.all()
            if workout.date_time.date() == datetime.datetime(
            *tuple(map(int, list((workout_date_time.split('-')))))).date()]
    })


@app.route('/workout/<workout_id>', methods=['GET'])
@authenticated
def participate_in_workout(curr_user, workout_id):
    """
    Adds the curr_user to the list of participants in the workout
    that has the id that is passed as the paramter workout_id. If the user
    is already participating it removes the connection between the user and the workout
    :param curr_user:
    :param workout_id:
    :return: error code (= 0 if none) if the workout does not exist
    then it sends an appropriate error code
    """
    workout = Workout.query.filter_by(id=workout_id).first()
    if workout is None:
        return jsonify({'error': error_codes.no_such_workout }), 431
    x = User.query.filter(User.workouts.any(id=workout_id)).first()
    if x is not None:
        curr_user.workouts.remove(workout)
    else:
        curr_user.workouts.append(workout)
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


@app.route('/admin/workout/update/<workout_id>', methods=['PUT'])
@authenticated
def admin_update_workout(curr_user, workout_id):
    """
    A function that allows the Admin to update every value bound to a
    specific id, excluding the id. 
    :param curr_user: The current session user
    :return: error code (= 0 if none)
    """
    if curr_user.user_role != 'Admin':
        return jsonify({'error': error_codes.access_denied}), 434
    update_workout = Workout.query.filter_by(id=workout_id).first()
    if not update_workout:
        return jsonify({'error': error_codes.no_such_workout}), 494
    data = request.get_json()
    if 'coach_id' not in data and 'description' not in data and 'date' not in data and 'time' not in data:
        return jsonify({'error': error_codes.missing_data}), 452
    if 'coach_id' in data:
        if len(data['coach_id']) == 0:
            return jsonify({'error': error_codes.empty_data}), 405
        update_workout.coach_id = data['coach_id']
    if 'description' in data:
        if len(data['description']) == 0:
            return jsonify({'error': error_codes.empty_data}), 406
        update_workout.description = data['description']
    if 'date' in data and 'time' in data:
        if len(data['date']) == 0 or len(data['time']) == 0:
            return jsonify({'error': error_codes.empty_data}), 407
        update_workout.date_time = datetime.datetime(*tuple(map(int, list(
            reversed(data['date'].split('/'))) + data['time'].split(':'))))
    if 'date' in data and 'time' not in data:
        if len(data['date']) == 0:
            return jsonify({'error': error_codes.empty_data}), 408
        old_time = update_workout.date_time.strftime('%H:%M')
        update_workout.date_time = datetime.datetime(*tuple(map(int, list(reversed(
            data['date'].split('/'))) + list(old_time.split(':')))))
    if 'time' in data and 'date' not in data:
        if len(data['time']) == 0:
            return jsonify({'error': error_codes.empty_data}), 409
        old_date = update_workout.date_time.strftime('%Y/%m/%d')
        update_workout.date_time = datetime.datetime(*tuple(map(int, list(
            old_date.split('/')) + data['time'].split(':'))))
    db.session.commit()
    return jsonify({'error': error_codes.no_error})


if __name__ == '__main__':
    app.run()
