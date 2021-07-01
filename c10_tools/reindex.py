
import os

from chapter10.computer import ComputerF3
from docopt import docopt
from termcolor import colored

from c10_tools.common import FileProgress, C10


class Parser:
    # Sequence number for channel 0
    seq = 0

    def __init__(self, args):
        self.args = args
        self.out = open(self.args['<dst>'], 'wb')
        self.messages = []
        self.nodes = []
        self.last_root = None
        
    def get_seq(self):
        value = self.seq
        self.seq = (self.seq + 1) & 0xff
        return value
        
    def write_node(self):
        """Write an index node packet."""
        
        offset = self.out.tell()
        packet = ComputerF3(
            index_type=1,
            seq=self.get_seq(),
            count=len(self.messages),
            file_size_present=1,
            rtc=self.messages[-1].ipts,
            file_size=offset,
        )
        packet._messages = self.messages
        self.out.write(bytes(packet))
        self.messages = []

        self.nodes.append(ComputerF3.Message(ipts=packet.rtc, offset=offset))

    def write_root(self):
        """Generate a root index packet."""

        offset = self.out.tell()
        packet = ComputerF3(
            seq=self.get_seq(),
            count=len(self.nodes),
            file_size_present=1,
            rtc=self.nodes[-1].ipts,
            file_size=offset,
            root_offset=self.last_root if self.last_root else offset,
        )
        packet._messages = self.nodes
        self.out.write(bytes(packet))
        self.nodes = []
        self.last_root = offset

    def main(self):
        with FileProgress(self.args['<src>'], disable=self.args['--quiet']) \
                as progress:
            for packet in C10(self.args['<src>']):
                progress.update(packet.packet_length)

                # Skip old index packets.
                if packet.data_type == 0x03:
                    continue

                # Write data to output file.
                self.out.write(bytes(packet))

                # Just stripping existing indices so move along.
                if self.args['--strip']:
                    continue

                self.messages.append(ComputerF3.Message(
                    channel_id=packet.channel_id,
                    data_type=packet.data_type,
                    ipts=packet.rtc,
                    offset=self.out.tell() - packet.packet_length
                ))

                # Projected index node packet size.
                size = 36 + (20 * len(self.messages))

                # Write index if we run across a recording index or time
                # packet.
                if packet.data_type in (0x02, 0x11) or size > 524000:
                    self.write_node()

                # Write root index if needed.
                if (44 + (16 * len(self.nodes))) > 524000:
                    self.write_root()

            # Final indices.
            if self.messages:
                self.write_node()
            if self.nodes:
                self.write_root()

        if self.args['--strip']:
            print('Stripped existing indices.')


def wrapper():
    """usage: c10-reindex <src> <dst> [options]

    Options:
        -s, --strip  Strip existing index packets and exit.
        -f, --force  Overwrite existing files.
    """

    print(colored('This will be deprecated in favor of c10 reindex', 'red'))
    main(docopt(wrapper.__doc__))
    

def main(args):
    """Remove or recreate index packets for a file.
    reindex <src> <dst> [options]
    -s, --strip  Strip existing index packets and exit.
    -f, --force  Overwrite existing files.
    """

    if os.path.exists(args['<dst>']) and not args['--force']:
        print('Destination file already exists. Use -f to overwrite.')
        raise SystemExit

    Parser(args).main()