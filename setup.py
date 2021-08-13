#!/usr/bin/env python

from contextlib import suppress
from glob import glob
from setuptools import setup, Command
import os
import shutil
import subprocess

from c10_tools.version import version


class BaseCommand(Command):
    description = ''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class Build(BaseCommand):
    description = 'compile to native binary executable'

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env['PYTHONOPTIMIZE'] = '1'
        print('Building')
        subprocess.run([
            'pyinstaller', 'c10_tools/c10.py', '-n', 'c10',
            '--exclude-module', 'numpy',
            '--exclude-module', 'matplotlib',
            '--exclude-module', 'tcl',
            '--exclude-module', 'pytz',
            '--exclude-module', 'pandas',
            '--exclude-module', 'tk',
            '--exclude-module', 'bokeh',
        ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env)


class Clean(BaseCommand):
    description = 'cleanup .spec files and build/dist directories'

    CLEAN_FILES = '''
        build dist *.pyc *.tgz *.egg-info __pycache__ dependencies
        htmlcov MANIFEST coverage.xml junit*.xml *.spec src
    '''

    def run(self):
        here = os.path.abspath(os.path.dirname(__file__))
        for path_spec in self.CLEAN_FILES.split():
            abs_paths = glob(os.path.normpath(os.path.join(here, path_spec)))
            for path in abs_paths:
                print('removing %s' % os.path.relpath(path))
                if os.path.isdir(path):
                    shutil.rmtree(path, True)
                else:
                    with suppress(os.error):
                        os.remove(path)


setup(
    name='c10-tools',
    cmdclass={
        'clean': Clean,
        'build_scripts': Build,
    },
    entry_points={
        'console_scripts': [
            'c10=c10_tools.c10:CLI.main',
        ],
    },
    version=version,
    description='Various tools for managing IRIG 106 Chapter 10/11 data',
    author='Micah Ferrill',
    author_email='ferrillm@avtest.com',
    packages=['c10_tools'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/atac/c10-tools',
    python_requires='>=py3.6',
    install_requires=[
        'docopt>=0.6.2',
        'dpkt>=1.9.3',
        'pychapter10>=1.1.9',
        'tqdm>=4.48.2',
        's3fs>=0.5.2',
        'termcolor>=1.1.0',
        'matplotlib>=3.3.4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
