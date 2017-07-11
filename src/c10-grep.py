#!/usr/bin/env python

"""usage: c10-grep <value> <path>... [options]

Search Chapter 10 files/directories for "<value>" based on user input.

Options:
    -c CHANNEL, --channel CHANNEL          Channel ID
    --cmd CMDWORD, --command-word CMDWORD  1553 Command word
    -w WORD, --word-offset WORD            Word offset within message
    -m MASK, --mask MASK                   Value mask
"""

import os

from docopt import docopt


def search(path, args):
    pass


if __name__ == '__main__':
    args = docopt(__doc__)

    for path in args.get('<path>'):
        path = os.path.abspath(path)
        basename = os.path.basename(path)
        prefix = path[:-len(basename)]
        print 'Searching %s...' % path
        if os.path.isdir(path):
            for dirname, dirnames, filenames in os.walk(path):
                for f in filenames:
                    if f.lower().endswith('.c10') or f.lower().endswith(
                            '.ch10'):
                        f = os.path.join(dirname, f)
                        print '    %s...' % f[len(path) + 1:]
                        search(f, args)
        else:
            search(path, args)
