PyChapter10 Tools
=================

These samples use a pure-python library (PyChapter10_).

Included Tools
--------------

* c10-copy - Copy a file optionally filtering on channel id or data type.
* c10-dump - Export packet data a file.
* c10-errcount - Count error flags in 1553 format 1 packets.
* c10-from-pcap - Extract chapter 10 data from a pcap file.
* c10-grep - Search files/directories for specific data markers
* c10-recovery - Attempt to recover viable data from a corrupt file.
* c10-reindex - Strip and optionally rebuild index packets for a file.
* c10-stat - Display packet counts and channel information for a file.
* c10-timefix - Correct time values in a file.
* c10-wrap-pcap - Wrap ethernet data from a pcap file as ethernet packets in a
  chapter 10 file.

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

* Cross platform build process
* Utilize index packets to optimize performance where practical
* Integrate tqdm (progress bar)
* Make sure usage options are consistent
* Expand errcount to read more than 1553 packets
* Recover Python 3 compatibility
* Automated tests (cross platform)
* Update to use new declarative format to generate packets (pending pychapter10
  updates)
