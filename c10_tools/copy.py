
from datetime import datetime, timedelta
import os

from c10_tools.common import walk_packets, FileProgress, C10


def parse_offset(s):
    """Take byte or time offset and return the correct object."""

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


def as_hex(bytes):
    from array import array
    return ' '.join(hex(b)[2:].zfill(2) for b in array('B', bytes))


def main(args):
    """Copy a Chapter 10 file. Can selectively copy by channel, type, byte \
offset, or time.
    copy <src> <dst> [options]
    copy <src> <dst> <end> [options]
    copy <src> <dst> <start> <end> [options]
    -c CHANNEL..., --channel CHANNEL...  Specify channels to include (comma \
separated).
    -e CHANNEL..., --exclude CHANNEL...  Specify channels to ignore (comma \
separated).
    -t TYPE, --type TYPE  The types of data to copy (comma separated, may be \
decimal or hex eg: 0x40)
    -f --force  Overwrite existing files.
    -s, --slice  Slice a file based on time or byte offset.

    Optional "<start>" is offset into file to start from. "<end>" is the offset
    from "<start>" or file start to trim to. "<start>" and "<end>" can be any
    combination of:
        byte offset
        relative time (HH:MM:SS.ms)
        absolute time (DDD:HH:MM:SS.ms) where DDD is julian day.
    """

    # TODO: make dst optional or add 'stdout' option?

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    start, end = 0, None
    if args.get('<end>'):
        end = parse_offset(args['<end>'])
    if args.get('<start>'):
        start = parse_offset(args['<start>'])

    if isinstance(end, int) and isinstance(start, int):
        end += start

    # Timestamp of offset 0 into the file
    start_time = None
    slice_start = None

    with open(args['<dst>'], 'wb') as out, FileProgress(args['<src>']) \
            as progress:

        # Iterate over packets based on args.
        offset = 0
        for packet in walk_packets(C10(args['<src>']), args, include_time=False):
            progress.update(packet.packet_length)

            if not start_time and packet.data_type == 0x11:
                start_time = packet.time

                if isinstance(start, timedelta):
                    start += packet.time

                if isinstance(end, timedelta):
                    if isinstance(start, datetime):
                        end += start
                    else:
                        end += start_time

                if isinstance(end, datetime):
                    end = end.replace(year=packet.time.year)

            # If we haven't reached start yet
            if isinstance(start, int) and offset < start:
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
            elif start_time and isinstance(end, datetime) and \
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
