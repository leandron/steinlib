class ParsingState(object):
    """
    States of the parsing process.
    """
    wait_for_header = 0
    wait_for_section = 1
    inside_section = 2
    end = 4
