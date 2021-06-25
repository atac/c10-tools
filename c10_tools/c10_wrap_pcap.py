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

from datetime import datetime
from io import BytesIO
import os
import sys

from chapter10.computer import ComputerF1
from chapter10.message import MessageF0
from chapter10.time import TimeF1
from docopt import docopt
import dpkt

from c10_tools.common import FileProgress, fmt_number


class Parser:
    start_timestamp, seq = 0, {}
    network_packets, c10_packets = 0, 0
    last_time = 0
    MAX_BODY_SIZE = 400000

    def __init__(self, args=[]):
        self.args = args

    def make_rtc(self, timestamp):
        """Take a timestamp and give an incrementing 10Mhz equivalent time."""

        if not self.start_timestamp:
            self.start_timestamp = timestamp
            return 0
        else:
            offset = timestamp - self.start_timestamp

        # Convert seconds to 10Mhz clock and mask to 6 bytes
        return int(offset * 10_000_000) & 0xffffffffffff
    
    def write_tmats(self):
        """Generate a TMATS packet from a source file."""

        with open(self.args['-t'], 'r') as tmats:
            tmats_body = tmats.read()
        tmats = ComputerF1(data_type=1, data=tmats_body)
        self.out.write(bytes(tmats))
    
    def write_data(self, messages):
        """Make a Message packet from a list of messages."""
        
        timestamp = messages[0][0]
        while timestamp - self.last_time > 1:
            self.write_time(timestamp)

        p = MessageF0(channel_id=32, data_type=0x30,
                      count=len(messages), rtc=messages[0][1].ipts,
                      sequence_number=self.get_seq(32))
        p._messages = [m[1] for m in messages]
        self.c10_packets += 1
        self.out.write(bytes(p))
        
    def get_seq(self, channel):
        sequence_number = self.seq.get(0, 0)
        self.seq[channel] = sequence_number + 1
        if sequence_number == 255:
            self.seq[channel] = 0
        return sequence_number
    
    def write_time(self, timestamp):
        if not self.last_time:
            timestamp = int(timestamp)
        else:
            timestamp = self.last_time + 1
        self.last_time = timestamp
        t = datetime.fromtimestamp(timestamp)
        packet = TimeF1(data_type=0x11, time=t,
                        rtc=self.make_rtc(timestamp),
                        header_version=8,
                        sequence_number=self.get_seq(0))
        self.out.write(bytes(packet))

    def main(self):
        """Parse a pcap file into chapter 10 format."""
        
        self.out = open(self.args['<outfile>'], 'wb')

        if self.args['-t']:
            self.write_tmats()

        # Loop over the packets and parse into C10.Packet objects if possile.
        with open(self.args['<infile>'], 'rb') as f, \
                FileProgress(self.args['<infile>']) as progress:

            if self.args['-q']:
                progress.close()

            length, messages = 0, []
            for timestamp, ethernet in dpkt.pcap.Reader(f):
                ip = dpkt.ethernet.Ethernet(ethernet).data
                if isinstance(getattr(ip, 'data', None), dpkt.udp.UDP):
                    self.network_packets += 1

                    # Wrap message with intra-packet headers
                    data = ip.data.data[4:]
                    msg = MessageF0.Message(ipts=self.make_rtc(timestamp),
                                            length=len(data),
                                            data=data)
                    messages.append((timestamp, msg))
                    length += len(data)
                    
                    # Write packet when full.
                    if length + 4 > self.MAX_BODY_SIZE:
                        self.write_data(messages)
                        length, messages = 0, []

                # Update progress bar.
                progress.update_from_tell(f.tell())

        if messages:
            self.write_data(messages)

        if not self.args['-q']:
            print('Created %s Chapter 10 packets from %s network packets'
                    % (fmt_number(self.c10_packets),
                       fmt_number(self.network_packets)))


def main(args=sys.argv[1:]):
    args = docopt(__doc__, args)

    if os.path.exists(args['<outfile>']) and not args['-f']:
        print('Output file exists. Use -f to overwrite.')
        return

    Parser(args).main()
