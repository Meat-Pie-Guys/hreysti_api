import datetime

from werkzeug.security import generate_password_hash
from src.api import User, Workout


class FakeUsers:
    def __init__(self):
        self.list_of_users = [
            (
                User(
                    id=1,
                    open_id=1,
                    name='Hassi',
                    ssn='1002873319',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=2,
                    open_id=2,
                    name='Bongo',
                    ssn='1104872159',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=3,
                    open_id=3,
                    name='Gudmundur-Rassgat',
                    ssn='2810842759',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=4,
                    open_id=4,
                    name='Manni',
                    ssn='1006893169',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Coach',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=5,
                    open_id=5,
                    name='Johann',
                    ssn='0510153630',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Coach',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=6,
                    open_id=6,
                    name='Arnar',
                    ssn='3011873949',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Admin',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=7,
                    open_id=7,
                    name='Maggi',
                    ssn='2005893869',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Admin',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=8,
                    open_id=8,
                    name='Viddi',
                    ssn='1111903059',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=9,
                    open_id=9,
                    name='Hinn Arnar',
                    ssn='1503943099',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=10,
                    open_id=10,
                    name='Hoddz',
                    ssn='0104902359',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=11,
                    open_id=11,
                    name='Swan',
                    ssn='0709943569',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
            (
                User(
                    id=12,
                    open_id=12,
                    name='Swaglord',
                    ssn='1602913629',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            ),
                (
                User(
                    id=13,
                    open_id=13,
                    name='McSkerp',
                    ssn='0609605509',
                    password=generate_password_hash('abcdef', method='sha256'),
                    user_role='Client',
                    start_date=datetime.datetime(2017, 12, 7, 10, 36, 00),
                    expire_date=datetime.datetime(2017, 12, 7, 10, 36, 00)
                )
            )

        ]


class FakeWorkouts:
    def __init__(self):
        self.list_of_workouts = [
            Workout(id=1, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 8, 00, 00), description='5 CockPushUps'),
            Workout(id=2, coach_id=5, date_time=datetime.datetime(2017, 11, 30, 12, 00, 00), description='5 CockPushUps',),
            Workout(id=3, coach_id=4, date_time=datetime.datetime(2017, 11, 30, 18, 00, 00), description='5 CockPushUps',),
            Workout(id=4, coach_id=5, date_time=datetime.datetime(2017, 12, 1, 12, 00, 00), description='69 CockPushUps',),
        ]



TEST_SQLITE_URI = 'sqlite:///{path}{db_name}.db'.format(
    path='..\\db\\',
    db_name='test'
)