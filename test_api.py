from unittest import TestCase
import json

from api import *

TEST_SQLITE_URI = 'sqlite:///{path}{db_name}.db'.format(
    path='db\\',
    db_name='test'
)


class TestApi(TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLITE_URI
        db.create_all()
        self.list_of_users = [
            (User(id=1, open_id=str(uuid.uuid4()), name='Hassi', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Client', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=2, open_id=str(uuid.uuid4()), name='Bongo', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Client', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=3, open_id=str(uuid.uuid4()), name='Gudmundur-Rassgat', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Client', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=4, open_id=str(uuid.uuid4()), name='Manni', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Coach', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=5, open_id=str(uuid.uuid4()), name='Johann', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Coach', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=6, open_id=str(uuid.uuid4()), name='Arnar', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Admin', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            (User(id=7, open_id=str(uuid.uuid4()), name='Maggi', password=generate_password_hash('abcd', method='sha256'),
                  user_role='Admin', start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                  expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00))),
            ]
        for user in self.list_of_users:
            db.session.add(user)
        # Descriptions
        self.list_of_descriptions = [
            (Description(id=1, text='5 CockPushUps', type='Cock')),
            (Description(id=2, text='69 CockPushUps', type='Cock')),
        ]
        for desc in self.list_of_descriptions:
            db.session.add(desc)
        # WORKOUTS
        self.list_of_workouts = [
            (Workout(id=1, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 8, 00, 00), description_id=1)),
            (Workout(id=2, coach_id=5, date_time=datetime.datetime(2017, 11, 30, 12, 00, 00), description_id=1)),
            (Workout(id=3, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 18, 00, 00), description_id=1)),
            (Workout(id=4, coach_id=5, date_time=datetime.datetime(2017, 12, 1, 12, 00, 00), description_id=2)),
        ]
        for work in self.list_of_workouts:
            db.session.add(work)
        db.session.commit()

    # after each test
    def tearDown(self):
        db.drop_all()

    def test_get_all_users(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'token': valid_fake_token}
        res = app.test_client().get('/users', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'all_users': [
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 1, 'name': 'Hassi', 'open_id': self.list_of_users[0].open_id,
             'password': self.list_of_users[0].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Client'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 2, 'name': 'Bongo', 'open_id': self.list_of_users[1].open_id,
             'password': self.list_of_users[1].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Client'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 3, 'name': 'Gudmundur-Rassgat', 'open_id': self.list_of_users[2].open_id,
             'password': self.list_of_users[2].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Client'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 4, 'name': 'Manni', 'open_id': self.list_of_users[3].open_id,
             'password': self.list_of_users[3].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Coach'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 5, 'name': 'Johann', 'open_id': self.list_of_users[4].open_id,
             'password': self.list_of_users[4].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Coach'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 6, 'name': 'Arnar', 'open_id': self.list_of_users[5].open_id,
             'password': self.list_of_users[5].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Admin'},
            {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'id': 7, 'name': 'Maggi', 'open_id': self.list_of_users[6].open_id,
             'password': self.list_of_users[6].password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'user_role': 'Admin'}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_all_workouts(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        res = app.test_client().get('/workout', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'all_workouts': [
            {'id': 1, 'coach_id': 4, 'description_id': 1, 'date_time': 'Thu, 30 Nov 2017 08:00:00 GMT'},
            {'id': 2, 'coach_id': 5, 'description_id': 1, 'date_time': 'Thu, 30 Nov 2017 12:00:00 GMT'},
            {'id': 3, 'coach_id': 4, 'description_id': 1, 'date_time': 'Thu, 30 Nov 2017 18:00:00 GMT'},
            {'id': 4, 'coach_id': 5, 'description_id': 2, 'date_time': 'Fri, 01 Dec 2017 12:00:00 GMT'}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_get_user(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        res = app.test_client().get('/user/1', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'User': [
            {'id': user.id, 'name': user.name, 'open_id': user.open_id, 'user_role': user.user_role,
             'password': user.password, 'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_get_coaches(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        res = app.test_client().get('/user/coach/', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'all_users': [
            {'id': 4, 'name': 'Manni', 'open_id': self.list_of_users[3].open_id, 'user_role': 'Coach', 'password': self.list_of_users[3].password,
             'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'},
            {'id': 5, 'name': 'Johann', 'open_id': self.list_of_users[4].open_id, 'user_role': 'Coach', 'password': self.list_of_users[4].password,
             'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_get_clients(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        res = app.test_client().get('/user/clients/', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'all_users': [
            {'id': 1, 'name': 'Hassi', 'open_id': self.list_of_users[0].open_id, 'user_role': 'Client', 'password': self.list_of_users[0].password,
             'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'},
            {'id': 2, 'name': 'Bongo', 'open_id': self.list_of_users[1].open_id, 'user_role': 'Client', 'password': self.list_of_users[1].password,
             'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'},
            {'id': 3, 'name': 'Gudmundur-Rassgat', 'open_id': self.list_of_users[2].open_id, 'user_role': 'Client', 'password': self.list_of_users[2].password,
             'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT', 'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT'}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_user_success(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'name': 'John Tennis', 'password': '1234'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        expected = {'message': 'success'}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_user_short_password(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'name': 'John Tennis', 'password': 'ace'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        expected = {'message': 'password must be at least 4 characters'}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_user_name_taken(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'name': 'Hassi', 'password': '1234'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        expected = {'message': 'username taken'}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_user_name_empty(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'name': '', 'password': '1234'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        expected = {'message': 'name can not be empty'}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_user_missing_headers(self):
        # neither
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'some_key': 'some_val'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)
        # only name
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'name': 'John'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)
        # only password
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        body_to_send = {'password': '1234'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)

    def test_get_single_workout(self):
        user = self.list_of_users[0]
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=10)
        valid_fake_token = jwt.encode({'open_id': user.open_id, 'exp': expire_time}, app.config['SECRET_KEY'])
        self.maxDiff = None
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'x-access-token': valid_fake_token}
        res = app.test_client().get('/workout/1', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'Workout': [
            {'id': 1, 'coach_id': 4, 'date_time': 'Thu, 30 Nov 2017 08:00:00 GMT', 'description_id': 1}
        ]}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_workout_success(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'coach_id': '4', 'description_id': '2'}
        res = app.test_client().post('/workout', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        expected = {'message': 'success'}
        body_received = json.loads(res.data)
        self.assertEqual(body_received, expected)

    def test_create_workout_missing_headers(self):
        # neither
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'some_key': 'some_val'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)
        # only name
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'coach_id': '4'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)
        # only password
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'description_id': '2'}
        res = app.test_client().post('/', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(404, res.status_code)
        body_received = json.loads(res.data)
        expected = {'message': 'missing header fields'}
        self.assertEqual(body_received, expected)
        #
