Introduction
============

This project aims to convert the xml datastore of GnuCash into OFX. This is
useful for anybody migrating from gnucash to another system that supports
OFX.

Setup
=====
This project relies on [gnucashxml][] for parsing. It is imported as a submodule.
make sure you create the file `__init__.py` manually in the gnucashxml folder
otherwise it won't be loadable as a module.

[gnucashxml]: https://github.com/jorgenschaefer/gnucashxml/

OFX Format
==========
This script uses the version 2 format of the ofx header. The main difference
is the xml header and can be easily tweaked to comply with older format versions.

Usage
=====
Type the following where <file> is your gnuCash file and optional [dir]
is the output directory of all the OFX files. One OFX file is produced
per account on GnuCash. *Make sure* that your gnucash file is gzipped.

'''
./convert.py <file> [dir]
'''

Todo
====
Import account codes along with name and type.

Import the start and end date of all transactions (for now its blank).
