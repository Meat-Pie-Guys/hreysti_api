import datetime
import re


def valid_password(pw):
    """

    :param pw:
    :return:
    """
    return len(pw) > 5


def is_valid(ssn):
    """
    Validates an Icelandic ssn for people. It
    does not matter if the ssn is of the form
    'xxxxxx-xxxx' or 'xxxxxxxxxx'. It assumes
    people being born in the current century
    or the last.

    :param ssn: a string containing a ssn
    :type ssn: str
    :return: True iff ssn is a valid icelandic ssn
    """
    if ssn is None:
        return False
    if type(ssn) != str:
        return False
    ssn = re.sub('[^0-9]', '', ssn)
    if len(ssn) != 10:
        return False
    if ssn[-1] not in ['0', '9']:
        return False
    day, month, year = ssn[0:2], ssn[2:4], ('19' if ssn[-1] == '9' else '20') + ssn[4:6]
    try:
        datetime.date(*tuple(map(lambda z: int(z), [year, month, day])))
    except ValueError:
        return False
    c = int(ssn[-2])
    return c == (11 - (sum([a * b for a, b in zip(map(int, list(ssn[0:8])), [3, 2, 7, 6, 5, 4, 3, 2])]) % 11)) % 11


def valid_role(role):
    if role is None:
        return False
    if type(role) != str:
        return False
    if role == 'Coach':
        return True
    if role == 'Client':
        return True
    if role == 'Admin':
        return True
