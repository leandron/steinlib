import unittest

from mock import MagicMock

from steinlib.exceptions import SteinlibParsingException
from steinlib.instance import SteinlibInstance
from steinlib.parser import RootHeaderParser


class TestRootHeaderParser(unittest.TestCase):
    graph = SteinlibInstance()

    def test_valid_header(self):
        valid_header = '33D32945 STP File, STP Format Version 1.0'
        result = RootHeaderParser.matches(valid_header,
                                          TestRootHeaderParser.graph)
        self.assertIsNotNone(result)

    def test_case_insensitive_header(self):
        mixed_case_header = '33d32945 STP File, STP Format Version 1.0'
        result = RootHeaderParser.matches(mixed_case_header,
                                          TestRootHeaderParser.graph)
        self.assertIsNotNone(result)

    def test_incomplete_header(self):
        incomplete_header = 'XXXXXXXX'
        with self.assertRaises(SteinlibParsingException):
            RootHeaderParser.matches(incomplete_header,
                                     TestRootHeaderParser.graph)

    def test_invalid_magic_number(self):
        invalid_magic_number = 'XXXXXXXX STP File, STP Format Version 1.0'
        with self.assertRaises(SteinlibParsingException):
            RootHeaderParser.matches(invalid_magic_number,
                                     TestRootHeaderParser.graph)

    def test_right_header_callback_is_executed(self):
        mock_graph = MagicMock()
        valid_header = '33D32945 STP File, STP Format Version 1.0'
        _ = RootHeaderParser.matches(valid_header, mock_graph)
        mock_graph.header.assert_called_with(
            valid_header, ('STP File, STP Format Version 1.0',))
