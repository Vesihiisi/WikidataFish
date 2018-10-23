#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import wikidatafish.utils as utils


class TestDatetimeMethods(unittest.TestCase):

    def test_date_to_dict_1(self):
        text = "1999-12-09"
        template = "%Y-%m-%d"
        output = {"year": 1999, "month": 12, "day": 9}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_2(self):
        text = "09-12-1999"
        template = "%d-%m-%Y"
        output = {"year": 1999, "month": 12, "day": 9}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_3(self):
        text = "12-1999"
        template = "%m-%Y"
        output = {"year": 1999, "month": 12}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_4(self):
        text = "1999"
        template = "%Y"
        output = {"year": 1999}
        self.assertEqual(utils.date_to_dict(text, template), output)


class TestStringMethods(unittest.TestCase):
    def test_string_is_q_item_pass(self):
        self.assertTrue(utils.string_is_q_item("Q1641992"))

    def test_string_is_q_item_fail(self):
        self.assertFalse(utils.string_is_q_item("a string"))

    def test_string_is_q_item_invalid(self):
        self.assertFalse(utils.string_is_q_item("Q1641992sss"))


if __name__ == '__main__':
    unittest.main()
