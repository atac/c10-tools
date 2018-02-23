#!/usr/bin/env python

from datetime import timedelta
import sys

from i106 import C10


def abs_time(rtc, time_packet):
    time_packet.body.parse()
    offset = (rtc - time_packet.rtc) / 10000000.0
    return time_packet.body.time + timedelta(seconds=offset)


def main():
    if len(sys.argv) < 2:
        print ('usage: c10-events <input_file>')

    last_time = None

    for packet in C10(sys.argv[-1]):
        if packet.data_type == 0x11:
            last_time = packet
            continue

        if packet.data_type == 0x2:
            print ('Recording Event packet at %s' % abs_time(
                packet.rtc, last_time))
            for i, entry in enumerate(packet.body):
                print ('    %s of %s at %s' % (
                    i + 1, packet.body.recording_event_entry_count,
                    abs_time(entry.intra_packet_timestamp, last_time)))
                print ('    Occurrence: %s' % entry.event_occurrence)
                print ('    Count: %s' % entry.event_count)
                print ('    Number: %s' % entry.event_number)
                print()


if __name__ == '__main__':
    main()
