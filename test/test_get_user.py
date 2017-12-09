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
        self.list_of_descriptions = FakeDescriptions().list_of_descriptions
        for desc in self.list_of_descriptions:
            db.session.add(desc)
        self.list_of_workouts = FakeWorkouts().list_of_workouts
        for work in self.list_of_workouts:
            db.session.add(work)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    def test_get_self_successfully(self):
        self.assertTrue(False)