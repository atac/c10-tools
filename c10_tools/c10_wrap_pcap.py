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
import sys

from docopt import docopt
import dpkt

from c10_tools.common import FileProgress, fmt_number


class Parser:
    start_timestamp, seq = 0, {}
    MAX_BODY_SIZE = 500000

    def __init__(self, args=[]):
        self.args = docopt(__doc__, args)

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

    def gen_packet(self, channel, type, time, body):
        """Quickly and easily build a packet given just a few arguments."""

        sequence_number = self.seq.get(channel, 0)
        self.seq[channel] = sequence_number + 1

        # Split RTC into high and low components
        rtc = self.make_rtc(time)
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
        checksum = sum(
            array('H', struct.pack('=HHIIBBBBIH', *header))) & 0xffff
        header.append(checksum)
        header = struct.pack('=HHIIBBBBIHH', *header)
        return header + body

    def time_packet(self, t):
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
        return self.gen_packet(0, 0x10, t, body)

    def main(self):
        """Parse a pcap file into chapter 10 format."""

        if os.path.exists(self.args['<outfile>']) and not self.args['-f']:
            print('Output file exists. Use -f to overwrite.')
            return

        with open(self.args['<outfile>'], 'wb') as out:

            # Write TMATS.
            if self.args['-t']:
                with open(self.args['-t'], 'r') as tmats:
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

            # Loop over the packets and parse into C10.Packet objects if
            # possile.
            packets, added = 0, 0

            with open(self.args['<infile>'], 'rb') as f, \
                    FileProgress(self.args['<infile>']) as progress:

                if self.args['-q']:
                    progress.close()

                first_time, frames, packet = None, 0, b''
                file_start_time = None

                for timestamp, ether in dpkt.pcap.Reader(f):
                    if first_time is None:
                        first_time = timestamp
                    if file_start_time is None:
                        file_start_time = timestamp
                        out.write(self.time_packet(timestamp))
                    ether = dpkt.ethernet.Ethernet(ether)
                    ip = ether.data
                    if hasattr(ip, 'data') and isinstance(
                            ip.data, dpkt.udp.UDP):

                        # Payload
                        data = ip.data.data[4:]

                        ipts = struct.pack('Q', self.make_rtc(timestamp))
                        packet += ipts

                        # message
                        ipdh = struct.pack('=HH', 99, len(data))

                        packet += ipdh
                        packet += data

                        frames += 1
                        if len(packet) + 4 > self.MAX_BODY_SIZE:
                            # ethernet packets
                            # csdw = struct.pack('HH', frames, 24)
                            # out.write(gen_packet(
                            #     40, 0x69, first_time, csdw + packet))

                            # message packets
                            csdw = struct.pack('HH', frames, 0)
                            out.write(self.gen_packet(
                                32, 0x30, first_time, csdw + packet))

                            added += 1
                            first_time, frames, packet = None, 0, b''

                        packets += 1

                    # Update progress bar.
                    progress.update_from_tell(f.tell())

            if packet:
                # message packets
                csdw = struct.pack('HH', 0, frames)
                out.write(self.gen_packet(
                    32, 0x30, first_time, csdw + packet))
                added += 1
                first_time, frames, packet = None, 0, b''
                added += 1

            if not self.args['-q']:
                print('Created %s Chapter 10 packets from %s network packets'
                      % (fmt_number(added), fmt_number(packets)))


def main():
    Parser(sys.argv[1:]).main()


if __name__ == '__main__':
    main()
