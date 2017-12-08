def valid_password(pw):
    """

    :param pw:
    :return:
    """
    return len(pw) > 5


def valid_ssn(ssn):
    """

    :param ssn:
    :return:
    """
    return len(ssn) == 10  # TODO: replace with ssn regex
