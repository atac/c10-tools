PyChapter10 Tools
=================

These samples use a pure-python library (PyChapter10_).

Included Tools
--------------

* pcap2c10 - Convert a .pcap file into .c10
* c10-stat - Display packet counts and channel information for a .c10 file
* c10-dump - Export data from channels within a .c10 file
* c10-copy - Copy a chapter 10 file optionally filtering on channel id or data type
* c10-reindex - Strip and optionally rebuild index packets for a .c10 file
* c10-timefix - Correct time values in a .c10 file

Dependencies
------------

* Python_ 2.7 or later
* PyChapter10_

Building and Running
--------------------

If the dependencies are installed you can run each sample from the commandline
using python (eg: python stat.py) and commandline help will show you how to use
each one.

.. _PyChapter10: https://bitbucket.org/pychapter10/pychapter10
.. _Python: http://python.org

To Do
-----

* Suppress scapy warnings on import in pcap2c10
* Verbosity settings for compile script
