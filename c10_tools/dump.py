
from array import array
import struct
import sys

from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.pcap import Writer
from dpkt.udp import UDP

from c10_tools.common import FileProgress, C10, get_time


def main(args):
    """Dump hex (default), binary data, or PCAP from a Chapter 10 channel.
    dump <file> <channel> [-c COUNT] [-b BYTEOFFSET] [options]
    dump <file> <channel> --bin [options]
    dump <file> <channel> -p [options]
    -c COUNT, --count COUNT  Number of bytes to show.
    -b BYTEOFFSET, --byteoffset BYTEOFFSET  Offset into message.
    --bin, --binary  Output in raw binary format (useful for exporting video).
    -p, --pcap  Output in PCAP format (ethernet only).
    """

    # Convert int args.
    for arg in ('--count', '--byteoffset', '<channel>'):
        if args.get(arg):
            args[arg] = int(args[arg])

    # Iterate over packets based on args.
    last_time = None
    with FileProgress(args['<file>']) as progress:
        if sys.stdout.isatty():
            progress.close()

        if args['--pcap']:
            writer = Writer(sys.stdout.buffer)

        for packet in C10(args['<file>']):
            progress.update(packet.packet_length)

            if packet.data_type == 0x11:
                last_time = packet

            elif packet.channel_id == args['<channel>']:
                if packet.data_type == 1:
                    yield from packet.data.decode().splitlines()
                    return

                for msg in packet:
                    rtc = getattr(msg, 'ipts', packet.rtc)

                    # Raw binary
                    if args['--binary']:
                        # Byteswap video data
                        if packet.data_type in (64, 65, 66, 67, 68):
                            ts = array('H', msg.data)
                            ts.byteswap()
                            sys.stdout.buffer.write(ts.tobytes())
                        else:
                            sys.stdout.buffer.write(msg.data)

                    # PCAP
                    elif args['--pcap']:
                        data = msg.data

                        # Format 0 (MAC payload), msg.content 1 = payload only
                        if packet.data_type == 0x68 and msg.content:
                            data = Ethernet(
                                data=data,
                                len=len(data),
                                dst=bytes(),
                                src=bytes()
                            ).pack()

                        # Format 1 (UDP/ARINC 664)
                        elif packet.data_type == 0x69:
                            udp = UDP(sport=msg.src_port,
                                      dport=msg.dst_port,
                                      data=data)
                            ip = IP(data=udp,
                                    len=len(udp),
                                    v=4,
                                    p=17,
                                    src=struct.pack('>L', msg.source_ip),
                                    dst=struct.pack('>L', msg.dest_ip)).pack()
                            data = Ethernet(
                                data=ip,
                                len=len(ip),
                                dst=struct.pack('>IH', 50331648,
                                                msg.virtual_link),
                                src=bytes()
                            ).pack()

                        writer.writepkt(data,
                                        get_time(rtc, last_time).timestamp())
                        sys.stdout.flush()

                    # Hex dump
                    else:
                        data_bytes = msg.data[
                            args['--byteoffset']:args['--count']]
                        yield ' '.join([str(get_time(rtc, last_time))] + [
                            f'{b:02x}'.zfill(2) for b in data_bytes])
