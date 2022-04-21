
from datetime import datetime, timedelta
import os

import click

from chapter10.computer import ComputerF1
from c10_tools.common import walk_packets, FileProgress, C10


def parse_offset(s):
    """Take byte or time offset and return the correct object."""

    if s is None:
        return

    # Byte offset
    if s.isnumeric():
        return int(s)

    # Absolute or relative time
    fmt = '%j:%H:%M:%S.%f'
    if '.' not in s:
        fmt, _ = fmt.split('.')
    while fmt.count(':') > s.count(':'):
        _, fmt = fmt.split(':', 1)
    dt = datetime.strptime(s, fmt)
    if s.count(':') == 3:
        return dt
    else:
        return timedelta(hours=dt.hour,
                         minutes=dt.minute,
                         seconds=dt.second,
                         microseconds=dt.microsecond)


@click.command
@click.option('-c', '--channel', type=str, help='Specify channels (comma-separated) to include')
@click.option('-e', '--exclude', type=str, help='Specify channels (comma-separated) to exclude')
@click.option('-t', '--type', type=str, help='Specify datatypes (comma-separated) to include')
@click.option('-f', '--force', is_flag=True, help='Overwrite existing files')
@click.argument('src')
@click.argument('dst')
@click.argument('start', default='0')
@click.argument('end', required=False)
@click.pass_context
def copy(ctx, src, dst, start, end, channel=None, exclude=None, type=None, force=False):
    """Copy a Chapter 10 file. Can selectively copy by channel, type, byte \
    offset, or time.

    Optional "START" is offset into file to start from. "END" is the offset
    from "START" or file start to trim to. "START" and "END" can be any
    combination of:

    \b
        byte offset
        relative time (HH:MM:SS.ms)
        absolute time (DDD:HH:MM:SS.ms) where DDD is julian day.
    """

    # TODO: make dst optional or add 'stdout' option?

    # Don't overwrite unless explicitly required.
    if os.path.exists(dst) and not force:
        click.echo('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    start = parse_offset(start)
    end = parse_offset(end)

    if isinstance(end, int) and isinstance(start, int):
        end += start

    # Timestamp of offset 0 into the file
    file_start_time = None
    slice_start = None

    with open(dst, 'wb') as out, FileProgress(src) as progress:

        # Iterate over packets based on args.
        offset = 0
        args = {
            '--type': type,
            '--channel': channel,
            '--exclude': exclude,
        }
        for packet in walk_packets(C10(src), args, include_time=False):
            progress.update(packet.packet_length)

            # First time packet
            if not file_start_time and packet.data_type == 0x11:
                file_start_time = packet.time

                if isinstance(start, timedelta):
                    start += packet.time
                elif isinstance(start, datetime):
                    start = start.replace(year=packet.time.year)

                if isinstance(end, timedelta):
                    if isinstance(start, datetime):
                        end += start
                    else:
                        end += file_start_time

                elif isinstance(end, datetime):
                    end = end.replace(year=packet.time.year)

            # Can't check time until we find a time packet. Preserve TMATS
            if start and not file_start_time and not isinstance(packet, ComputerF1):
                pass

            # If we haven't reached start yet
            elif isinstance(start, int) and offset < start:
                pass
            elif isinstance(start, datetime) and packet.get_time() < start:
                pass

            # If we've reached the end
            elif isinstance(end, int) and (
                    offset + packet.packet_length) > end:
                # Trim
                if start == 0:
                    return
                # Slice
                elif slice_start is not None:
                    break
            elif file_start_time and isinstance(end, datetime) and \
                    packet.get_time() > end:
                break
            else:
                if slice_start is None:
                    slice_start = offset
                    if isinstance(end, int):
                        end += slice_start

                # Copy packet to new file.
                out.write(bytes(packet))

            offset += packet.packet_length
