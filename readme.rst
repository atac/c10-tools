PyChapter10 Tools
=================

These samples use a pure-python library (PyChapter10_).

Included Tools
--------------

* pcap2c10 - Convert a .pcap file into .c10
* stat - Display packet counts and channel information for a .c10 file
* dump - Export data from channels within a .c10 file
* copy - Copy a chapter 10 file optionally filtering on channel id or data type
* reindex - Strip and optionally rebuild index packets for a .c10 file
* timefix - Correct time values in a .c10 file

Dependencies
------------

* Python_ 2.7 or later (also tested with 3.5)
* PyChapter10_

Building and Running
--------------------

If the dependencies are installed you can run each sample from the commandline using python (eg: python stat.py) and commandline help will show you how to use each one.

.. _PyChapter10: https://bitbucket.org/mcferrill/pychapter10
.. _Python: http://python.org
