
class SteinlibParsingException(Exception):
    """
    This is the generic exception for the overall parsing process. If there is
    something wrong, this will be raised.
    """
    pass


class UnrecognizedSectionException(SteinlibParsingException):
    """
    This exception is raised when a unknown section name is found.
    """
    pass
