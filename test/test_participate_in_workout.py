import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestParticipateInWorkout(unittest.TestCase):
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
            {'open_id': self.list_of_users[0].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }

        valid_token2 = jwt.encode(
            {'open_id': self.list_of_users[12].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.headers_sent2 = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token2
        }

    def tearDown(self):
        db.drop_all()

    def test_participate_attend_succesfully(self):
        workout = self.list_of_workouts[0]
        res = app.test_client().get('/workout/' + str(workout.id), headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error, 'message': 'attended'})

    def test_participate_and_remove_self_successfully(self):
        self.list_of_users[0].workouts = [self.list_of_workouts[0], self.list_of_workouts[1]]
        workout = self.list_of_workouts[0]
        res = app.test_client().get('/workout/' + str(workout.id), headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error, 'message': 'removed'})

    def test_participate_no_such_workout(self):
        res = app.test_client().get('/workout/' + '69', headers=self.headers_sent)
        self.assertEqual(400, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_such_workout})

    def test_participate_workout_full(self):
        workout = self.list_of_workouts[0]
        workout.users = [self.list_of_users[0], self.list_of_users[1], self.list_of_users[2], self.list_of_users[3],
                         self.list_of_users[4], self.list_of_users[5], self.list_of_users[6], self.list_of_users[7],
                         self.list_of_users[11], self.list_of_users[10], self.list_of_users[9], self.list_of_users[8], ]
        res = app.test_client().get('/workout/' + str(workout.id), headers=self.headers_sent2)
        self.assertEqual(400, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.workout_is_full})


if __name__ == '__main__':
    unittest.main()
