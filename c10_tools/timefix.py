
from datetime import timedelta
import os

import click

from c10_tools.common import FileProgress, C10


def valid(timestamp, previous):
    """Validate a timestamp based on previous recorded one
    (should be at 1-second intervals).
    """

    if previous is None:
        return True

    diff = max(timestamp, previous) - min(timestamp, previous)
    return diff == timedelta(seconds=1)


@click.command
@click.argument('infile')
@click.argument('outfile')
@click.option('-f', '--force', is_flag=True, help='Overwrite existing files.')
@click.pass_context
def timefix(ctx, infile, outfile, force=False):
    """Ensure that time packets are at 1-second intervals."""

    ctx.ensure_object(dict)

    if os.path.exists(outfile) and not force:
        print('Output file exists. Use -f to overwrite.')
        raise SystemExit

    last_time = None
    with FileProgress(infile, disable=ctx.obj.get('quiet')) as progress, open(outfile, 'wb') as out_f:
        for packet in C10(infile):
            progress.update(packet.packet_length)

            if packet.data_type == 0x11:
                if not valid(packet.time, last_time):
                    packet.time = last_time + timedelta(seconds=1)
                last_time = packet.time

            out_f.write(bytes(packet))