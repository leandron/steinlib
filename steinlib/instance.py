class SteinlibInstance(object):
    '''
    This is the base class that do basic hadling of attribute magic method_name
    to handle the calls from the parser.
    '''

    def __init__(self):
        pass

    def __getattribute__(self, name):
        try:
            attr = object.__getattribute__(self, name)
            if hasattr(attr, '__call__'):
                def newfunc(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    return result
                return newfunc
            else:
                return attr
        except AttributeError:
            def do_nothing(*args, **kwargs):
                pass
            return do_nothing
