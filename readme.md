PyChapter10 Tools
=================

Various utilities for analyzing and manipulating Irig 106 Chapter 10 data.


Included Tools
--------------

* c10-allbus - Switch 1553 format 1 messages to indicate the same bus (A or B).
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
* wireshark_dissector - Lua based wireshark dissector for Chapter 10 data


Dependencies
------------

* [Python](http://python.org) 2.7 or later
* [PyChapter10](https://bitbucket.org/atac-bham/pychapter10)


Building and Running
--------------------

If the dependencies are installed (pip install -r requirements.txt) you can run
each sample from the commandline using python (eg: python c10-stat.py) and
commandline help will show you how to use each one.

The compile.py script can be used to generate native binaries (via PyInstaller)
