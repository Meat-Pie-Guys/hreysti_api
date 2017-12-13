import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestHome(unittest.TestCase):
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

    def test_authentication_no_token(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        res = app.test_client().get('/', headers=headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_token})

    def test_authentication_no_such_user(self):
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        false_open_id = 'asdfsdafasdfasdf'
        valid_token = jwt.encode(
            {'open_id': false_open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }
        res = app.test_client().get('/', headers=headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_such_user})

    def test_authentication_invalid_token(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json', 'fenrir-token': 'ABCD1234'}
        res = app.test_client().get('/', headers=headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.invalid_token})

    def test_authentication_valid(self):
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        valid_token = jwt.encode(
            {'open_id': self.list_of_users[0].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }
        res = app.test_client().get('/', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        expected = {'error': error_codes.no_error, 'message': 'Welcome to Fenrir, Hassi'}
        self.assertEqual(json.loads(res.data), expected)


if __name__ == '__main__':
    unittest.main()