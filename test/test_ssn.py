from unittest import TestCase
from src.validator import is_valid


class TestIsValid(TestCase):

    def setUp(self):
        self.valid = [
            '1405433229',
            '1601017170',
            '100287-3319',
            '3011873949',
            '301187-3949'
        ]

    def testInvalidNone(self):
        self.assertFalse(is_valid(None))

    def testInvalidNotString(self):
        self.assertFalse(is_valid(1012821313))

    def testInvalidWrongLength(self):
        self.assertFalse(is_valid('1231'))

    def testInvalidWrongCentury(self):
        self.assertFalse(is_valid('150599-1608'))
        self.assertFalse(is_valid('150599-1604'))

    def testInvalidIncorrectDate(self):
        self.assertFalse(is_valid('330189-1999'))
        self.assertFalse(is_valid('151389-1999'))
        self.assertFalse(is_valid('290201-1990'))

    def testInvalidCheckSum(self):
        for ssn in self.valid:
            lis = list(ssn)
            c = int(lis[-2])
            for i in range(10):
                if c != i:
                    lis[-2] = str(i)
                    self.assertFalse(is_valid(''.join(lis)))

    def testValid(self):
        for ssn in self.valid:
            self.assertTrue(ssn)

    def testValidCompanySSNToFail(self):
        self.assertFalse(is_valid('681201-2890'))

