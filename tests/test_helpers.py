import os
import types
import logging
import unittest

from cheap_caller import helpers


class TestHelpers(unittest.TestCase):
    conf_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_logging_conf.json"
        )
    )
    test_operatordir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "data",
        )
    )

    test_operator_file1 = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_data1.txt"
        )
    )
    test_operator_file2 = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_data2.txt"
        )
    )


    def test_ok__read_logging_conf_file_no_input(self):
        # Test the default behavior
        # Two handlers: screen(level:INFO), rotatingfilehandler(level:debug)
        # cheap_caller logger's log level is DEBUG
        helpers.read_logging_conf_file()
        logger = logging.getLogger("cheap_caller")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 2)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.INFO)
        self.assertIsInstance(logger.handlers[1], logging.handlers.RotatingFileHandler)
        self.assertEqual(logger.handlers[1].level, logging.DEBUG)

    def test_ok__read_logging_conf_file_with_input(self):
        # Test with a test config file.
        # Check if named logger has appropriate level and
        # verify handlers(name, level) as defined in config file
        helpers.read_logging_conf_file(self.conf_file)
        logger = logging.getLogger("test")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.WARNING)
        self.assertEqual(logger.handlers[0].name, "screen")

    def test_ok__configure_logger_valid_log_level(self):
        # check if logging level of streamhandler changes
        # when configure_logger is called with a valid log level
        helpers.read_logging_conf_file(self.conf_file)
        logger = helpers.configure_logger("test", "info")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.INFO)

    def test_ok__configure_logger_invalid_log_level(self):
        # check if logging level of streamhandler is default
        # when configure_logger is called with invalid log level
        helpers.read_logging_conf_file(self.conf_file)
        logger = helpers.configure_logger("test", "jadv")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.WARNING)

    def test_ok__gen_find(self):
        out = helpers.gen_find("*.operator", self.test_operatordir)
        self.assertListEqual(list(out), [])
        out = helpers.gen_find("*.txt", self.test_operatordir)
        self.assertEqual(
            list(out),
            [
                '/home/sulav/personal_stuffs/CheapCaller/tests/data/test_data1.txt',
                '/home/sulav/personal_stuffs/CheapCaller/tests/data/test_data2.txt',
            ]
        )

    def test_ok__open_files(self):
        # Check if open_files returns a sequence of dicts with
        # expected named fields and value types
        file_gen = helpers.open_files(
            [self.test_operator_file1, "somesummy.txt"]
        )
        self.assertIsInstance(file_gen, types.GeneratorType)
        file_gen = list(file_gen)
        self.assertEqual(len(file_gen), 1)
        for adict in file_gen:
            self.assertIsInstance(adict, types.DictionaryType)
            self.assertIn("name", adict)
            self.assertEqual(adict["name"], "test_data1")
            self.assertIn("source", adict)
            self.assertIsInstance(adict["source"], types.FileType)

    def test_ok__gen_right_triangle(self):
        # Test for expected output for a given string
        out = helpers.gen_right_triangle("1234")
        self.assertListEqual(out, ["12", "123", "1234"])

    def test_ok__remove_leading_plus_and_zeros(self):
        # Test that + and 00 are stripped for a given string
        for val in ["+00123400", "00+123400", "123400"]:
            out = helpers.remove_leading_plus_and_zeros(val)
            self.assertEqual(out, "123400")

    def test_ok__sanitize_phoneno(self):
        # Test that +, 00 and -are stripped for a given phone number
        for val in ["+123-456-000", "+123456000"]:
            out = helpers.sanitize_and_validate_phoneno(val)
            self.assertEqual(out, "123456000")

    def test_raises_value_error__sanitize_phoneno(self):
        # Should raise ValueError with different messages
        # for different bogus input phone numbers
        inputs = ["123akbkab", "akbkab", ""]
        error_messages = [
            "invalid literal for float(): {}",
            "could not convert string to float: {}",
            "No phoneno provided{}"
        ]
        zipped = zip(inputs, error_messages)
        for val in zipped:
            with self.assertRaises(ValueError) as cm:
                helpers.sanitize_and_validate_phoneno(val[0])
            self.assertEqual(
                val[1].format(val[0]),
                str(cm.exception)
            )

    def test_ok__gen_lines(self):
        # Test for expected output with a given
        # test file obj
        with open(self.test_operator_file1) as file_obj:
            self.assertListEqual(
                list(helpers.gen_lines("something", file_obj)),
                [["4673", "0.9"], ["46732", "1.1"],  ["467321", "0.5"], ["1234", "0.2"]]
            )

    def test_ok__filter_using_startswith(self):
        # Test for output with a prefix that exists in test data
        # and a prefix that does not
        inputs = ["123", "456"]
        outputs = [[["1234", "0.2"]], []]
        zipped = zip(inputs, outputs)
        with open(self.test_operator_file1) as file_obj:
            lines = helpers.gen_lines("something", file_obj)
            dictseq = ({"source": lines, "name": "something"} for _ in xrange(1))
            for val in zipped:
                out = helpers.filter_using_startswith(dictseq, val[0])
                for adict in out:
                    self.assertListEqual(
                        list(adict["source"]),
                        val[1]
                    )

    def test_ok__cheapest_per_operator(self):
        # Check that for two given test operator files
        # a dict with expected test operator and price is returned
        inputs = [self.test_operator_file1, self.test_operator_file2]
        names = ["test_data1", "test_data2"]
        dictseq = (
            {"source": helpers.gen_lines(names[index], open(inputs[index])), "name": names[index]}
            for index in xrange(len(inputs))
        )
        out = helpers.get_cheapest_per_operator(
            dictseq,
            helpers.gen_right_triangle("4673210")
        )
        self.assertDictEqual(
            out,
            {"test_data1": 0.5, "test_data2": 1.1}
        )

    def test_ok__get_cheapest(self):
        # Test that for a given dict containing cheapest per operator data
        # a tuple with expected test operator and price is returned
        input_dict = {"test_data1": 0.5, "test_data2": 1.1}
        out = helpers.get_cheapest(input_dict)
        self.assertTupleEqual(out, ("test_data1", 0.5))



if __name__ == "__main__":
    unittest.main()
