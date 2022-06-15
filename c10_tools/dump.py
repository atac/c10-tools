
from array import array
import struct
import sys
import os

from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.pcap import Writer
from dpkt.udp import UDP
import click

from c10_tools.common import FileProgress, C10, get_time


@click.command()
@click.argument('infile')
@click.argument('channel', type=int)
@click.option('-c', '--count', type=int, default=1000, help='Maximum number of bytes to show in hexdump mode')
@click.option('-b', '--byteoffset', type=int, default=0, help='Offset into message in hexdump mode')
@click.option('-p', '--pcap', is_flag=True, help='Output in PCAP format (ethernet data only)')
@click.option('--bin', '--binary', is_flag=True, help='Output raw binary (useful for exporting video).')
@click.pass_context
def dump(ctx, infile, channel, count, byteoffset, pcap, bin):
    """Dump hex (default), binary data, or PCAP from a Chapter 10 channel."""

    ctx.ensure_object(dict)

    # Iterate over packets based on args.
    last_time = None
    progress = None
    if not sys.stdout.isatty() and not ctx.obj.get('quiet'):
        progress = FileProgress(infile, file=sys.stderr)

    if pcap:
        writer = Writer(sys.stdout.buffer)

    for packet in C10(infile):
        if progress:
            progress.update(packet.packet_length)

        if packet.data_type == 0x11:
            last_time = packet

        if packet.channel_id != channel:
            continue

        if packet.data_type == 1:
            print(packet.data.decode())

        for msg in packet:
            msg_time = get_time(getattr(msg, 'ipts', packet.rtc), last_time)

            # Raw binary
            if bin:
                # Byteswap video data
                if packet.data_type in (64, 65, 66, 67, 68):
                    ts = array('H', msg.data)
                    ts.byteswap()
                    sys.stdout.buffer.write(ts.tobytes())
                else:
                    sys.stdout.buffer.write(msg.data)

            # PCAP
            elif pcap:
                data = msg.data

                # Format 0 (MAC payload), msg.content 1 = payload only
                if packet.data_type == 0x68 and msg.content:
                    data = Ethernet(data, len=msg.length)

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

                writer.writepkt(data, msg_time.timestamp())
                sys.stdout.flush()

            # Hex dump
            else:
                data_bytes = msg.data[byteoffset:count]
                print(' '.join([str(msg_time)] + [f'{b:02x}'.zfill(2) for b in data_bytes]))
