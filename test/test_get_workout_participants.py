import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestGetWorkoutParticipants(unittest.TestCase):
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

        invalid_valid_token = jwt.encode(
            {'open_id': self.list_of_users[0].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.invalid_headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': invalid_valid_token
        }

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

    def test_get_participants_with_2_participants(self):
        workout = self.list_of_workouts[0]
        workout.users = [self.list_of_users[0], self.list_of_users[1]]
        res = app.test_client().get('/workout/users/' + str(workout.id), headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'all_users': [
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[0].name,
                                                        'open_id': self.list_of_users[0].open_id,
                                                        'ssn': self.list_of_users[0].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[0].user_role
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[1].name,
                                                        'open_id': self.list_of_users[1].open_id,
                                                        'ssn': self.list_of_users[1].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[1].user_role
                                                    }
                                                ],
                                                'error': error_codes.no_error,
                                                })

    def test_get_participants_with_0_participants(self):
        workout = self.list_of_workouts[0]
        res = app.test_client().get('/workout/users/' + str(workout.id), headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'all_users': [], 'error': error_codes.no_error })

    def test_get_all_participants_as_non_admin_unsuccessfully(self):
        res = app.test_client().get('/user/all', headers=self.invalid_headers_sent)
        self.assertEqual(403, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})

    def test_get_participants_no_such_workout(self):
        res = app.test_client().get('/workout/users/' + 'thisisnotavalidworkoutid', headers=self.headers_sent)
        self.assertEqual(400, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_such_workout })

if __name__ == '__main__':
    unittest.main()
