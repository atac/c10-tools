#!/usr/bin/env python

"""Wrap ethernet data in a pcap file in a valid chapter10 file.

usage: c10-wrap-pcap <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
"""

from array import array
import os
import struct
import time

from docopt import docopt
import dpkt

from common import FileProgress, fmt_number

start_timestamp, seq = 0, {}


def rtc(timestamp):
    """Take a timestamp and give an incrementing 10Mhz equivalent time."""

    global start_timestamp

    if not start_timestamp:
        start_timestamp = time
        offset = 0
    else:
        offset = time - start_timestamp

    # Convert seconds to 10Mhz clock
    return offset / 10000000


def gen_packet(channel, type, time, body):
    """Quickly and easily build a packet given just a few arguments."""

    sequence_number = seq.get(channel, 0)
    seq[channel] = sequence_number + 1

    # Split RTC into high and low components
    rtc_high, rtc_low = struct.unpack('IHxx', struct.pack('Q', rtc(time)))

    header = [
        0xeb25,
        channel,
        len(body) + 24,
        len(body),
        1,
        sequence_number,
        0,
        type,
        rtc_low,
        rtc_high,
    ]
    header.append(sum(header))
    try:
        header, = struct.pack('HHIIBBBBIHH', *header)
    except:
        print header
        raise
    return header + body


MAX_BODY_SIZE = 500000


def main():
    """Parse a pcap file into chapter 10 format."""

    args = docopt(__doc__)

    if os.path.exists(args['<outfile>']) and not args['-f']:
        print('Output file exists. Use -f to overwrite.')
        return

    with open(args['<outfile>'], 'wb') as out:

        # Write TMATS.
        if args['-t']:
            with open(args['<tmats_file>'], 'r') as tmats:
                tmats_body = tmats.read()

            header_values = [
                0xeb25,
                0,
                len(tmats_body) + 24,
                len(tmats_body),
                0,
                0,
                0,
                1,
                0,
                0,
            ]

            header = struct.pack('HHIIBBBBIH', *header_values)
            out.write(header)

            # Compute and append checksum.
            sums = sum(array('H', header)) & 0xffff
            out.write(struct.pack('H', sums))

            out.write(tmats_body)

        # Loop over the packets and parse into C10.Packet objects if possible.
        packets, added = 0, 0

        with open(args['<infile>'], 'rb') as f, \
                FileProgress(args['<infile>']) as progress:

            if args['-q']:
                progress.close()

            first_time, frames, packet = None, 0, ''

            for timestamp, ether in dpkt.pcap.Reader(f):
                timestamp = time.gmtime(timestamp)
                if first_time is None:
                    first_time = timestamp
                ether = dpkt.ethernet.Ethernet(ether)
                ip = ether.data
                if hasattr(ip, 'data') and isinstance(
                        ip.data, dpkt.udp.UDP):

                    # Payload
                    data = ip.data.data[4:]

                    # @TODO: add IPTS

                    # IPDH
                    first, second = struct.unpack('xhh', ether.src)
                    virtual_link = int((first << 8) & second)
                    src_ip, = struct.unpack('I', ip.src)
                    dst_ip, = struct.unpack('I', ip.dst)
                    ipdh = struct.pack('HxxxxHIIHH',
                                       len(data), virtual_link, src_ip, dst_ip,
                                       ip.data.sport, ip.data.dport)
                    packet += ipdh

                    packet += data

                    frames += 1
                    if len(packet) + 4 > MAX_BODY_SIZE:
                        csdw = struct.pack('HH', 24, frames)
                        out.write(gen_packet(
                            10, 0x69, first_time, csdw + packet))
                        first_time, frames, packet = None, 0, ''
                        added += 1

                    packets += 1

                # Update progress bar.
                progress.update_from_tell(f.tell())

        if not args['-q']:
            print('Parsed %s Chapter 10 packets from %s network packets' % (
                fmt_number(added), fmt_number(packets)))

if __name__ == '__main__':
    main()
