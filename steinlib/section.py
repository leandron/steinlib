import re

from steinlib.exceptions import SteinlibParsingException
from steinlib.state import ParsingState


class SectionParser(object):
    """
    Superclass for all the sections parsing.
    """
    DEFAULT_SECTION_END = {'regex': r"^END$",
                           'next_state': ParsingState.wait_for_section}

    @classmethod
    def section_start(cls, line):
        return ParsingState.inside_section

    @classmethod
    def _convert_int_digits_when_possible(cls, tokens):
        '''
        Cast numbers to provide better callback arguments with actual numbers
        and not string representations.
        '''
        converted_tokens = []
        for t in tokens:
            converted_tokens.append(int(t) if t.isdigit() else t)

        return converted_tokens

    @classmethod
    def _get_regex_for_token(cls, token, meta, line):
        '''
        Provide a hook to collect the regex. Important because sections can
        override it and have custom implementations to create dynamic regex.

        See a custom implementation in CoordinatesSectionParser.
        '''
        return meta['regex']

    @classmethod
    def _get_parsed_tokens(cls, line):
        matching_name = None
        extracted_tokens = None
        next_state = ParsingState.inside_section
        known_tokens = cls._get_known_tokens()

        for name, meta in known_tokens.items():
            token_regex = cls._get_regex_for_token(name, meta, line)
            matches = re.search(token_regex, line, re.IGNORECASE)
            if matches:
                matching_name = name
                extracted_tokens = matches.groups()
                next_state = meta.get('next_state',
                                      ParsingState.inside_section)

        return matching_name, extracted_tokens, next_state

    @classmethod
    def parse_token(cls, line, steiner_instance):
        name, tokens, next_state = cls._get_parsed_tokens(line)

        if name:
            method_name = "%s__%s" % (cls.callback_token, name)
            converted_tokens = cls._convert_int_digits_when_possible(tokens)
            callback = getattr(steiner_instance, method_name)
            callback(line, converted_tokens)
        else:
            raise SteinlibParsingException(
                "Error parsing the following line: %s" % line)

        return next_state


class CommentSectionParser(SectionParser):
    callback_token = "comment"

    @classmethod
    def _get_known_tokens(cls):
        return {
            "name": {'regex': r"^Name(?:\s+)\"(.+)\"$"},
            "creator": {'regex': r"^Creator(?:\s+)\"(.+)\"$"},
            "remark": {'regex': r"^Remark(?:\s+)\"(.+)\"$"},
            "problem": {'regex': r"^Problem(?:\s+)\"(.+)\"$"},
            "end": SectionParser.DEFAULT_SECTION_END
        }


class CoordinatesSectionParser(SectionParser):
    callback_token = "coordinates"

    @classmethod
    def _get_known_tokens(cls):
        return {
            "dd": {},
            "end": SectionParser.DEFAULT_SECTION_END
        }

    @classmethod
    def _get_regex_for_token(cls, token, meta, line):
        token_regex = meta.get('regex', None)

        if token == "dd":
            token_regex = cls._get_dd_regex(token, meta, line)

        return token_regex

    @classmethod
    def _get_dd_regex(cls, token, meta, line):
        '''
        This function count how many tokens the dd line contain and
        validate as all of them are numbers.
        '''
        token_count = len(line.split()[1:])  # ignore the first "DD"
        token_regex = r'^DD%s$' % (token_count * r'\s+(\d+)')
        return token_regex


class GraphSectionParser(SectionParser):
    callback_token = "graph"

    @classmethod
    def _get_known_tokens(cls):
        return {
            "obstacles": {'regex': r"^Obstacles(?:\s+)(.+)$"},
            "nodes": {'regex': r"^Nodes\s+(\d+)$"},
            "edges": {'regex': r"^Edges\s+(\d+)$"},
            "arcs": {'regex': r"^Arcs\s+(\d+)$"},
            "e": {'regex': r"^E\s+(\d+)\s+(\d+)\s+(\d+)$"},
            "a": {'regex': r"^A\s+(\d+)\s+(\d+)\s+(\d+)$"},
            "end": SectionParser.DEFAULT_SECTION_END,
        }


class MaximumDegreesSectionParser(SectionParser):
    callback_token = "maximum_degrees"

    @classmethod
    def _get_known_tokens(cls):
        return {
            "md": {'regex': r"^MD\s+(\d+)$"},
            "end": SectionParser.DEFAULT_SECTION_END
        }


class PresolveSectionParser(SectionParser):
    callback_token = "presolve"

    @classmethod
    def _get_known_tokens(cls):
        return {
            "fixed": {'regex': r"^FIXED\s+(\d+)$"},
            "lower": {'regex': r"^LOWER\s+(\d+)$"},
            "upper": {'regex': r"^UPPER\s+(\d+)$"},
            "time": {'regex': r"^TIME\s+(\d+)$"},
            "orgnodes": {'regex': r"^ORGNODES\s+(\d+)$"},
            "orgedges": {'regex': r"^ORGEDGES\s+(\d+)$"},
            "ea": {'regex': r"^EA\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$"},
            "ec": {'regex': r"^EC\s+(\d+)\s+(\d+)\s+(\d+)$"},
            "ed": {'regex': r"^ED\s+(\d+)\s+(\d+)\s+(\d+)$"},
            "es": {'regex': r"^ES\s+(\d+)\s+(\d+)$"},
            "end": SectionParser.DEFAULT_SECTION_END
        }


class ObstaclesSectionParser(SectionParser):
    callback_token = "obstacles"

    @classmethod
    def _get_known_tokens(cls):
        return {
            'rr': {'regex': r"^RR\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$"},
            'end': SectionParser.DEFAULT_SECTION_END,
        }


class TerminalsSectionParser(SectionParser):
    callback_token = "terminals"

    @classmethod
    def _get_known_tokens(cls):
        return {
            'terminals': {'regex': r"^Terminals\s+(\d+)$"},
            'rootp': {'regex': r"^RootP\s+(\d+)$"},
            't': {'regex': r"^T\s+(\d+)$"},
            'tp': {'regex': r"^TP\s+(\d+)$"},
            'end': SectionParser.DEFAULT_SECTION_END,
        }
