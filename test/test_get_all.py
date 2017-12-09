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

    def tearDown(self):
        db.drop_all()

    def test_get_all_users_as_admin_successfully(self):
        self.assertTrue(False)

    def test_get_all_users_as_non_admin_unsuccessfully(self):
        self.assertTrue(False)