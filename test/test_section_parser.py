import unittest

from mock import MagicMock

from steinlib.exceptions import SteinlibParsingException, \
                                UnrecognizedSectionException
from steinlib.instance import SteinlibInstance
from steinlib.parser import RootSectionParser
from steinlib.section import CommentSectionParser
from steinlib.state import ParsingState


class TestRootSectionParser(unittest.TestCase):
    graph = SteinlibInstance()

    def test_simple_section_match(self):
        simple_section = 'SECTION Foo'
        result = RootSectionParser.matches(simple_section,
                                           TestRootSectionParser.graph)
        self.assertEqual(len(result.groups()), 1,
                         'RootSectionParser.matches should return 1 name')

    def test_mixed_case_section_match(self):
        simple_section = 'sEcTiOn Foo'
        result = RootSectionParser.matches(simple_section,
                                           TestRootSectionParser.graph)
        self.assertEqual(len(result.groups()), 1,
                         'RootSectionParser.matches should return 1 name')

    def test_section_name_is_correct(self):
        simple_section = 'SECTION Foobar'
        result = RootSectionParser.matches(simple_section,
                                           TestRootSectionParser.graph)
        self.assertEqual(result.groups()[0], 'Foobar')

    def test_invalid_empty_section_raises_exception(self):
        simple_section = 'SECTION'
        with self.assertRaises(SteinlibParsingException):
            result = RootSectionParser.matches(
                        simple_section, TestRootSectionParser.graph)

    def test_invalid_multiple_section_names_raises_exception(self):
        simple_section = 'section Foo Bar'
        with self.assertRaises(SteinlibParsingException):
            result = RootSectionParser.matches(
                        simple_section, TestRootSectionParser.graph)

    def test_invalid_section_string_raises_exception(self):
        simple_section = 'chapter Foo'
        with self.assertRaises(SteinlibParsingException):
            result = RootSectionParser.matches(
                        simple_section, TestRootSectionParser.graph)

    def test_right_section_parser_is_returned(self):
        comment_section = 'section Comment'
        section_parser = RootSectionParser.get_section_parser(
                            comment_section, TestRootSectionParser.graph)
        self.assertEqual(section_parser, CommentSectionParser)

    def test_right_section_callback_is_executed(self):
        mock_graph = MagicMock()
        comment_section = 'section Comment'
        section_parser = RootSectionParser.get_section_parser(
                            comment_section, mock_graph)
        # generic callback for all sections
        mock_graph.section.assert_called_with('section Comment', ('Comment',))
        # specific callback, called only when 'comment' section is found
        mock_graph.comment.assert_called_with('section Comment', ('Comment',))

    def test_right_section_parser_is_returned(self):
        comment_section = 'section Bogus'
        with self.assertRaises(UnrecognizedSectionException):
            section_parser = RootSectionParser.get_section_parser(
                                comment_section,
                                TestRootSectionParser.graph)

    def test_capture_exception_unrecognized_section(self):
        comment_section = 'section Bogus'
        try:
            section_parser = RootSectionParser.get_section_parser(
                                comment_section,
                                TestRootSectionParser.graph)
        except UnrecognizedSectionException as ex:
            message_snippet = 'Invalid section identifier'
            self.assertTrue(
                message_snippet in str(ex),
                '"%s" should appear in the exception message: %s' % (
                    message_snippet, str(ex)))


class TestCommentSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Comment', self._mock_graph)

    def test_invalid_line_for_comment_section(self):
        invalid_line = 'FOO 1 2 3'
        with self.assertRaises(SteinlibParsingException):
            next_state = self._sut.parse_token(invalid_line, self._mock_graph)

    def test_default_next_status_is_returned(self):
        name = 'Name "Foo bar"'
        next_state = self._sut.parse_token(name, self._mock_graph)
        self.assertEqual(
            ParsingState.inside_section,
            next_state,
            'Default next state should be inside_section %s, but got %s.' % (
                ParsingState.inside_section, next_state))

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_single_string_regex_rejects_invalid(self):
        invalid_line = 'Remark "Foo bar" MORE STUFF'
        with self.assertRaises(SteinlibParsingException):
            next_state = self._sut.parse_token(invalid_line, self._mock_graph)

    def test_name_callback(self):
        name = 'Name "Foo bar"'
        next_state = self._sut.parse_token(name, self._mock_graph)
        self._mock_graph.comment__name.assert_called_with(name, ['Foo bar'])

    def test_creator_callback(self):
        creator = 'Creator "Foo bar"'
        next_state = self._sut.parse_token(creator, self._mock_graph)
        self._mock_graph.comment__creator.assert_called_with(
            creator, ['Foo bar'])

    def test_remark_callback(self):
        remark = 'Remark "Foo bar"'
        next_state = self._sut.parse_token(remark, self._mock_graph)
        self._mock_graph.comment__remark.assert_called_with(
            remark, ['Foo bar'])

    def test_problem_callback(self):
        problem = 'Problem "Foo bar"'
        next_state = self._sut.parse_token(problem, self._mock_graph)
        self._mock_graph.comment__problem.assert_called_with(
            problem, ['Foo bar'])


class TestCoordinatesSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Coordinates', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_dd_callback_two_params(self):
        dd = 'DD 222 333'
        next_state = self._sut.parse_token(dd, self._mock_graph)
        self._mock_graph.coordinates__dd.assert_called_with(
            dd, [222, 333])

    def test_dd_callback_three_params(self):
        dd = 'DD 777 888 999'
        next_state = self._sut.parse_token(dd, self._mock_graph)
        self._mock_graph.coordinates__dd.assert_called_with(
            dd, [777, 888, 999])

    def test_dd_callback_four_params(self):
        dd = 'DD 777 888 999 222'
        next_state = self._sut.parse_token(dd, self._mock_graph)
        self._mock_graph.coordinates__dd.assert_called_with(
            dd, [777, 888, 999, 222])

    def test_dd_callback_reject_unexpected_parameters(self):
        dd = 'DD 777 abc 999 222'
        with self.assertRaises(SteinlibParsingException):
            next_state = self._sut.parse_token(dd, self._mock_graph)


class TestGraphSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Graph', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_obstacles_callback(self):
        obstacles = 'Obstacles 555'
        next_state = self._sut.parse_token(obstacles, self._mock_graph)
        self._mock_graph.graph__obstacles.assert_called_with(
            obstacles, [555])

    def test_nodes_callback(self):
        nodes = 'Nodes 777'
        next_state = self._sut.parse_token(nodes, self._mock_graph)
        self._mock_graph.graph__nodes.assert_called_with(nodes, [777])

    def test_edges_callback(self):
        edges = 'Edges 234'
        next_state = self._sut.parse_token(edges, self._mock_graph)
        self._mock_graph.graph__edges.assert_called_with(edges, [234])

    def test_arcs_callback(self):
        arcs = 'Arcs 321'
        next_state = self._sut.parse_token(arcs, self._mock_graph)
        self._mock_graph.graph__arcs.assert_called_with(arcs, [321])

    def test_e_callback(self):
        e = 'e 234 789 123'
        next_state = self._sut.parse_token(e, self._mock_graph)
        self._mock_graph.graph__e.assert_called_with(e, [234, 789, 123])

    def test_a_callback(self):
        a = 'a 234 654 321'
        next_state = self._sut.parse_token(a, self._mock_graph)
        self._mock_graph.graph__a.assert_called_with(a, [234, 654, 321])


class TestMaximumDegreesSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION MaximumDegrees', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_md_callback(self):
        md = 'md 555'
        next_state = self._sut.parse_token(md, self._mock_graph)
        self._mock_graph.maximum_degrees__md.assert_called_with(md, [555])


class TestPresolveSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Presolve', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_fixed_callback(self):
        fixed = 'fixed 555'
        next_state = self._sut.parse_token(fixed, self._mock_graph)
        self._mock_graph.presolve__fixed.assert_called_with(fixed, [555])

    def test_lower_callback(self):
        lower = 'lower 444'
        next_state = self._sut.parse_token(lower, self._mock_graph)
        self._mock_graph.presolve__lower.assert_called_with(lower, [444])

    def test_upper_callback(self):
        upper = 'upper 999'
        next_state = self._sut.parse_token(upper, self._mock_graph)
        self._mock_graph.presolve__upper.assert_called_with(upper, [999])

    def test_time_callback(self):
        _time = 'time 555'
        next_state = self._sut.parse_token(_time, self._mock_graph)
        self._mock_graph.presolve__time.assert_called_with(_time, [555])

    def test_orgnodes_callback(self):
        orgnodes = 'orgnodes 555'
        next_state = self._sut.parse_token(orgnodes, self._mock_graph)
        self._mock_graph.presolve__orgnodes.assert_called_with(orgnodes, [555])

    def test_orgedges_callback(self):
        orgedges = 'orgedges 555'
        next_state = self._sut.parse_token(orgedges, self._mock_graph)
        self._mock_graph.presolve__orgedges.assert_called_with(orgedges, [555])

    def test_ea_callback(self):
        ea = 'ea 111 222 333 444'
        next_state = self._sut.parse_token(ea, self._mock_graph)
        self._mock_graph.presolve__ea.assert_called_with(
            ea, [111, 222, 333, 444])

    def test_ec_callback(self):
        ec = 'ec 555 666 777'
        next_state = self._sut.parse_token(ec, self._mock_graph)
        self._mock_graph.presolve__ec.assert_called_with(ec, [555, 666, 777])

    def test_ed_callback(self):
        ed = 'ed 555 888 999'
        next_state = self._sut.parse_token(ed, self._mock_graph)
        self._mock_graph.presolve__ed.assert_called_with(ed, [555, 888, 999])

    def test_es_callback(self):
        es = 'es 555 666'
        next_state = self._sut.parse_token(es, self._mock_graph)
        self._mock_graph.presolve__es.assert_called_with(es, [555, 666])


class TestObstaclesSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Obstacles', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_rr_callback(self):
        rr = 'rr 555 444 333 222'
        next_state = self._sut.parse_token(rr, self._mock_graph)
        self._mock_graph.obstacles__rr.assert_called_with(
            rr, [555, 444, 333, 222])


class TestTerminalsSectionParser(unittest.TestCase):

    def setUp(self):
        self._mock_graph = MagicMock()
        self._sut = RootSectionParser.get_section_parser(
                        'SECTION Terminals', self._mock_graph)

    def test_end_next_status_is_returned(self):
        end = 'END'
        next_state = self._sut.parse_token(end, self._mock_graph)
        self.assertEqual(
            ParsingState.wait_for_section,
            next_state,
            'Default next state should be  %s, but got %s.' % (
                ParsingState.wait_for_section, next_state))

    def test_terminals_callback(self):
        terminals = 'terminals 444'
        next_state = self._sut.parse_token(terminals, self._mock_graph)
        self._mock_graph.terminals__terminals.assert_called_with(
            terminals, [444])

    def test_rootp_callback(self):
        rootp = 'rootp 555'
        next_state = self._sut.parse_token(rootp, self._mock_graph)
        self._mock_graph.terminals__rootp.assert_called_with(rootp, [555])

    def test_t_callback(self):
        t = 't 333'
        next_state = self._sut.parse_token(t, self._mock_graph)
        self._mock_graph.terminals__t.assert_called_with(t, [333])

    def test_tp_callback(self):
        tp = 'tp 888'
        next_state = self._sut.parse_token(tp, self._mock_graph)
        self._mock_graph.terminals__tp.assert_called_with(tp, [888])
