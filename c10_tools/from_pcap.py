
from datetime import datetime
import os

from chapter10.computer import ComputerF1
from chapter10.message import MessageF0
from chapter10.time import TimeF1
from dpkt import pcap
from dpkt.ethernet import Ethernet
from dpkt.udp import UDP
import click

from c10_tools.common import FileProgress, fmt_number


class Parser:
    start_timestamp, seq = 0, {}
    network_packets, c10_packets = 0, 0
    last_time = 0
    MAX_BODY_SIZE = 400000

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def make_rtc(self, timestamp):
        """Take a timestamp and give an incrementing 10Mhz equivalent time."""

        if not self.start_timestamp:
            self.start_timestamp = timestamp
            return 0

        offset = timestamp - self.start_timestamp

        # Convert seconds to 10Mhz clock and mask to 6 bytes
        return int(offset * 10_000_000) & 0xffffffffffff

    def write_tmats(self):
        """Generate a TMATS packet from a source file."""

        with open(self.tmats, 'r') as tmats:
            tmats_body = tmats.read()
        tmats = ComputerF1(data_type=1, data=tmats_body)
        self.out.write(bytes(tmats))

    def write_data(self, messages):
        """Make a Message packet from a list of messages."""

        timestamp = messages[0][0]
        while timestamp - self.last_time > 1:
            self.write_time(timestamp)

        p = MessageF0(channel_id=32, data_type=0x30,
                      count=len(messages), rtc=self.make_rtc(timestamp),
                      sequence_number=self.get_seq(32))
        p._messages = [m[1] for m in messages]
        self.c10_packets += 1
        self.out.write(bytes(p))

    def get_seq(self, channel):
        """Get a valid sequence number for a given channel ID."""

        sequence_number = self.seq.get(0, 0)
        self.seq[channel] = sequence_number + 1
        if sequence_number == 255:
            self.seq[channel] = 0
        return sequence_number

    def write_time(self, timestamp):
        """Write a Chapter 10 time packet based on a unix timestamp."""

        if self.last_time:
            timestamp = self.last_time + 1
        timestamp = int(timestamp)
        self.last_time = timestamp
        packet = TimeF1(data_type=0x11,
                        time=datetime.fromtimestamp(timestamp),
                        rtc=self.make_rtc(timestamp),
                        header_version=8,
                        sequence_number=self.get_seq(0))
        self.out.write(bytes(packet))

    def parse_udp(self, timestamp, data):
        self.network_packets += 1
        msg = MessageF0.Message(ipts=self.make_rtc(timestamp),
                                length=len(data),
                                data=data)
        return bytes(msg)

    def parse_and_write(self):
        """Parse a pcap file into chapter 10 format."""

        self.out = open(self.outfile, 'wb')

        if self.tmats:
            self.write_tmats()

        with FileProgress(self.infile, disable=self.quiet) as progress:

            f = open(self.infile, 'rb')
            length, messages = 0, []
            for timestamp, ethernet in pcap.Reader(f):
                ip = Ethernet(ethernet).data
                if isinstance(getattr(ip, 'data', None), UDP):
                    msg = self.parse_udp(timestamp, ip.data.data[4:])
                    messages.append((timestamp, msg))
                    length += len(msg)

                    # Write packet when full.
                    if length > self.MAX_BODY_SIZE:
                        self.write_data(messages)
                        length, messages = 0, []

                progress.update_from_tell(f.tell())

        # Write any remaining messages.
        if messages:
            self.write_data(messages)

        if not self.quiet:
            print('Created %s Chapter 10 packets from %s network packets'
                    % (fmt_number(self.c10_packets),
                       fmt_number(self.network_packets)))


# @TODO: make channel # and datatype options
@click.command()
@click.argument('infile')
@click.argument('outfile')
@click.option('-f', '--force', is_flag=True, help='Overwrite existing files')
@click.option('-t', '--tmats', help='Insert an existing TMATS record at the beginning off the output file')
@click.pass_context
def frompcap(ctx, infile, outfile, force=False, tmats=None):
    """Wrap network data in a pcap file as Chapter 10 Message format."""

    ctx.ensure_object(dict)

    if os.path.exists(outfile) and not force:
        print('Output file exists. Use -f to overwrite.')
        raise SystemExit

    p = Parser(infile=infile,
               outfile=outfile,
               force=force,
               tmats=tmats,
               verbose=ctx.obj.get('verbose'),
               quiet=ctx.obj.get('quiet'))
    p.parse_and_write()
