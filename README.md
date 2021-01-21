
# C10 Tools

[![Build Status](https://img.shields.io/azure-devops/build/atac-bham/ee9fec36-25b3-4698-9fc2-f77a58ad9ecb/8)](https://dev.azure.com/atac-bham/c10-tools/_build/latest?definitionId=8&branchName=master)
![PyPI - License](https://img.shields.io/github/license/atac/c10-tools)
[![PyPI](https://img.shields.io/pypi/v/c10-tools)](https://pypi.org/project/c10-tools/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/c10-tools)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/mcferrill/c10-tools)](https://hub.docker.com/repository/docker/mcferrill/c10-tools/builds)

Various utilities for analyzing and manipulating Irig 106 Chapter 10 data using
[libirig106-python](https://github.com/atac/libirig106-python) and
[pychapter10](https://github.com/atac/pychapter10).


## Included Tools

Each tool is self-documenting with the --help flag as in:

```
c10-stat --help
```

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

## Installation

Install the latest version with pip:

```
pip install c10-tools
```

To install offline from the "full" zip, install the included dependencies and the library with:

```
pip install dependencies/* .
```

## Choosing Parser Library

By default everything will run with pychapter10.
You can improve the performance of pychapter10 by installing cbitstruct `pip install cbitstruct`.
You can also install libirig106-python to use the libirig106 wrapper instead of the python library.
To manually select between backends when both are installed, set the LIBRARY environment variable to c10 or i106 as in (for unix):

```
LIBRARY=i106 c10-stat test.ch10
```

## Running Tests

To run the included sanity tests install dependencies with pip (also included in full zip, see above):

```
pip install -r requirements.txt
```

Then run:

```
pytest test
```

## Building Native Binaries

If the dependencies are installed (see Running Tests) you can compile native executables of the tools with:

```
python setup.py build_scripts
```
