import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestUpdateUserName(unittest.TestCase):
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

    def test_update_user_name_success(self):
        tmp_oid = self.list_of_users[0].open_id
        tmp_ssn = self.list_of_users[0].ssn
        body_to_send = {'name': 'Herbie Hancock'}
        res = app.test_client().put('/user/name/update', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error})
        name, ssn = db.session.query(User.name, User.ssn).filter_by(open_id=tmp_oid).first()
        self.assertEqual(name, 'Herbie Hancock')
        self.assertEqual(ssn, tmp_ssn)

    def test_update_user_name_missing_data(self):
        body_to_send = {'A': 'B'}
        res = app.test_client().put('/user/name/update', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.missing_data})

    def test_upgrade_user_name_invalid_data(self):
        body_to_send = {'name': ''}
        res = app.test_client().put('/user/name/update', headers=self.headers_sent, data=json.dumps(body_to_send))
        self.assertEqual(json.loads(res.data), {'error': error_codes.empty_data})