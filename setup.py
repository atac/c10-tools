#!/usr/bin/env python

from distutils import cmd
from distutils.core import setup
from glob import glob
import shutil
import os


class Command(cmd.Command):
    description = ''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class Install(Command):
    description = 'copy tools from dist to ~/bin'

    def run(self):
        for f in glob('dist/*'):
            shutil.copy(f, os.path.join(os.environ.get('HOME'), 'bin'))

        print('Installed to ~/bin')


class Build(Command):
    description = 'compile tools to standalone binaries'

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        for f in glob('src/c10_*.py') + glob('src/c10-*.py'):
            os.system('pyinstaller -F %s -p . -p src \
--exclude-module matplotlib;' % f)
            if 'c10_' in f:
                name, ext = os.path.splitext('dist/' + os.path.basename(f))
                try:
                    os.rename(name, '-'.join(name.rsplit('_', 1)))
                except FileNotFoundError:
                    name += '.exe'
                    os.rename(name, '-'.join(name.rsplit('_', 1)))


class Link(Command):
    description = 'symlink scripts to /usr/bin'

    def run(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        for f in glob('src/c10_*.py') + glob('src/c10-*.py'):
            f = os.path.abspath(f)
            link = os.path.basename(os.path.splitext(f)[0].replace('_', '-'))
            os.system('ln -s %s /usr/bin/%s' % (f, link))


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
        'build': Build,
        'link': Link,
        'install_scripts': Install,
    },
    version='0.1',
    description='A collection of basic tools for managing Irig106 Chapter \
10/11 data',

    # Not supported in 3.7?
    # setup_requires=['pytest-runner'],
    # tests_requires=['pytest'],

    author='Micah Ferrill',
    packages=['src'],
)
