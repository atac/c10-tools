
-- This script is a dissector for wireshark that allows inspecting chapter 10
-- data within a network capture.
--
-- Installation:
-- Windows: Add to <USER_DIR>\AppData\Roaming\Wireshark\plugins
-- OSX: Add to <USER_DIR>/.wireshark/plugins

-- Port to listen for
target_port = 2000

-- Convert a data type value to a type and format string.
data_types = {
    'Computer Generated',
    'PCM',
    'Time',
    'Mil-STD-1553',
    'Analog',
    'Discrete',
    'Message',
    'ARINC 429',
    'Video',
    'Image',
    'UART',
    'IEEE-1394',
    'Parallel',
    'Ethernet',
    'TSPI/CTS Data',
    'Controller Area Network Bus'}

function format(data_type)
    t = math.floor(tonumber(data_type) / 8.0)
    f = data_type - (t * 8)
    return string.format("%s data format %d", data_types[t + 1], f)
end


-- Declare our protocol.
chapter10_proto = Proto("c10", "Chapter 10")

-- Create a function to dissect it.
function chapter10_proto.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = "Chapter10"

    -- Ensure there is chapter 10 data in this packet.
    if tostring(buffer(4, 2)) ~= '25eb' then
        return 0
    end

    local subtree = tree:add(chapter10_proto, buffer(), "Chapter 10 Data")

    local trans = subtree:add(buffer(0, 4), "UDP Transport Header")
    local trans_raw = buffer(0, 4)
    trans:add(trans_raw(3, 1), "Version " .. trans_raw:bitfield(28, 4))
    trans:add(trans_raw(3, 1), "Message Type " .. trans_raw:bitfield(24, 4))
    trans:add(trans_raw(1, 3), "Sequence Number " .. trans_raw(1, 3):le_uint())

    -- Todo: add actual support for segmented chapter 10 packets.
    subtree = subtree:add(buffer(4), "Chapter 10 Packet")
    buffer = buffer(4)
    subtree:add(buffer(0, 2), "Sync Pattern: 0x" .. buffer(0, 2))
    subtree:add(buffer(2, 2), "Channel ID: " .. buffer(2, 2):le_int())
    subtree:add(buffer(4, 4), "Packet Length: " .. buffer(4, 4):le_int())
    subtree:add(buffer(8, 4), "Data Length: " .. buffer(8, 4):le_int())
    subtree:add(buffer(12, 1), "Header Version: " .. buffer(12, 1):le_uint())
    subtree:add(buffer(13, 1), "Sequence Number: " .. buffer(13, 1):le_uint())
    subtree:add(buffer(14, 1), "Flags: 0x" .. buffer(14, 1))
    subtree:add(buffer(15, 1), string.format("Data Type: 0x%s (%s)",
                tostring(buffer(15, 1)), format(buffer(15, 1):le_uint())))
    local rtc_low = tostring(buffer(16, 3)):reverse()
    local rtc_high = tostring(buffer(19, 3)):reverse() 
    local rtc = tonumber(rtc_high .. rtc_low, 16)
    subtree:add(buffer(16, 6), "Relative Time Counter: " .. tostring(rtc))
    subtree:add(buffer(22, 2), "Header Checksum: 0x" .. buffer(22, 2))

    -- subtree:add(buffer(0,2),"The first two bytes: " .. buffer(0,2))
    -- subtree = subtree:add(buffer(4,2),"The next two bytes")
    -- subtree:add(buffer(2,1),"The 3rd byte: " .. buffer(2,1):uint())
    -- subtree:add(buffer(3,1),"The 4th byte: " .. buffer(3,1):uint())
end

-- Register our protocol to handle an arbitrary udp port
udp_table = DissectorTable.get("udp.port")
udp_table:add(target_port, chapter10_proto)
