import datetime
import uuid
import jwt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '>kz9q>GnW<>~_.7,8cw_-/xA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db\\fenrir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##########
# TABLES #
##########

participates = db.Table(
    'Participates',
    db.Column('u_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('w_id', db.Integer, db.ForeignKey('workout.id', ondelete='CASCADE'), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    open_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), primary_key=False, nullable=False)
    password = db.Column(db.String(50), primary_key=False, nullable=False)
    user_role = db.Column(db.String(12), primary_key=False, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    expire_date = db.Column(db.DateTime, nullable=True)
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


class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), primary_key=False, nullable=False)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'x-access-token' not in request.headers:
            return jsonify({'message': 'no token'}), 404
        token = request.headers['x-access-token']
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            curr_user = User.query.filter_by(open_id=data['open_id']).first()
            return f(curr_user, *args, **kwargs)
        except jwt.DecodeError:
            return jsonify({'message': 'invalid token'}), 404
    return decorated


@app.route('/login', methods=['GET'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'missing header fields'}), 404
    user = User.query.filter_by(name=auth.username).first()
    if not user or not check_password_hash(user.password, auth.password):
        return jsonify({'message': 'invalid credentials'})
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=5)
    token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})


@app.route('/users', methods=['GET'])
def get_all_users():
    lis = []
    all_users = User.query.all()
    for user in all_users:
        dictionary = {}
        dictionary['id'] = user.id
        dictionary['name'] = user.name
        dictionary['open_id'] = user.open_id
        dictionary['user_role'] = user.user_role
        dictionary['password'] = user.password
        dictionary['start_date'] = user.start_date
        dictionary['expire_date'] = user.expire_date
        lis.append(dictionary)
    return jsonify({'all_users': lis})


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user_got = User.query.filter_by(id=id).first()
    return jsonify(
        {
            'User': [
                {
                    'id': user_got.id,
                    'name': user_got.name,
                    'open_id': user_got.open_id,
                    'user_role': user_got.user_role,
                    'password': user_got.password,
                    'start_date': user_got.start_date,
                    'expire_date': user_got.expire_date
                }
            ]})


@app.route('/user/coach/', methods=['GET'])
def get_coaches():
    lis = []
    all_users = User.query.all()
    for user in all_users:
        if user.user_role == 'Coach':
            dictionary = {}
            dictionary['id'] = user.id
            dictionary['name'] = user.name
            dictionary['open_id'] = user.open_id
            dictionary['user_role'] = user.user_role
            dictionary['password'] = user.password
            dictionary['start_date'] = user.start_date
            dictionary['expire_date'] = user.expire_date
            lis.append(dictionary)
    return jsonify({'all_users': lis})


@app.route('/user/clients/', methods=['GET'])
def get_clients():
    lis = []
    all_users = User.query.all()
    for user in all_users:
        if user.user_role == 'Client':
            dictionary = {}
            dictionary['id'] = user.id
            dictionary['name'] = user.name
            dictionary['open_id'] = user.open_id
            dictionary['user_role'] = user.user_role
            dictionary['password'] = user.password
            dictionary['start_date'] = user.start_date
            dictionary['expire_date'] = user.expire_date
            lis.append(dictionary)
    return jsonify({'all_users': lis})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'name' not in data or 'password' not in data:
        return jsonify({'message': 'missing header fields'}), 404
    pw = data['password']
    if len(name) == 0:
        return jsonify({'message': 'name can not be empty'}), 404
    if db.session.query(User.id).filter_by(name=name).scalar() is not None:
        return jsonify({'message': 'username taken'}), 404
    if len(pw) < 4:
        return jsonify({'message': 'password must be at least 4 characters'}), 404
    pw = generate_password_hash(pw, method='sha256')
    db.session.add(User(open_id=str(uuid.uuid4()), name=name, password=pw, user_role='Client',
                        start_date=datetime.datetime.today(), expire_date=datetime.datetime.today()))
    db.session.commit()
    return jsonify({'message': 'success'})


@app.route('/delete/user/<int:id>/', methods=['GET'])
def remove_user(id):
    user_gone = User.query.get_or_404(id)
    db.session.delete(user_gone)
    db.session.commit()
    return jsonify({'message': 'success'})


@app.route('/update/user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    data = request.get_json()
    curr_user = User.query.get_or_404(id)
    if 'name' in data:
        curr_user.name = data['name']
    if 'user_role' in data:
        curr_user.user_role = data['user_role']
    if 'password' in data:
        if len(data['password']) < 4:
            return jsonify({'message': 'password must be at least 4 characters'}), 404
        else:
            curr_user.password = generate_password_hash(data['password'], method='sha256')
    if 'expire_date' in data:
        curr_user.expire_date = data['expire_date']
    return jsonify({'message': 'success'})


###################
# WORKOUT QUERIES #
###################
@app.route('/workout', methods=['GET'])
def all_workouts():
    lis = []
    all_work = Workout.query.all()
    for workout in all_work:
        dictionary = {}
        dictionary['id'] = workout.id
        dictionary['coach_id'] = workout.coach_id
        dictionary['description_id'] = workout.description_id
        dictionary['date_time'] = workout.date_time
        lis.append(dictionary)
    return jsonify({'all_workouts': lis})


@app.route('/workout/coach/<int:id>/', methods=['GET'])
def coach_workouts(id):
    workouts = Workout.query.all()
    lis = []
    descript = Description.query.all()
    for workout in workouts:
        if workout.coach_id == id:
            dictionary = {}
            dictionary['id'] = workout.id
            dictionary['coach_id'] = workout.coach_id
            dictionary['description'] = workout.description_id
            for d in descript:
                if workout.description_id == d.id:
                    dictionary['description'] = d.text
                    dictionary['type'] = d.type
            dictionary['date_time'] = workout.date_time
            lis.append(dictionary)
    return jsonify({'all_workouts': lis})


@app.route('/workout/<int:id>/', methods=['GET'])
def get_workout(id):
    workout_got = Workout.query.filter_by(id=id).first()
    return jsonify(
        {
            'Workout': [
                {
                    'id': workout_got.id,
                    'coach_id': workout_got.coach_id,
                    'date_time': workout_got.date_time,
                    'description_id': workout_got.description_id,
                }
            ]})


@app.route('/s', methods=['POST'])
def create_workout():
    data = request.get_json()
    if 'coach_id' not in data or 'description_id' not in data:
        return jsonify({'message': 'missing header fields'}), 404
    coach = data['coach_id']
    desc_id = data['description_id']
    if len(coach) == 0 or len(desc_id) == 0:
        return jsonify({'message': 'Fields cannot be empty'}), 404
    #Veryify that coach_id is correct
    db.session.add(Workout(coach_id=coach, date_time=datetime.datetime.utcnow(), description_id=desc_id))
    db.session.commit()
    return jsonify({'message': 'success'})


@app.route('/description', methods=['POST'])
def create_description(curr_user):
    data = request.get_json()
    if 'text' not in data or 'type' not in data:
        return jsonify({'message': 'missing header fields'}), 404
    text = data['text']
    type = data['type']
    if len(text) == 0 or len(type) == 0:
        return jsonify({'message': 'Fields cannot be empty'}), 404
    db.session.add(Description(text=text, type=type))
    db.session.commit()
    return jsonify({'message': 'success'})


@app.route('/workout/today', methods=['GET'])
def get_workout_by_date():
    currentdate = datetime.datetime.today()
    print(currentdate)
    all_work = Workout.query.all()
    lis = []
    for workout in all_work:
        print(workout.date_time.date())
        if workout.date_time.date() == currentdate:
            dictionary = {}
            dictionary['id'] = workout.id
            dictionary['coach_id'] = workout.coach_id
            dictionary['description_id'] = workout.description_id
            dictionary['date_time'] = workout.date_time
            lis.append(dictionary)
    return jsonify({'all_workouts': lis})

if __name__ == '__main__':
    db.create_all()
    app.run()