
import socket

import matplotlib.pyplot as plt

from c10_tools.common import C10


class Parser:

    def __init__(self, buffer_size=100000):
        self.buffer_size = buffer_size
        self.buf = bytes()

    def parse(self, data):
        """Take a bytes object and attempt to parse chapter 10 data into db."""

        # Limit the buffer size and add new data to the buffer.
        self.buf = self.buf[-self.buffer_size:] + data

        sync_count = self.buf.count(b'\x25\xeb')
        for i in range(sync_count):

            sync = self.buf.find(b'\x25\xeb')
            if sync < 0:
                break

            try:
                for packet in C10.from_string(self.buf[sync:]):
                    yield packet
                continue
            except:
                pass

            if i < (sync_count - 2):
                self.buf = self.buf[sync + 2:]


def main(args):
    """Plot data density of a channel in a Chapter 10 stream. Requires matplotlib.
    streamcheck <dsthost> <dstport> <channel>
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args['<dsthost>'], int(args['<dstport>'])))

    parser = Parser()
    channel = int(args['<channel>'])
    last_rtc = 0

    maxlength = 100
    plot = [0 for i in range(maxlength)]
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    while True:
        try:
            raw, addr = sock.recvfrom(1048576)
            for packet in parser.parse(raw[4:]):

                if packet.channel_id == channel:
                    offset = (packet.rtc - last_rtc) & 0xffffffffffff
                    seconds = offset / 10_000_000
                    if not seconds:
                        continue
                    last_rtc = packet.rtc
                    density = packet.data_length / seconds
                    plot.append(density)
                    plot = plot[-maxlength:]
                    ax1.clear()
                    ax1.plot(range(len(plot)), plot)
                    plt.pause(0.1)
        except KeyboardInterrupt:
            print('Stopped')
            break
