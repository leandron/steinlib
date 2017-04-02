import unittest

from mock import MagicMock

from steinlib.exceptions import SteinlibParsingException
from steinlib.instance import SteinlibInstance
from steinlib.parser import RootEofParser


class TestRootEofParser(unittest.TestCase):
    graph = SteinlibInstance()

    def test_valid_eof(self):
        upper_case_eof = 'EOF'
        result = RootEofParser.matches(upper_case_eof,
                                       TestRootEofParser.graph)
        self.assertIsNotNone(result)

    def test_case_insensitive_eof(self):
        mixed_case_eof = 'eOf'
        result = RootEofParser.matches(mixed_case_eof,
                                       TestRootEofParser.graph)
        self.assertIsNotNone(result)

    def test_invalid_eof(self):
        invalid_eof = 'begin'
        with self.assertRaises(SteinlibParsingException):
            RootEofParser.matches(invalid_eof,
                                  TestRootEofParser.graph)

    def test_right_eof_callback_is_executed(self):
        mock_graph = MagicMock()
        valid_eof = 'EOF'
        _ = RootEofParser.matches(valid_eof, mock_graph)
        mock_graph.eof.assert_called_with('EOF', ())
