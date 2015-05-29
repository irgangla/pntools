PNTools
=======

PNTools is a collection of small Python 3 scripts. This
scripts support parsing of pnml and lpo files, define a
data structure for Petri nets and labelled partial orders
and contain algorithms to work with such structures.

Modules:
--------

* partialorder.py:

This module implements classes for labelled partial orders
and a parser for .lpo-files created with VipTool or MoPeBs
(http://www.fernuni-hagen.de/sttp/forschung/mopebs.shtml)

* petrinet.py:
This module implements classes for Petri nets and a parser
for .pnml-files. (http://www.pnml.org/)

* lpo_viewer.py:
This module implements a GUI for viewing labeled partial
orders. This GUI uses PyQt5!

(partial) Requirements:
-----------------------

The GUIs are build with PyQt5, therefore you need to install
Qt5 and PyQt5 if you want to use this GUIs. A nice tutorial 
for installing PyQt5 on Linux is: 

http://robertbasic.com/blog/install-pyqt5-in-python-3-virtual-environment

