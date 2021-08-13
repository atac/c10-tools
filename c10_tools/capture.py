
from array import array
from contextlib import suppress
import os

from chapter10 import C10
from chapter10.computer import ComputerF1
import dpkt

from c10_tools.common import FileProgress, fmt_number


class NetworkCapture:
    """Capture Chapter 10 from an ethernet sniff or PCAP."""

    BUF_SIZE = 100000

    def __init__(self, args=[]):
        self.args = args
        self.buf = b''
        self.tmats_present = False


    def parse_bytes(self, data, out_file):
        """Adds "data" to buffer and attempts to parse chapter 10 data.
        Returns count of packets added.
        """

        packets_added = 0

        # Limit the buffer size and add new data to the buffer.
        self.buf = self.buf[-self.BUF_SIZE:] + data

        # Start each attempt from a sync pattern.
        for i in range(self.buf.count(b'\x25\xeb')):
            sync = self.buf.find(b'\x25\xeb')

            # Needed in case our sync pattern isn't around anymore.
            if sync < 0:
                continue

            with suppress(RuntimeError, EOFError):
                for packet in C10.from_string(self.buf[sync:]):

                    # Ignore data until TMATS is present.
                    if not self.tmats_present:
                        if packet.data_type == 1:
                            self.tmats_present = True
                        else:
                            continue

                    # Skip additional TMATS records
                    elif packet.data_type == 1:
                        continue

                    raw = bytes(packet)
                    if len(raw) == packet.packet_length:
                        packets_added += 1
                        out_file.write(raw)

                    # Only read one packet.
                    break

            self.buf = self.buf[sync + 2:]

        return packets_added

    def parse_pcap(self, infile, outfile):
        network_packets, c10_packets = 0, 0

        with open(infile, 'rb') as f, FileProgress(infile) as progress:

            if self.args['-q']:
                progress.close()

            for packet in dpkt.pcap.Reader(f):
                ip = dpkt.ethernet.Ethernet(packet[1]).data
                if hasattr(ip, 'data') and isinstance(
                        ip.data, dpkt.udp.UDP):
                    data = ip.data.data[4:]
                    network_packets += 1
                    c10_packets += self.parse_bytes(data, outfile)

                # Update progress bar.
                progress.update_from_tell(f.tell())

        return network_packets, c10_packets

    def main(self):
        """Parse a pcap file into chapter 10 format."""

        with open(self.args['<outfile>'], 'wb') as out:

            # Write TMATS if needed.
            if self.args['-t']:
                with open(self.args['-t'], 'r') as tmats:
                    tmats_body = tmats.read()
                tmats = ComputerF1(data_type=1, data=tmats_body)
                out.write(bytes(tmats))
                self.tmats_present = True

            # Parse data.
            network_packets, c10_packets = self.parse_pcap(
                self.args['<infile>'], out)

            if not self.args['-q']:
                print('Parsed %s Chapter 10 packets from %s network packets'
                      % (fmt_number(c10_packets), fmt_number(network_packets)))


def main(args):
    """Capture chapter 10 data from a pcap file.
    capture -p <infile> <outfile> [options]
    -q  Don't display progress bar.
    -f  Overwrite existing output file.
    -t <tmats_file>  Insert an existing TMATS record at the beginning of the\
output file.
    """

    if os.path.exists(args['<outfile>']) and not args['-f']:
        print('Output file exists. Use -f to overwrite.')
        raise SystemExit

    parser = NetworkCapture(args)
    parser.main()
