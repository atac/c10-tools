#!/usr/bin/env python

from distutils import cmd
from distutils.core import setup
from glob import glob
import os
import shutil
import subprocess


class Command(cmd.Command):
    description = ''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class Build(Command):
    description = 'compile tools to standalone binaries'

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        for f in glob('c10_tools/c10_*.py'):
            print(f'Building {f}')
            name, _ = os.path.splitext(os.path.basename(f))
            subprocess.run([
                'pyinstaller', '-F', f, '-n', name.replace('_', '-')],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class Clean(Command):
    description = 'cleanup .spec files and build/dist directories'

    def run(self):
        shutil.rmtree('dist', True)
        shutil.rmtree('build', True)
        shutil.rmtree('htmlcov', True)
        for f in glob('*.spec') + glob('junit*.xml') + ['coverage.xml']:
            os.remove(f)

        print('cleaned build & dist files')


setup(
    name='c10-tools',
    cmdclass={
        'clean': Clean,
        'build_scripts': Build,
    },
    entry_points={
        'console_scripts': [
            'c10-allbus=c10_tools.c10_allbus:main',
            'c10-copy=c10_tools.c10_copy:main',
            'c10-dmp1553=c10_tools.c10_dmp1553:main',
            'c10-dump=c10_tools.c10_dump:main',
            'c10-dump-pcap=c10_tools.c10_dump_pcap:main',
            'c10-errcount=c10_tools.c10_errcount:main',
            'c10-events=c10_tools.c10_events:main',
            'c10-from-pcap=c10_tools.c10_from_pcap:main',
            'c10-grep=c10_tools.c10_grep:main',
            'c10-reindex=c10_tools.c10_reindex:main',
            'c10-stat=c10_tools.c10_stat:main',
            'c10-timefix=c10_tools.c10_timefix:main',
            'c10-validator=c10_tools.c10_validator:main',
            'c10-wrap-pcap=c10_tools.c10_wrap_pcap:main',
        ],
    },
    version='0.1',
    description='Various tools for managing IRIG 106 Chapter 10/11 data',
    author='Micah Ferrill',
    packages=['c10_tools'],
)
