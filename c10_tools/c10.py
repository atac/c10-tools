
from os.path import basename
import sys
import types

from docopt import docopt
from termcolor import colored

from c10_tools.allbus import main as allbus
from c10_tools.capture import main as capture
from c10_tools.copy import main as copy
from c10_tools.dump import main as dump
from c10_tools.find import main as find
from c10_tools.from_pcap import main as frompcap
from c10_tools.inspect import main as inspect
from c10_tools.reindex import main as reindex
from c10_tools.stat import main as stat
from c10_tools.timefix import main as timefix
from c10_tools.version import version
try:
    import matplotlib
    from c10_tools.streamcheck import main as streamcheck
except ImportError:
    streamcheck = None


def help(args):
    """Show general usage or help for a command.
    help [<command>] [options]

    Running with no arguments prints general help while specifying a command
    will give a detailed explanation of the relevant options and behaviors.
    """

    if args['<command>'] in CLI.COMMANDS:
        return CLI.build_usage(CLI.COMMANDS[args['<command>']].__doc__)
    elif args['<command>'] is None:
        return CLI.general_usage()
    else:
        return '%s not understood' % args['<command>']


class CLI:
    GLOBAL_USAGE = colored('Usage:', 'yellow') + \
        '\n    %s <command> [<args>] [options]' % basename(sys.argv[0])
    GLOBAL_OPTIONS = [
        '-v, --verbose  Verbose output.',
        '-q, --quiet  Minimal output.',
        '-h, --help  ' + help.__doc__.split('\n')[0]]
    COMMANDS = {
        'allbus': allbus,
        'capture': capture,
        'copy': copy,
        'dump': dump,
        'find': find,
        'frompcap': frompcap,
        'help': help,
        'inspect': inspect,
        'reindex': reindex,
        'stat': stat,
        'timefix': timefix,
    }
    if streamcheck:
        COMMANDS['streamcheck'] = streamcheck

    @classmethod
    def build_usage(cls, s=''):
        """Format a usage string for docopt. s should be a sub-command usage with:
        One-line description
        <usage and opts>

        [optional long description]
        """

        # Reformat description if present (4 spaces indent assumed).
        description = ''
        if s.count('\n\n') > 0:
            s, description = s.split('\n\n', 1)
            description = '\n'.join(
                line[4:] for line in description.splitlines())

        # Separate out usage and options.
        usage, options = '', cls.GLOBAL_OPTIONS
        for i, line in enumerate(s.splitlines()):
            line = line.strip()
            if i == 0:
                usage += line + '\n\n' + colored('Usage:', 'yellow')
            elif line.startswith('-'):
                options.append(line)
            elif line:
                usage += '\n    {} {}'.format(basename(sys.argv[0]), line)

        return ('\n\n'.join((
            usage,
            cls.format_options(options),
            description,
        ))).strip()

    @classmethod
    def general_usage(cls):
        """Top-level usage shown with 'help' command."""

        # Spacing based on option size.
        width = max(len(opt.split('  ')[0]) for opt in cls.GLOBAL_OPTIONS) + 2

        commands = colored('Commands:', 'yellow')
        for name, func in sorted(cls.COMMANDS.items()):
            help = func.__doc__.splitlines()[0].strip()
            commands += f'\n    {name:{width}}{help}'

        # Output options.
        return ('\n\n'.join((
            cls.GLOBAL_USAGE,
            commands,
            cls.format_options(cls.GLOBAL_OPTIONS),
        ))).strip()

    @classmethod
    def format_options(cls, options):
        """Takes a list of strings and returns a formatted string suitable for
        options usage.
        """

        width = max(len(opt.split('  ')[0]) for opt in options) + 2
        output = f"{colored('Options:', 'yellow')}\n"
        for opt in options:
            opt, help = opt.split('  ', 1), ''
            if isinstance(opt, list) and len(opt) == 2:
                opt, help = opt
            output += f'    {opt:{width}}{help}\n'
        return output

    @classmethod
    def main(cls, args=sys.argv[1:]):
        """Find and run the appropriate command."""

        # Reroute anything with a help flag to the help command.
        if '-h' in args or '--help' in args:
            args = [a for a in args if a not in ('-h', '--help')]
            args.insert(0, 'help')

        usage, command = cls.GLOBAL_USAGE, args and args[0] or None

        # Show general usage if appropriate.
        if '--version' not in args and command not in cls.COMMANDS:
            print(usage)
            return

        # Get usage for specific commands.
        if command != '--version':
            func = cls.COMMANDS[command]
            usage = cls.build_usage(func.__doc__)

        # Parse with docopt (also handles version and help requests).
        args = docopt(usage, args, False, version)

        # Execute command and print any response.
        result = func(args)
        if isinstance(result, types.GeneratorType):
            for line in result:
                print(line)
        elif result:
            print(result)


if __name__ == '__main__':
    CLI.main()