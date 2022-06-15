
from contextlib import suppress
import os
import sys
import struct

from tqdm import tqdm
import click

from c10_tools.common import find_c10, C10, walk_packets


def word(b):
    """Combine two bytes into a 16-bit word."""

    return struct.unpack('=H', struct.pack('=BB', b[0], b[1]))[0]


def search(path, value, channel, exclude, type, cmd, length, offset, mask):
    """Search file "path" based on parameters from "args"."""

    print(f'\n  {path}')
    c10 = C10(path)
    args = {
        '--type': type,
        '--channel': channel,
        '--exclude': exclude
    }
    for packet in walk_packets(c10, args):

        # Assumes no secondary header.
        pos = 28

        # Iterate over messages
        for msg in packet:
            pos += len(bytes(msg))

            # 1553: match command word if requested
            if cmd:
                if packet.data_type != 0x19:
                    continue
                elif cmd != word(msg.data[:2]):
                    continue

            # Get our value to match against and convert to int.
            check_value = msg.data[offset:offset + length]
            check_value = int.from_bytes(check_value, 'little')

            if mask:
                check_value &= mask

            # Output matches
            if value == '*' or check_value == value:

                # Find message time and format
                t = ''
                with suppress(AttributeError):
                    t = msg.get_time()

                # Julian-day format
                if t and hasattr(c10, 'last_time') and not c10.last_time.date_format:
                    t = t.strftime('%j %H:%M:%S.%f')

                # Offset to start of message.
                file_pos = c10.file.tell() - packet.packet_length
                file_pos += pos - len(bytes(msg))

                hex_value = f'{check_value:02x}'
                if length:
                    hex_value = hex_value.zfill(length * 2)
                print(f'    {hex_value}  {t} at {file_pos}')


def parseint(s: str) -> int:
    """Convert a string based on binary or hex prefix if present."""

    if not s or s == '*':
        return s
    if s.startswith('0x'):
        return int(s, 16)
    if s.startswith('0b'):
        return int(s, 2)
    else:
        return int(s)


@click.command()
@click.argument('value')
@click.argument('path', nargs=-1)
@click.option('-c', '--channel', type=str, help='Specify channels (comma-separated) to include')
@click.option('-e', '--exclude', type=str, help='Specify channels (comma-separated) to exclude')
@click.option('-t', '--type', type=str, help='Specify datatypes (comma-separated) to include')
@click.option('--cmd', type=str, help='1553 command word')
@click.option('-l', '--length', default=1, help='Byte length')
@click.option('-o', '--offset', default=0, help='Byte offset within message')
@click.option('-m', '--mask', default='0', help='Value mask')
@click.pass_context
def find(ctx, value, path, channel, exclude, type, cmd, length, offset, mask):
    """Search for a given value in Chapter 10 files."""

    ctx.ensure_object(dict)

    # Validate int/hex inputs.
    cmd = parseint(cmd)
    value = parseint(value)
    mask = parseint(mask)

    # Describe the search parameters.
    value_repr = value
    if isinstance(value_repr, int):
        value_repr = hex(value_repr)
    print('Searching for %s' % value_repr, end='')
    if channel:
        print(f' in channel #{channel}', end='')
    if cmd:
        print(f' with command word {hex(cmd)}', end='')
    if offset:
        print(f' at offset {offset}', end='')
    if mask:
        print(f' with mask {mask}', end='')

    files = list(find_c10(path))

    print(f' in {len(files)} files...')
    if sys.stdout.isatty() and not ctx.obj.get('quiet'):
        files = tqdm(
            files,
            desc='Overall',
            unit='files',
            dynamic_ncols=True,
            leave=False)
    for f in files:
        search(f, value, channel, exclude, type, cmd, length, offset, mask)
    print('\nfinished')
