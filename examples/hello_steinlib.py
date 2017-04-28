#!/usr/bin/env python
# -*- coding: utf-8 -*-
from steinlib.instance import SteinlibInstance
from steinlib.parser import SteinlibParser

import sys


class MySteinlibInstance(SteinlibInstance):
    """
    This is my first steinlib parser!
    """

    def comment(self, raw_args, list_args):
        print "Comment section found"

    def comment__end(self, raw_args, list_args):
        print "Comment section end"

    def coordinates(self, raw_args, list_args):
        print "Coordinates section found"

    def eof(self, raw_args, list_args):
        print "End of file found"

    def graph(self, raw_args, list_args):
        print "Graph section found"

    def header(self, raw_args, list_args):
        print "Header found"

    def terminals(self, raw_args, list_args):
        print "Terminals section found"


if __name__ == "__main__":
    my_class = MySteinlibInstance()
    with open(sys.argv[1]) as my_file:
        my_parser = SteinlibParser(my_file, my_class)
        my_parser.parse()

