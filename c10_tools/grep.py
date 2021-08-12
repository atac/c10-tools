
from contextlib import suppress
import os
import struct

from tqdm import tqdm

from c10_tools.common import find_c10, C10, walk_packets


def word(b):
    """Combine two bytes into a 16-bit word."""

    return struct.unpack('=H', struct.pack('=BB', b[0], b[1]))[0]


def search(path, args):
    """Search file "path" based on parameters from "args"."""

    print(f'\n  {path}')
    c10 = C10(path)
    for packet in walk_packets(c10, args):

        # Iterate over messages
        for msg in packet:
            # 1553
            if packet.data_type == 0x19:

                # Match command word
                cmd = word(msg.data[:2])
                if args.get('--cmd') and args.get('--cmd') != cmd:
                    continue

            offset = args.get('--offset')
            value = msg.data[offset:offset + args.get('--length')]
            value = int.from_bytes(value, 'little')

            if args.get('--mask') is not None:
                value &= args.get('--mask')

            # Output findings
            if args.get('<value>') == '*' or value == args.get('<value>'):

                # Find message time and format
                t = ''
                with suppress(AttributeError):
                    t = msg.get_time()
                if hasattr(c10, 'last_time') and not c10.last_time.date_format:
                    t = t.strftime('%j %H:%M:%S.%f')

                # TODO: give file offset
                s = f'    {t}'
                if args.get('<value>') == '*':
                    s += f'{hex(value)}'
                print(s)



def main(args):
    """Search for a given value in Chapter 10 files.
    grep <value> <path>... [options]
    -c CHANNEL, --channel CHANNEL  Channel ID[s]
    -t TYPE, --type TYPE  Data type
    -e EXCLUDE, --exclude EXCLUDE  Channel[s] to ignore
    --cmd CMDWORD  1553 Command word
    -l LENGTH, --length LENGTH  Byte length [default: 1]
    -o OFFSET, --offset OFFSET  Byte offset within message [default: 0]
    -m MASK, --mask=MASK  Value mask
    """

    # Validate int/hex inputs.
    for key in ('--offset', '--cmd', '<value>', '--mask', '--length'):
        value = args.get(key)
        if not value:
            continue
        if key == '<value>' and value == '*':
            continue
        try:
            if args[key].lower().startswith('0x'):
                args[key] = int(args[key], 16)
            elif args[key].lower().startswith('0b'):
                args[key] = int(args[key], 2)
            else:
                args[key] = int(args[key])
        except ValueError:
            print('Invalid value "%s" for %s' % (args[key], key))
            raise SystemExit

    # Describe the search parameters.
    value_repr = args.get('<value>')
    if isinstance(value_repr, int):
        value_repr = hex(value_repr)
    print('Searching for %s' % value_repr, end='')
    if args.get('--channel'):
        print(' in channel #%s' % args.get('--channel'), end='')
    if args.get('--cmd'):
        print(' with command word %s' % hex(args.get('--cmd')), end='')
    if args.get('--offset'):
        print(' at offset %s' % args.get('--offset'), end='')
    if args.get('--mask'):
        print(' with mask %s' % hex(args.get('--mask')), end='')

    files = list(find_c10(args.get('<path>')))

    print(' in %s files...' % len(files))
    files = tqdm(
        files,
        desc='Overall',
        unit='files',
        dynamic_ncols=True,
        leave=False)
    if os.fstat(0) == os.fstat(1):
        files.close()
    for f in files:
        search(f, args)
    print('\nfinished')
