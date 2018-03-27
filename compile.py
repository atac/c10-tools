#!/usr/bin/env python

from glob import glob
import os
import shutil
import sys


filedir = os.path.dirname(os.path.abspath(__file__))


def build():
    os.chdir(filedir)
    for f in glob('src/c10-*.py'):
        os.system('pyinstaller -F %s -p ../pychapter10 -p ../libirig106-python \
--exclude-module matplotlib;' % f)


def clean():
    shutil.rmtree('dist', True)
    shutil.rmtree('build', True)
    for f in glob('*.spec'):
        os.remove(f)

    print('Cleaned build & dist files')


def install():
    for f in glob('dist/*'):
        shutil.copy(f, os.path.join(os.environ.get('HOME'), 'bin'))

    print('Installed to ~/bin')


if __name__ == '__main__':
    command = sys.argv[1:]
    if not command:
        build()
    elif command == ['install']:
        install()
    elif command == ['clean']:
        clean()
