import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestGetUser(unittest.TestCase):
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

    def tearDown(self):
        db.drop_all()

    def test_get_self_successfully(self):
        user = self.list_of_users[0]
        res = app.test_client().get('/get_user', headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error,
                                                'user': {'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                         'id': user.id,
                                                         'name': user.name,
                                                         'role': user.user_role,
                                                         'open_id': user.open_id,
                                                         'ssn': user.ssn,
                                                         'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT'}})


if __name__ == '__main__':
    unittest.main()