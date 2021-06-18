
from time import mktime
import os
import struct
import sys
import csv

from docopt import docopt
from dask.delayed import delayed
import dask.bag as db
from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.pcap import Writer
from dpkt.udp import UDP
from termcolor import colored

from c10_tools.common import find_c10, FileProgress, C10, fmt_table, walk_packets, get_time


def events(args=sys.argv[1:]):
    print(colored('This will be deprecated in favor of c10 stat --verbose'))
    args = docopt('usage: c10-events <input_file>', args)

    last_time = None
    for packet in C10(args['<input_file>']):
        if packet.data_type == 0x11:
            last_time = packet
            continue

        if packet.data_type == 0x2:
            print('Recording Event packet at {}'.format(get_time(
                packet.rtc, last_time)))
            for i, entry in enumerate(packet):
                print(entry.__dict__)
                t = get_time(entry.ipts, last_time)
                print(f'''    {i + 1} of {len(packet)} at {t}
    Occurrence: {entry.occurrence}
    Count: {entry.count}
    Number: {entry.number})''')
    

def dmp1553(args=sys.argv[1:]):
    """usage: c10-dmp1553 <file> <word> [options]

    Print a hex dump of word "<word>" for any 1553 messages found.

    Options:
        -w COUNT, --word-count COUNT  Number of words to print out [default: 1].
    """

    print(colored('This will be deprecated in favor of c10 dump', 'red'))

    # Get commandline args.
    args = docopt(dmp1553.__doc__, args)
    word = int(args.get('<word>'))
    size = int(args.get('--word-count'))

    # Iterate over packets based on args.
    for packet in C10(args['<file>']):

        if packet.data_type == 25:
            for msg in packet:
                s = ''
                msg = getattr(msg, 'data', msg)
                for w in msg[word:word + size]:
                    s += f'{w:02x}'.zfill(4) + ' '
                if s:
                    print(s)
                    

def dump_pcap(args=sys.argv[1:]):
    """Extract ethernet data from a chapter 10 file and export as a pcap file.

    usage: c10-dump-pcap <src> <dst> <channel> [options]

    Options:
        -q          Don't display progress bar
        -f --force  Overwrite existing files."""

    print(colored('This will be deprecated in favor of c10 dump', 'red'))

    # Get commandline args.
    args = docopt(dump_pcap.__doc__, args)
    args['<channel>'] = int(args['<channel>'])

    # Don't overwrite unless explicitly required.
    if os.path.exists(args['<dst>']) and not args['--force']:
        print('dst file already exists. Use -f to overwrite.')
        raise SystemExit

    # Open input and output files.
    with open(args['<dst>'], 'wb') as out, FileProgress(args['<src>']) \
            as progress:

        writer = Writer(out)
        last_time = None

        # Iterate over packets based on args.
        for packet in walk_packets(C10(args['<src>']), args):

            progress.update(packet.packet_length)

            # Track time
            if packet.data_type == 0x11:
                last_time = packet
                continue

            if packet.channel_id != args['<channel>']:
                continue

            for msg in packet:
                data = msg.data

                # Ethernet format 1 (ARINC 664)
                if packet.data_type == 0x69:
                    udp = UDP(
                        sport=msg.src_port,
                        dport=msg.dst_port,
                        data=data)
                    ip = IP(data=udp,
                            len=len(udp),
                            v=4,
                            p=17,
                            src=struct.pack('>L', msg.source_ip),
                            dst=struct.pack('>L', msg.dest_ip)).pack()
                    ethernet = Ethernet(
                        data=ip,
                        len=len(ip),
                        dst=struct.pack('>IH', 50331648, msg.virtual_link),
                        src=bytes()
                    )

                    data = ethernet.pack()

                t = get_time(msg.ipts, last_time)
                t = mktime(t.timetuple()) + (t.microsecond/1000000.0)
                writer.writepkt(data, t)
                

error_keys = ('le', 'se', 'we')


def parse_file(path, args):

    # Parse file.
    errcount = 0
    chan_errors = {}
    chan_count = {}

    if not args['-q']:
        progress = FileProgress(path)

    for packet in C10(path):
        if packet.data_type == 25:
            try:
                chan_count[packet.channel_id] += 1
            except KeyError:
                chan_count[packet.channel_id] = 1
            valid = True
            for msg in packet:
                errors = [getattr(msg, k) for k in error_keys]
                count = sum(errors)
                if count:
                    valid = False
                errcount += count

                if packet.channel_id not in chan_errors:
                    chan_errors[packet.channel_id] = errors
                else:
                    for i, err in enumerate(errors):
                        chan_errors[packet.channel_id][i] += err

            if args['-o'] and not valid:
                # Log to file
                with open(args['-o'], 'a') as logfile:
                    writer = csv.writer(logfile, lineterminator='\n')
                    row = [path]
                    for k in ('Channel ID', 'Sequence Number', 'RTC'):
                        attr = '_'.join(k.split()).lower()
                        row.append(getattr(packet, attr))
                    for e in chan_errors[packet.channel_id]:
                        row.append(str(e))

                    row.append(str(sum(chan_errors[packet.channel_id])))
                    writer.writerow(row)

        if not args['-q']:
            try:
                progress.update(packet.packet_length)
            except UnicodeEncodeError:
                progress.ascii = True

    # Print summary.
    print('File: ', path)
    table = [('Channel ID', 'Length', 'Sync', 'Word', 'Total', 'Packets')]
    for k, v in sorted(chan_errors.items()):
        row = [f'{cell:,}' for cell in [k] + v]
        row += [
            f'{sum(v):>,}',
            f'{chan_count[k]:>,}']
        table.append(row)

    footer = ['Totals:']
    for i in range(len(error_keys)):
        type_total = sum([chan[i] for chan in chan_errors.values()])
        footer.append(str(type_total))
    footer += [str(errcount), str(sum(chan_count.values()))]
    table.append(footer)

    print(fmt_table(table))


def errcount(args=sys.argv[1:]):
    """usage: c10-errcount <path>... [options]

    Counts error flags in 1553 format 1 packets.

    Options:
        -q            Quiet output (no progress bar)
        -o <logfile>  Output to CSV file with channel, sequence, and rtc
        -x            Run with multiprocessing (using dask)
    """

    print(colored('This will be deprecated in favor of c10 stat --verbose'))
    args = docopt(errcount.__doc__, args)
    if args['-o']:
        with open(args['-o'], 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(('File', 'Channel', 'Sequence', 'RTC',
                             'Length Errors', 'Sync Errors', 'Word Errors',
                             'Total Errors'))
    files = find_c10(args['<path>'])
    if args.get('-x'):
        bag = db.from_delayed([delayed(parse_file)(path, args=args)
                               for path in files])
        bag.compute()
    else:
        for path in files:
            parse_file(path, args)