import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestGetAll(unittest.TestCase):
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
        invalid_token = jwt.encode(
            {'open_id': self.list_of_users[0].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        self.valid_token = valid_token
        self.headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }
        self.headers_sent2 = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': invalid_token
        }

    def tearDown(self):
        db.drop_all()

    def test_get_all_users_as_admin_successfully(self):
        res = app.test_client().get('/user/all', headers=self.headers_sent)
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
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[2].name,
                                                        'open_id': self.list_of_users[2].open_id,
                                                        'ssn': self.list_of_users[2].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[2].user_role
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[3].name,
                                                        'open_id': self.list_of_users[3].open_id,
                                                        'ssn': self.list_of_users[3].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[3].user_role
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[4].name,
                                                        'open_id': self.list_of_users[4].open_id,
                                                        'ssn': self.list_of_users[4].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[4].user_role
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[5].name,
                                                        'open_id': self.list_of_users[5].open_id,
                                                        'ssn': self.list_of_users[5].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[5].user_role
                                                    },
                                                    {
                                                        'expire_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'name': self.list_of_users[6].name,
                                                        'open_id': self.list_of_users[6].open_id,
                                                        'ssn': self.list_of_users[6].ssn,
                                                        'start_date': 'Thu, 07 Dec 2017 10:36:00 GMT',
                                                        'user_role': self.list_of_users[6].user_role
                                                    }
                                                ],
                                                'error': error_codes.no_error,
                                                })

    def test_get_all_users_as_non_admin_unsuccessfully(self):
        res = app.test_client().get('/user/all', headers=self.headers_sent2)
        self.assertEqual(403, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})


if __name__ == '__main__':
    unittest.main()