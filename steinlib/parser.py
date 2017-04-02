import argparse
import re

from steinlib.exceptions import SteinlibParsingException, \
                                UnrecognizedSectionException
from steinlib.section import CoordinatesSectionParser, \
                             CommentSectionParser, \
                             GraphSectionParser, \
                             MaximumDegreesSectionParser, \
                             ObstaclesSectionParser, \
                             PresolveSectionParser, \
                             TerminalsSectionParser

from steinlib.state import ParsingState


class RootParser(object):
    '''
    Base parser class for root elements.
    '''

    @classmethod
    def matches(cls, line, steiner_instance):
        '''
        Generic regular expression matching for the root parsers.

        Note: re.IGNORECASE is used due to mixed case observed in
              some benchmarks.
        '''
        assert hasattr(cls, 'token_regex'), '%s must have a token_regex' % cls
        assert hasattr(cls, 'callback_method'), (
            '%s must have a callback_method' % cls)

        matching_groups = re.search(cls.token_regex, line, re.IGNORECASE)

        if matching_groups:
            callback = getattr(steiner_instance, cls.callback_method)
            callback(line, matching_groups.groups())
        else:
            raise SteinlibParsingException('Unexpected line: %s' % line)

        return matching_groups


class RootHeaderParser(RootParser):
    '''
    Parses the STP file header.
    The magic number comparison should be case insensitive.
    '''
    token_regex = r'^33D32945(?:\s+)(.+)$'
    callback_method = 'header'


class RootEofParser(RootParser):
    '''
    Parses the global end of the STP file.
    '''
    token_regex = r'^EOF$'
    callback_method = 'eof'


class RootSectionParser(RootParser):
    '''
    Aggregates the Secion parsers and call the appropriate classes.
    '''
    token_regex = r'^SECTION(?:\s+)(\w+)$'
    callback_method = 'section'
    section_parsers = {
        'Comment': CommentSectionParser,
        'Coordinates': CoordinatesSectionParser,
        'Graph': GraphSectionParser,
        'MaximumDegrees': MaximumDegreesSectionParser,
        'Obstacles': ObstaclesSectionParser,
        'Presolve': PresolveSectionParser,
        'Terminals': TerminalsSectionParser,
    }

    @classmethod
    def get_section_parser(cls, line, steiner_instance):
        '''
        Provide the specific class that will parse the inner tokens for the
        supported sections.

        Also, call the appropriate callbacks for sections.
        '''
        section_matches = cls.matches(line, steiner_instance)
        section_name = section_matches.groups()[0]
        section_parser = cls.section_parsers.get(section_name)

        if section_parser:
            callback = getattr(steiner_instance, section_name.lower())
            callback(line, section_matches.groups())
        else:
            all_known_section_names = ', '.join(cls.section_parsers.keys())
            raise UnrecognizedSectionException(
                'Invalid section identifier "%s". Known sections: %s.' %
                (section_name, all_known_section_names))

        return section_parser


class SteinlibParser(object):
    '''
    Parser for the SteinLib format.
    '''
    comment_symbol = '#'

    def __init__(self, lines, steiner_instance):
        self._lines = lines
        self._state = ParsingState.wait_for_header
        self._steiner_instance = steiner_instance

    def parse(self):
        '''
        Main parsing loop.
        '''
        section_class = None

        for raw_line in self._lines:
            line = self._cleanup_line(raw_line)

            if not line or self._is_comment(line):
                continue

            if self._state == ParsingState.wait_for_header:
                _ = RootHeaderParser.matches(line, self._steiner_instance)
                self._state = ParsingState.wait_for_section

            elif self._state == ParsingState.wait_for_section:
                try:
                    section_class = RootSectionParser.get_section_parser(
                                        line, self._steiner_instance)
                    self._state = section_class.section_start(line)

                except UnrecognizedSectionException as ex:
                    raise ex  # pragma: no cover

                except SteinlibParsingException as ex:
                    if RootEofParser.matches(line, self._steiner_instance):
                        self._state = ParsingState.end

            elif self._state == ParsingState.inside_section:
                self._state = section_class.parse_token(
                                line, self._steiner_instance)

            elif self._state == ParsingState.end:
                # See test.test_parser.test_unexpected_eof()
                raise SteinlibParsingException('Unexpected "EOF".')

        if self._state != ParsingState.end:
            raise SteinlibParsingException('Illegal state.')

        return self._steiner_instance

    def _cleanup_line(self, line):
        '''
        Removes trailing spaces do sanitize lines.
        '''
        return line.strip()

    def _is_comment(self, line):
        '''
        Check if a given line is a comment.
        '''
        return line.startswith(self.comment_symbol)
