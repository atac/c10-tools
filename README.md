
# C10 Tools

[![Build Status](https://img.shields.io/azure-devops/build/atac-bham/ee9fec36-25b3-4698-9fc2-f77a58ad9ecb/8)](https://dev.azure.com/atac-bham/c10-tools/_build/latest?definitionId=8&branchName=master)
![PyPI - License](https://img.shields.io/github/license/atac/c10-tools)
[![PyPI](https://img.shields.io/pypi/v/c10-tools)](https://pypi.org/project/c10-tools/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/c10-tools)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/mcferrill/c10-tools)](https://hub.docker.com/repository/docker/mcferrill/c10-tools/builds)

Commandline toolkit for inspecting and troubleshooting IRIG 106 Chapter 10/11 data with 
[pychapter10](https://github.com/atac/pychapter10).


## Usage

Get top-level usage and list of commands with:

```
c10 help
```

Get specific usage for each command with

```
c10-stat help <command>
```

See issue #8 for details on new command layout for 1.0

## Installation

Install the latest version with pip:

```
pip install c10-tools
```

To install offline from the "full" zip, install the included dependencies and the library with:

```
pip install dependencies/* .
```

## Running Tests

To run the included tests install dependencies with pip (also included in full zip, see above):

```
pip install -r requirements.txt
```

Then run:

```
pytest
```

## Building Native Binaries

If the dependencies are installed you can compile a native executable with:

```
python setup.py build_scripts
```
