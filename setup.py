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
        for f in glob('*.spec') + glob('junit*.xml'):
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
            'c10-stat=c10_tools.c10_stat:main',
        ],
    },
    version='0.1',
    description='Various tools for managing IRIG 106 Chapter 10/11 data',
    author='Micah Ferrill',
    packages=['c10_tools'],
)
