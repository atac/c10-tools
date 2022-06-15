
import click

from c10_tools.allbus import allbus
from c10_tools.capture import capture
from c10_tools.copy import copy
from c10_tools.dump import dump
from c10_tools.find import find
from c10_tools.from_pcap import frompcap
from c10_tools.inspect import inspect
from c10_tools.reindex import reindex
from c10_tools.stat import stat
from c10_tools.timefix import timefix
try:
    import matplotlib
    from c10_tools.streamcheck import streamcheck
except ImportError:
    streamcheck = None


VERSION = '1.1.4'

@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('-q', '--quiet', is_flag=True, help='Minimal output')
@click.pass_context
def cli(ctx, verbose=False, quiet=False):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet

cli.add_command(allbus)
cli.add_command(capture)
cli.add_command(copy)
cli.add_command(dump)
cli.add_command(find)
cli.add_command(frompcap)
cli.add_command(inspect)
cli.add_command(reindex)
cli.add_command(stat)
cli.add_command(timefix)
if streamcheck:
    cli.add_command(streamcheck)


if __name__ == '__main__':
    cli()