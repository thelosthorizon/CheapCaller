import unittest

from cheap_caller import parser

class TestParser(unittest.TestCase):

    def test_raises_system_exit__no_args(self):
        # negative test, check behavior when too few arguments
        args = []
        with self.assertRaises(SystemExit):
            parser.parse(args)

    def test_raises_system_exit__not_all_positional_args(self):
        # negative test, check behavior when no operatordir provided
        args = ["12345"]
        with self.assertRaises(SystemExit):
            parser.parse(args)

    def test_raises_system_exit__operatordir_doesnot_exist(self):
        # negative test, check behavior when operatordir does not exist
        args = ["12345", "bullshit"]
        with self.assertRaises(SystemExit):
            parser.parse(args)

    def test_ok__all_positional_args(self):
        # check when all positional args provided
        # all positional arguments are parsed as expected
        args = ["12345", "data"]
        parsed = parser.parse(args)
        self.assertIn("operatordir", parsed)
        self.assertEqual(parsed["operatordir"], "data")
        self.assertIn("phoneno", parsed)
        self.assertEqual(parsed["phoneno"], "12345")

    def test_has__parsed_optional_args_default(self):
        # check that optional args have default values
        args = ["12345", "data"]
        parsed = parser.parse(args)
        self.assertIn("log_level", parsed)
        self.assertEqual(parsed["log_level"], "info")
        self.assertIn("pattern", parsed)
        self.assertEqual(parsed["pattern"], "*.operator")

    def test_has__parsed_optional_args_not_default(self):
        # check that optional args have passed values
        args = ["12345", "data", "-ll", "error", "-p", "something"]
        parsed = parser.parse(args)
        self.assertIn("log_level", parsed)
        self.assertEqual(parsed["log_level"], "error")
        self.assertIn("pattern", parsed)
        self.assertEqual(parsed["pattern"], "something")

    def test_ok__long_version_optional_arg(self):
        # check that long version of optional are also parsed
        args = ["12345", "data", "--log-level", "error", "--pattern", "something"]
        parsed = parser.parse(args)
        self.assertIn("log_level", parsed)
        self.assertEqual(parsed["log_level"], "error")
        self.assertIn("pattern", parsed)
        self.assertEqual(parsed["pattern"], "something")

if __name__ == '__main__':
    unittest.main()