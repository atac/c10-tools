
# C10 Tools

[![Build Status](https://img.shields.io/azure-devops/build/atac-bham/ee9fec36-25b3-4698-9fc2-f77a58ad9ecb/8)](https://dev.azure.com/atac-bham/c10-tools/_build/latest?definitionId=8&branchName=master)
![PyPI - License](https://img.shields.io/github/license/atac/c10-tools)
[![PyPI](https://img.shields.io/pypi/v/c10-tools)](https://pypi.org/project/c10-tools/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/c10-tools)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/mcferrill/c10-tools)](https://hub.docker.com/repository/docker/mcferrill/c10-tools/builds)

Commandline toolkit for inspecting and troubleshooting IRIG 106 Chapter 10/11 data with
[pychapter10](https://github.com/atac/pychapter10).


## Usage

```
Usage:
    c10 <command> [<args>] [options]

Commands:
    allbus         Switch 1553 format 1 messages to indicate the same bus (a or b).
    capture        Capture chapter 10 data from a pcap file.
    copy           Copy a Chapter 10 file. Can selectively copy by channel, type, byte offset, or time.
    dump           Dump hex (default), binary data, or PCAP from a Chapter 10 channel.
    find           Search for a given value in Chapter 10 files.
    frompcap       Wrap network data in a pcap file as Chapter 10 Message format.
    help           Show general usage or help for a command.
    inspect        Report on packets found in a file.
    reindex        Remove or recreate index packets for a file.
    stat           Inspect one or more Chapter 10 files and get channel info.
    streamcheck    Plot data density of a channel in a Chapter 10 stream. Requires matplotlib.
    timefix        Ensure that time packets are at 1-second intervals.

Options:
    -v, --verbose  Verbose output.
    -q, --quiet    Minimal output.
    -h, --help     Show general usage or help for a command.
```

Get top-level usage and list of commands with:

```
c10 help
```

Get specific usage for each command with

```
c10 help <command>
```

## Installation

Install the latest version with pip (or [pipx](https://pypa.github.io/pipx/)):

```
pip install c10-tools
```

To install offline from the "full" zip, install the included dependencies and the library with:

```
pip install dependencies/* . --no-index --no-deps
```

## Running Locally

To use locally install [pdm](https://pdm.fming.dev/) and install dependencies with:

```
pdm install
```

Then to run the test suite run:

```
pytest
```
