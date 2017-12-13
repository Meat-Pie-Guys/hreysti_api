import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestGetWorkoutsByDate(unittest.TestCase):
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
            {'open_id': self.list_of_users[6].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }

    def tearDown(self):
        db.drop_all()

    def test_get_workout_successfully(self):
        workout = self.list_of_workouts[0]
        res = app.test_client().get('/workout/today/' + '2017-11-30-08-00-00', headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error,
                                                'workout':
                                                    {
                                                        'id': workout.id,
                                                        'coach_id': workout.coach_id,
                                                        'description': workout.description,
                                                        'date_time': 'Thu, 30 Nov 2017 08:00:00 GMT',
                                                    }
                                                })

    def test_get_workout_unsuccessfully(self):
        res = app.test_client().get('/workout/today/' + '2017-11-30-08-15-00', headers=self.headers_sent)
        self.assertEqual(487, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.invalid_date_time })


if __name__ == '__main__':
    unittest.main()