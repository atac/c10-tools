#!/usr/bin/env python

import os

import click

from c10_tools.common import FileProgress, C10


@click.command()
@click.option('-b', is_flag=True, help='use the b bus instead of the default a')
@click.option('-f', '--force', is_flag=True, help='overwrite existing dst file if present')
@click.argument('src')
@click.argument('dst')
def allbus(src, dst, force=False, b=False):
    """Switch 1553 format 1 messages to indicate the same bus (a or b)."""

    if os.path.exists(dst) and not force:
        print('Destination file exists. Use --force to overwrite it.')
        raise SystemExit

    with open(dst, 'wb') as out, \
            FileProgress(src) as progress:
        for packet in C10(src):
            progress.update(packet.packet_length)

            if packet.data_type == 0x19:
                for msg in packet:
                    msg.bus = int(b)

            out.write(bytes(packet))