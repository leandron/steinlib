Welcome to Steinlib parser documentation!
#########################################

This module provides a Python parser to STP, the `SteinLib Testdata Library
<http://steinlib.zib.de/steinlib.php>`_ file format.

The SteinLib Testdata consists of hundreds of `Steiner tree problem
<https://en.wikipedia.org/wiki/Steiner_tree_problem>`_ instances. Using this
module allows you to write your own Python code to handle STP format parsed
and validated structures.

There is complete documentation about the format itself on the official
steinlib website.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installing
==========

It is easy to obtain the latest released version via ``pip``::

    pip install steinlib

Basic Usage
============

In order to use the parsed structures, two main components are required:

 - A *parser*, that will be responsible for parsing the structure, and;
 - A *instance*, where the parser will invoke callbacks when known structures are found

So, let's see an example about how it works.

Starting with an STP file available on Steinlib official website:

 .. literalinclude:: ../../examples/hello.stp
    :linenos:

It is possible to observe this file contains three main components:

 - a **header line**;
 - a set of delimited **sections** and;
 - the **end of file** marker.

This *parser* will identify all these small pieces of the STP file and use it to
trigger functions on your *instance*. This is the key concept used to create
this module.

The script below provides some initial examples about how these ``callback`` methods
works:

 .. literalinclude:: ../../examples/hello_steinlib.py
    :linenos:

For each identified structure, the appropriate method will be called in the *instance*
object, with the standard parameters:

 - ``raw_args`` is the actual full line from the input stream
 - ``list_args`` contains the extracted and converted parameters from the current line

