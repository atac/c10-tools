#!/usr/bin/env python

"""Wrap ethernet data in a pcap file in a valid chapter 10 file.

usage: c10-wrap-pcap <infile> <outfile> [options]

Options:
    -q               Don't display progress bar.
    -f               Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
"""

# @TODO: make channel # and datatype options

from array import array
from datetime import datetime
import os
import struct

from docopt import docopt
import dpkt

from common import FileProgress, fmt_number

start_timestamp, seq = 0, {}


def make_rtc(timestamp):
    """Take a timestamp and give an incrementing 10Mhz equivalent time."""

    global start_timestamp

    if not start_timestamp:
        start_timestamp = timestamp
        offset = 0
    else:
        offset = timestamp - start_timestamp

    # Convert seconds to 10Mhz clock
    return int(offset * 10000000)


def gen_packet(channel, type, time, body):
    """Quickly and easily build a packet given just a few arguments."""

    sequence_number = seq.get(channel, 0)
    seq[channel] = sequence_number + 1

    # Split RTC into high and low components
    rtc = make_rtc(time)
    rtc_low = int((rtc >> 32) & 0xffffffff)
    rtc_high = int((rtc >> 16) & 0xffff)

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
    checksum = sum(array('H', struct.pack('=HHIIBBBBIH', *header))) & 0xffff
    header.append(checksum)
    header = struct.pack('=HHIIBBBBIHH', *header)
    return header + body


def time_packet(t):
    """Generate and return a complete time packet from a unix timestamp."""

    time = datetime.fromtimestamp(t)

    # Time
    TSn, Sn = (int(char) for char in str(time.second).zfill(2))
    Hmn, Tmn = (int(char)
                for char in str(time.microsecond).zfill(2)[:2])
    TMn, Mn = (int(char) for char in str(time.minute).zfill(2))
    THn, Hn = (int(char) for char in str(time.hour).zfill(2))

    # IRIG day
    day = time.timetuple().tm_yday
    HDn, TDn, Dn = (int(char) for char in str(day))

    data = [
        (TSn << 12) + (Sn << 8) + (Hmn << 4) + Tmn,
        (THn << 12) + (Hn << 8) + (TMn << 4) + Mn,
        (HDn << 8) + (TDn << 4) + Dn
    ]
    body = struct.pack('xxxxH' * len(data), *data)
    return gen_packet(0, 0x10, t, body)


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
            with open(args['-t'], 'r') as tmats:
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

            out.write(tmats_body.encode('utf8'))

        # Loop over the packets and parse into C10.Packet objects if possible.
        packets, added = 0, 0

        with open(args['<infile>'], 'rb') as f, \
                FileProgress(args['<infile>']) as progress:

            if args['-q']:
                progress.close()

            first_time, frames, packet = None, 0, b''
            file_start_time = None

            for timestamp, ether in dpkt.pcap.Reader(f):
                if first_time is None:
                    first_time = timestamp
                if file_start_time is None:
                    file_start_time = timestamp
                    out.write(time_packet(timestamp))
                ether = dpkt.ethernet.Ethernet(ether)
                ip = ether.data
                if hasattr(ip, 'data') and isinstance(
                        ip.data, dpkt.udp.UDP):

                    # Payload
                    data = ip.data.data[4:]

                    ipts = struct.pack('Q', make_rtc(timestamp))
                    packet += ipts

                    # IPDH
                    # ethernet
                    # first, second = struct.unpack('xhh', ether.src)
                    # virtual_link = int((first << 8) & second)
                    # src_ip, = struct.unpack('I', ip.src)
                    # dst_ip, = struct.unpack('I', ip.dst)
                    # ipdh = struct.pack('HxxxxHIIHH',
                    #                  len(data), virtual_link, src_ip, dst_ip,
                    #                    ip.data.sport, ip.data.dport)

                    # message
                    ipdh = struct.pack('=HH', 99, len(data))

                    packet += ipdh
                    packet += data

                    frames += 1
                    if len(packet) + 4 > MAX_BODY_SIZE:
                        # ethernet packets
                        # csdw = struct.pack('HH', frames, 24)
                        # out.write(gen_packet(
                        #     40, 0x69, first_time, csdw + packet))

                        # message packets
                        csdw = struct.pack('HH', frames, 0)
                        out.write(gen_packet(
                            32, 0x30, first_time, csdw + packet))

                        added += 1
                        first_time, frames, packet = None, 0, b''

                    packets += 1

                # Update progress bar.
                progress.update_from_tell(f.tell())

        if packet:
            # message packets
            csdw = struct.pack('HH', 0, frames)
            out.write(gen_packet(
                32, 0x30, first_time, csdw + packet))
            added += 1
            first_time, frames, packet = None, 0, b''
            added += 1

        if not args['-q']:
            print('Created %s Chapter 10 packets from %s network packets' % (
                fmt_number(added), fmt_number(packets)))


if __name__ == '__main__':
    main()
