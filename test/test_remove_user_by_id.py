import unittest

from flask import json

from src.api import *
from test.util.fake_data import *


class TestRemoveUserById(unittest.TestCase):
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

    def test_remove_user_success(self):
        u_id = self.list_of_users[0].open_id
        res = app.test_client().delete('/admin/user/delete/{0}'.format(u_id), headers=self.headers_sent)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_error})
        self.assertIsNone(db.session.query(User.id).filter_by(open_id=u_id).scalar())

    def test_remove_user_as_non_admin(self):
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        valid_token = jwt.encode(
            {'open_id': self.list_of_users[1].open_id, 'exp': expire_time},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        headers_sent = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'fenrir-token': valid_token
        }
        u_id = self.list_of_users[0].open_id
        res = app.test_client().delete('/admin/user/delete/{0}'.format(u_id), headers=headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})
        self.assertIsNotNone(db.session.query(User.id).filter_by(open_id=u_id).scalar())

    def test_remove_user_that_does_not_exist(self):
        u_id = self.list_of_users[0].open_id
        res = app.test_client().delete('/admin/user/delete/asdfasdf231fasdf123', headers=self.headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.no_such_user})
        self.assertIsNotNone(db.session.query(User.id).filter_by(open_id=u_id).scalar())

    def test_remove_user_that_is_also_an_admin(self):
        u_id = self.list_of_users[5].open_id
        res = app.test_client().delete('/admin/user/delete/{0}'.format(u_id), headers=self.headers_sent)
        self.assertEqual(json.loads(res.data), {'error': error_codes.access_denied})
        self.assertIsNotNone(db.session.query(User.id).filter_by(open_id=u_id).scalar())

