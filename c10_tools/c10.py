
from os.path import basename
import sys
import types

from docopt import docopt
from termcolor import colored

from c10_tools.allbus import main as allbus
from c10_tools.stat import main as stat
from c10_tools.streamcheck import main as streamcheck
from c10_tools.version import version
from c10_tools.copy import main as copy
from c10_tools.dump import main as dump


def build_usage(s=''):
    """Format a usage string for docopt. s should be a sub-command usage with:
    One-line description
    <usage and opts>

    [optional long description]
    """

    # The elements of our usage string.
    oneline, description = '', ''
    options = GLOBAL_OPTIONS

    # If we have a usage string, combine it with global options.
    if s:

        # Pull the four parts from s.
        s = s.split('\n\n', 1)
        if len(s) == 2:
            s, text = s
        else:
            s = s[0]
        usage = [line.strip() for line in s.splitlines() if line.strip()]
        oneline = usage.pop(0)
        options += [line for line in usage if line.startswith('-')]
        usage = ['    {} {}'.format(basename(sys.argv[0]), line)
                 for line in usage if line not in options]

        # Format the one-line description and usage samples.
        output = '{}\n\n{}\n{}\n'.format(oneline,
                                         colored('Usage:', 'yellow'),
                                         '\n'.join(usage))

    # Spacing based on option size
    width = max(len(opt.split('  ')[0]) for opt in options) + 2

    # When called without args print full global usage
    if not s:
        output = '{}\n\n{}\n'.format(GLOBAL_USAGE,
                                     colored('Commands:', 'yellow'))
        for cmd in sorted(COMMANDS.keys()):
            help = COMMANDS[cmd].__doc__.splitlines()[0].strip()
            output += '    {}{}{}\n'.format(cmd,
                                            ' ' * (width - len(cmd)),
                                            help)

    # Output options.
    output += '\n{}\n'.format(colored('Options:', 'yellow'))
    for opt in options:
        opt, help = opt.split('  ', 1), ''
        if isinstance(opt, list) and len(opt) == 2:
            opt, help = opt
        output += '    {}{}{}\n'.format(opt,
                                        (' ' * (width - len(opt))),
                                        help)

    # Output any misc text.
    output += '\n' + '\n'.join(line[4:] for line in description.splitlines())

    return output.strip()


def help(args):
    """Show general usage or help for a command.
    help [<command>] [options]

    Running with no arguments prints general help while specifying a command
    will give a detailed explanation of the relevant options and behaviors.
    """

    if args['<command>']:
        if args['<command>'] in COMMANDS:
            return build_usage(COMMANDS[args['<command>']].__doc__)
        else:
            return '%s not understood' % args['<command>']
    else:
        return build_usage()


GLOBAL_USAGE = colored('Usage:', 'yellow') + '''
    %s <command> [<args>] [options]''' % basename(sys.argv[0])
GLOBAL_OPTIONS = [
    '-v, --verbose  Verbose output.',
    '-q, --quiet  Minimal output.',
    '-h, --help  ' + help.__doc__.split('\n')[0]]
COMMAND_SPACING = 40  # Left column width for top-level usage or options

# Create a dictionary of type (command: function) of available commands.
std_commands = (
    allbus,
    copy,
    dump,
    help,
    stat,
    streamcheck
)
COMMANDS = {}
for cmd in std_commands:
    COMMANDS[cmd.__doc__.splitlines()[1].strip().split()[0]] = cmd
# TODO: aliases such as cp for copy and st for stat


def main(args=sys.argv[1:]):
    """Find and run the appropriate command."""

    # Reroute anything with a help flag to the help command.
    if '-h' in args or '--help' in args:
        if '-h' in args:
            args.remove('-h')
        else:
            args.remove('--help')
        args.insert(0, 'help')

    usage, command = GLOBAL_USAGE, args and args[0] or None

    # Validate the command exists.
    if '--version' not in args and command not in COMMANDS:
        print(usage)

    else:
        if command != '--version':
            func = COMMANDS[command]
            usage = build_usage(func.__doc__)

        # Parse the command (also handles version and help requests).
        args = docopt(usage, args, False, version)

        # Execute command and print any response.
        result = func(args)
        if result:
            if isinstance(result, types.GeneratorType):
                for line in result:
                    print(line)
            else:
                print(result)


if __name__ == '__main__':
    main()
