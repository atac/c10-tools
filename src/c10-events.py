#!/usr/bin/env python

import sys

from chapter10 import C10


def main():
    if len(sys.argv) < 2:
        print 'usage: c10-events <input_file>'

    for packet in C10(sys.argv[-1]):
        if packet.data_type == 0x2:
            print 'Recording Event packet at %s' % packet.rtc
            for i, entry in enumerate(packet.body):
                print '    %s of %s at %s' % (
                    i + 1, packet.body.recording_event_entry_count,
                    entry.intra_packet_timestamp)
                print '    Occurrence: %s' % entry.event_occurrence
                print '    Count: %s' % entry.event_count
                print '    Number: %s' % entry.event_number
                print


if __name__ == '__main__':
    main()
