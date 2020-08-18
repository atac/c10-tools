
# C10 Tools

[![Build Status](https://img.shields.io/azure-devops/build/atac-bham/ee9fec36-25b3-4698-9fc2-f77a58ad9ecb/8)](https://dev.azure.com/atac-bham/c10-tools/_build/latest?definitionId=8&branchName=master)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/mcferrill/c10-tools)](https://hub.docker.com/repository/docker/mcferrill/c10-tools/builds)

Various utilities for analyzing and manipulating Irig 106 Chapter 10 data using
[libirig106-python](https://github.com/atac/libirig106-python) and
[pychapter10](https://github.com/atac/pychapter10).


## Included Tools

* c10-allbus - Switch 1553 format 1 messages to indicate the same bus.
* c10-copy - Copy a file optionally filtering on channel id or data type.
* c10-dmp1553 - Print a hex dump of word n for every 1553 message found.
* c10-dump - Export packet data to file.
* c10-dump-pcap - Export Ethernet data from a Chapter 10 file to pcap.
* c10-errcount - Count error flags in 1553 format 1 packets.
* c10-events - Print recording event packet info.
* c10-from-pcap - Extract chapter 10 data from a pcap file.
* c10-grep - Search files/directories for specific data markers
* c10-reindex - Strip and optionally rebuild index packets for a file.
* c10-stat - Display packet counts and channel information for a file.
* c10-timefix - Correct time values in a file.
* c10-validator - Attempt to recover viable data from a corrupt file.
* c10-wrap-pcap - Wrap ethernet data from a pcap file as ethernet packets in a
  chapter 10 file.
* wireshark_dissector - Lua based wireshark dissector for Chapter 10 data


## Dependencies

* [Python](https://python.org) 3.6 or later

## Building and Running

If the dependencies are installed (pip install -r requirements) you can run
each sample from the commandline using python (eg: python c10-stat.py) and
commandline help will show you how to use each one.

You can use the setup script to compile and install to native binaries if
needed.
