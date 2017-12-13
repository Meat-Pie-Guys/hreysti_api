import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestCreateWorkout(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLITE_URI
        db.create_all()
        self.list_of_users = FakeUsers().list_of_users
        for user in self.list_of_users:
            db.session.add(user)
        self.list_of_workouts = FakeWorkouts().list_of_workouts
        for work in self.list_of_workouts:
            db.session.add(work)
        db.session.commit()

        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        valid_token = jwt.encode(
            {'open_id': self.list_of_users[5].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.valid_token = valid_token
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }

    def tearDown(self):
        db.drop_all()

    def test_create_workout_success(self):
        body_to_send = {'coach_id': self.list_of_users[3].open_id, 'description': '123456', 'date': '11/11/2017',
                        'time': '12:00'}
        res = app.test_client().post('/workout', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error})

    def test_create_workout_missing_data_one(self):
        # No coach_id
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'fenrir-token': self.valid_token}
        body_to_send = {'description': '123456', 'date': '11/11/2017', 'time': '12:00'}
        res = app.test_client().post('/workout', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_create_workout_missing_data_two(self):
        # No description
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'fenrir-token': self.valid_token}
        body_to_send = {'coach_id': self.list_of_users[4].open_id, 'date': '11/11/2017', 'time': '12:00'}
        res = app.test_client().post('/workout', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_create_workout_missing_data_three(self):
        # No date
        body_to_send = {'coach_id': self.list_of_users[5].open_id, 'description': '123456', 'time': '12:00'}
        res = app.test_client().post('/workout', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_create_workout_missing_data_four(self):
        # No time
        body_to_send = {'coach_id': self.list_of_users[6].open_id, 'description': '123456', 'date': '11/11/2017'}
        res = app.test_client().post('/workout', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_create_workout_invalid_coach_id(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'fenrir-token': self.valid_token}
        body_to_send = {'description': '123456', 'coach_id': self.list_of_users[0].open_id,
                        'date': '11/11/2017', 'time': '12:00'}
        res = app.test_client().post('/workout', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})

    def test_creae_workout_already_exists(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'fenrir-token': self.valid_token}
        body_to_send = {'description': '123456', 'coach_id': self.list_of_users[4].open_id,
                        'date': '1/12/2017', 'time': '12:00'}
        res = app.test_client().post('/workout', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.workout_already_exists})


if __name__ == '__main__':
    unittest.main()
