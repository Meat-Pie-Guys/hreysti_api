import datetime
import uuid

from werkzeug.security import generate_password_hash
from src.api import User, Workout


class FakeWorkouts:
    def __init__(self):
        self.list_of_workouts = [
            Workout(id=1, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 8, 00, 00), description='5 CockPushUps'),
            Workout(id=2, coach_id=5, date_time=datetime.datetime(2017, 11, 30, 12, 00, 00), description='5 CockPushUps',),
            Workout(id=3, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 18, 00, 00), description='5 CockPushUps',),
            Workout(id=4, coach_id=5, date_time=datetime.datetime(2017, 12, 1, 12, 00, 00), description='69 CockPushUps',),
        ]


class FakeUsers:
    def __init__(self):
        self.list_of_users = [
            (
                User(
                    id=1,
                    open_id=str(uuid.uuid4()),
                    name='Hassi',
                    ssn='0123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=2,
                    open_id=str(uuid.uuid4()),
                    name='Bongo',
                    ssn='1123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=3,
                    open_id=str(uuid.uuid4()),
                    name='Gudmundur-Rassgat',
                    ssn='2123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=4,
                    open_id=str(uuid.uuid4()),
                    name='Manni',
                    ssn='3123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Coach',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=5,
                    open_id=str(uuid.uuid4()),
                    name='Johann',
                    ssn='4123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Coach',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=6,
                    open_id=str(uuid.uuid4()),
                    name='Arnar',
                    ssn='5123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Admin',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=7,
                    open_id=str(uuid.uuid4()),
                    name='Maggi',
                    ssn='6123456789',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Admin',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            )
        ]


TEST_SQLITE_URI = 'sqlite:///{path}{db_name}.db'.format(
    path='..\\db\\',
    db_name='test'
)