PNTools
=======

PNTools is a collection of small Python 3 scripts. These
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

* lpo_viewer_tk.py:
This module implements a GUI for viewing labeled partial 
orders. This GUI is build with Tkinter.

* petrinet_viewer_tk.py:
This module implements a GUI for viewing Petri nets. This GUI
is build with Tkinter.

* lpo_viewer.py:
This module implements a GUI for viewing labeled partial
orders. This GUI uses PyQt5!

(partial) Requirements:
-----------------------

Some of the user interfaces are build with PyQt5, therefore 
you need to install Qt5 and PyQt5 if you want to use these GUIs.
