import unittest

from mock import MagicMock

from steinlib.exceptions import SteinlibParsingException
from steinlib.instance import SteinlibInstance
from steinlib.parser import SteinlibParser, RootHeaderParser
from steinlib.state import ParsingState


class TestSteinlibParser(unittest.TestCase):
    HEADER = '33D32945 STP File, STP Format Version 1.0'
    EOF = 'eof'
    SECTION_START = 'SECTION Comment'
    SECTION_END = 'END'

    def test_simple_empty_section(self):
        lines = (
            TestSteinlibParser.HEADER,
            TestSteinlibParser.SECTION_START,
            TestSteinlibParser.SECTION_END,
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(lines)

    def test_wait_for_header_state(self):
        try:
            sut = SteinlibParser([], None)
            sut.parse()
        except SteinlibParsingException as ex:
            # check state even when the parser throws an (expected) exception
            self.assertEquals(sut._state, ParsingState.wait_for_header,
                              'Initial should be wait_for_header. '
                              'expecting %s but is %s' %
                              (ParsingState.wait_for_header, sut._state))

    def test_wait_for_section_state(self):
        lines = (
            TestSteinlibParser.HEADER,
        )
        steiner_instance = SteinlibInstance()

        try:
            sut = SteinlibParser(lines, steiner_instance)
            sut.parse()
        except SteinlibParsingException as ex:
            # check state even when the parser throws an (expected) exception
            self.assertEquals(sut._state, ParsingState.wait_for_section,
                              'Initial should be wait_for_section. '
                              'expecting %s but is %s' %
                              (ParsingState.wait_for_section, sut._state))

    def test_ignore_blank_lines__spaces__tabs(self):
        lines = (
            '', '  ',  # a few spaces
            TestSteinlibParser.HEADER,
            '   ',  # TAB
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(lines)

    def test_ignore_comment_lines(self):
        lines = (
            '# first line is a comment',
            '# so, this is a comment. should be ignored',
            '',
            TestSteinlibParser.HEADER,
            '# another comment here. problem ?',
            '',  # spaces
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(lines)

    def test_ignore_mixed_tabs_spaces_comments(self):
        lines = (
            '# first line is a comment',
            '# so, this is a comment. should be ignored',
            '   ',
            TestSteinlibParser.HEADER,
            '# another comment here. problem ?  ',
            '               ',  # spaces
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(lines)

    def test_empty_lines_after_eof_dont_break_flow(self):
        lines = (
            TestSteinlibParser.HEADER,
            TestSteinlibParser.SECTION_START,
            TestSteinlibParser.SECTION_END,
            TestSteinlibParser.EOF,
            '', '', '', '   ',
        )
        self._assert_complete_successfully(lines)

    def test_unexpected_eof(self):
        with self.assertRaises(SteinlibParsingException):
            lines = (
                TestSteinlibParser.HEADER,
                TestSteinlibParser.EOF,  # <--- illegal 'EOF'
                TestSteinlibParser.SECTION_START,
                TestSteinlibParser.SECTION_END,
            )
            steiner_instance = SteinlibInstance()
            sut = SteinlibParser(lines, steiner_instance)
            sut.parse()

    def test_all_callbacks_are_called__mock(self):
        steiner_instance = MagicMock()
        lines = (
            TestSteinlibParser.HEADER,
            TestSteinlibParser.SECTION_START,
            TestSteinlibParser.SECTION_END,
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(lines,
                                           steiner_instance=steiner_instance)
        # parameters (i.e. 'assert_called_with') are being validated in each
        # specific test class (e.g TestRootEofParser, TestRootHeaderParser)
        steiner_instance.header.assert_called()
        steiner_instance.section.assert_called()
        steiner_instance.comment.assert_called()
        steiner_instance.comment__end.assert_called()
        steiner_instance.eof.assert_called()

    def test_all_callbacks_are_called__real(self):
        steiner_instance = SteinlibInstance()
        lines = (
            TestSteinlibParser.HEADER,
            TestSteinlibParser.SECTION_START,
            TestSteinlibParser.SECTION_END,
            TestSteinlibParser.EOF,
        )
        self._assert_complete_successfully(
            lines, steiner_instance=steiner_instance)

    def _assert_complete_successfully(self, lines, steiner_instance=None):
        steiner_instance = steiner_instance or SteinlibInstance()
        sut = SteinlibParser(lines, steiner_instance)
        _ = sut.parse()
        self.assertEqual(sut._state, ParsingState.end,
                         'State should be "end". Expecting %s but is %s' %
                         (ParsingState.end, sut._state))
        return sut


class TestSteinerInstance(unittest.TestCase):

    class SteinlibInstanceWithSomeCallbacks(SteinlibInstance):

        def __init__(self):
            # this is the attribute
            self.context = ''

        def header(self, raw_line, tokens):
            self.context += 'H'

        def section(self, raw_line, tokens):
            self.context += 'S'

        def eof(self, raw_line, tokens):
            self.context += 'E'

    def test_instance_callbacks(self):
        st = TestSteinerInstance.SteinlibInstanceWithSomeCallbacks()
        lines = (
            TestSteinlibParser.HEADER,  # <-- will call header 'H'
            TestSteinlibParser.SECTION_START,  # <-- will call section 'S'
            TestSteinlibParser.SECTION_END,  # <-- here just for coherence
            TestSteinlibParser.EOF,  # <-- will call eof 'E'
        )
        sut = SteinlibParser(lines, st)
        sut.parse()

        self.assertEqual(
            st.context,
            'HSE',
            'Callbacks not called in the expected order HSE: %s' % st.context)
