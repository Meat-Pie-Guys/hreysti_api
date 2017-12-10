import json
import unittest

from src.api import *
from test.util.fake_data import *


class TestApi(unittest.TestCase):
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

    def tearDown(self):
        db.drop_all()

    def test_create_user_success(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '123456', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error})
        self.assertEqual(db.session.query(User.name).filter_by(ssn='9123456789').first()[0], 'John Tennis')


    def test_create_user_missing_data(self):
        # No name
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'password': '123456', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})
        # No password
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})
        # No ssn
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '123456'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_create_user_empty_data(self):
        # No name
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': '', 'password': '123456', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.empty_data})
        # No password
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.empty_data})
        # No ssn
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '123456', 'ssn': ''}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.empty_data})

    def test_create_user_invalid_password(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': 'X', 'ssn': '9123456789'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.invalid_password})

    def test_create_user_invalid_ssn(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '123456', 'ssn': 'X'}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.invalid_ssn})

    def test_create_user_ssn_taken(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body_to_send = {'name': 'John Tennis', 'password': '123456', 'ssn': self.list_of_users[0].ssn}
        res = app.test_client().post('/user', headers=headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.user_already_exists})


if __name__ == '__main__':
    unittest.main()