import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestGetCoachWorkoutsByDate(unittest.TestCase):
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
            {'open_id': self.list_of_users[4].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }

        invalid_token = jwt.encode(
            {'open_id': self.list_of_users[0].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.invalid_headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': invalid_token
        }

    def tearDown(self):
        db.drop_all()

    def test_get_coach_workouts_successfully(self):
        workout = self.list_of_workouts[1]
        self.maxDiff = None
        res = app.test_client().get('/workout/coach/' + '2017-12-1', headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        """
        self.assertEqual(json.loads(res.data), {'all_workouts': [
            {
                'attending': db.session.query(Workout).join(Workout.users).filter(
                    Workout.id == workout.id).count(),
                'coach_name': User.query.filter_by(
                    id=self.list_of_users[4].id).first().name,
                'date_time': 'Fri, 1 Dec 2017 12:00:00 GMT',
                'description': workout.description,
                'id': workout.id
            }
        ],
            'error': error_codes.no_error,
        })
        """

    def test_get_workout_unsuccessfully(self):
        res = app.test_client().get('/workout/coach/' + '2017-11-30', headers=self.invalid_headers_sent)
        self.assertEqual(403, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})

    def test_get_workouts_successfully_no_workout(self):
        self.maxDiff = None
        res = app.test_client().get('/workout/coach/' + '2016-12-01', headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'all_workouts': [], 'error': error_codes.no_error })

if __name__ == '__main__':
    unittest.main()
