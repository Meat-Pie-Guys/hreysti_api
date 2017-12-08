import datetime
import uuid
from functools import wraps

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
    description_id = db.Column(db.Integer, db.ForeignKey('description.id'), primary_key=False, nullable=False)


class Description(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.Text, primary_key=False, nullable=False)
    type = db.Column(db.String(50), primary_key=False, nullable=False)


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
    user_got = User.query.filter_by(id=curr_user.id).first()
    if not user_got:
        return jsonify({'error': error_codes.no_such_user}), 444
    return jsonify(
        {
            'error': error_codes.no_error,
            'user': {
                    'id': user_got.id,
                    'ssn': user_got.ssn,
                    'name': user_got.name,
                    'open_id': user_got.open_id,
                    'start_date': user_got.start_date,
                    'expire_date': user_got.expire_date
                }
        })


@app.route('/user/all', methods=['GET'])
@authenticated
def get_all_users(curr_user):
    user_got = User.query.filter_by(id=curr_user.id).first()
    if not user_got:
        return jsonify({'error': error_codes.no_such_user}), 444
    lis = []
    all_users = User.query.all()
    for user in all_users:
        dictionary = {}
        dictionary['id'] = user.id
        dictionary['name'] = user.name
        dictionary['ssn'] = user.ssn
        dictionary['open_id'] = user.open_id
        dictionary['user_role'] = user.user_role
        dictionary['password'] = user.password
        dictionary['start_date'] = user.start_date
        dictionary['expire_date'] = user.expire_date
        lis.append(dictionary)
    return jsonify({'error': error_codes.no_error, 'all_users': lis})


if __name__ == '__main__':
    app.run()
