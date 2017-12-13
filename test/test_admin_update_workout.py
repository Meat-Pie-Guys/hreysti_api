import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestAdminUpdateWorkout(unittest.TestCase):
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
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }

    def tearDown(self):
        db.drop_all()

    def test_admin_update_workout_success(self):
        workout = self.list_of_workouts[0]
        body_to_send = {'description': '5 Cock-thrusts and wrestle a bear'}
        res = app.test_client().put('/admin/workout/update/' + str(workout.id),
                                    headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error})

    def test_admin_update_workout_missing_data(self):
        workout = self.list_of_workouts[0]
        body_to_send = {'A': 'B'}
        res = app.test_client().put('/admin/workout/update/' + str(workout.id),
                                    headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_admin_upgrade_workout_coach_id_invalid_data(self):
        workout = self.list_of_workouts[0]
        body_to_send = {'coach_id': ''}
        res = app.test_client().put('/admin/workout/update/' + str(workout.id),
                                    headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.empty_data})

    def test_admin_update_role_invalid(self):
        tmp_oid = self.list_of_users[0].open_id
        body_to_send = {'role': 'Rocket'}
        res = app.test_client().put('/admin/user/name/update/' + tmp_oid,
                                    headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.invalid_role})


if __name__ == '__main__':
    unittest.main()