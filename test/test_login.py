import base64
import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestLogin(unittest.TestCase):
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

    def test_login_success(self):
        user = self.list_of_users[0]
        authentication = base64.b64encode(bytes('{0}:{1}'.format(user.ssn, 'abcdef'), 'utf-8')).decode('utf-8')
        auth_str = 'Basic {0}'.format(authentication)
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': auth_str}
        res = app.test_client().get('/login', headers=headers_sent)
        self.assertEqual(200, res.status_code)
        body_received = json.loads(res.data)
        self.assertEqual(body_received['error'], error_codes.no_error)

    def test_login_missing_headers(self):
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        res = app.test_client().get('/login', headers=headers_sent)
        self.assertEqual({'error': error_codes.missing_header_fields}, json.loads(res.data))

    def test_login_invalid_credentials(self):
        user = self.list_of_users[0]
        # wrong pw
        authentication = base64.b64encode(bytes('{0}:{1}'.format(user.ssn, 'abcdex'), 'utf-8')).decode('utf-8')
        auth_str = 'Basic {0}'.format(authentication)
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': auth_str}
        res = app.test_client().get('/login', headers=headers_sent)
        self.assertEqual({'error': error_codes.invalid_credentials}, json.loads(res.data))
        # no such user
        authentication = base64.b64encode(bytes('{0}:{1}'.format('1111119999', 'abcdex'), 'utf-8')).decode('utf-8')
        auth_str = 'Basic {0}'.format(authentication)
        headers_sent = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': auth_str}
        res = app.test_client().get('/login', headers=headers_sent)
        self.assertEqual({'error': error_codes.invalid_credentials}, json.loads(res.data))


if __name__ == '__main__':
    unittest.main()