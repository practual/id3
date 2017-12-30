#! /usr/bin/env python

# http://id3.org/id3v2.3.0

import argparse

from bitstring import BitArray


parser = argparse.ArgumentParser()
parser.add_argument('path')
args = parser.parse_args()


def to_string(byte_data):
    return byte_data.decode('ascii')


def to_integer(byte_data):
    return int.from_bytes(byte_data, byteorder='big')


v2_format = [
    ('identifier', 3, to_string),
    ('minor version', 1, to_integer),
    ('revision', 1, to_integer),
    ('flags', 1, to_integer),
    ('size', 4, lambda x: x),
]


def process_size(naive_size):
    # The most significant bit of each byte is ignored.
    bits = [bit for i, bit in enumerate(BitArray(naive_size).bin) if i % 8]
    return int(''.join(bits), 2)


fsock = open(args.path, 'rb', 0)
try:
    tags = {}
    for tag_name, num_bytes, byte_map in v2_format:
        data = byte_map(fsock.read(num_bytes))
        tags[tag_name] = data
    tags['size'] = process_size(tags['size'])
    frame_data = fsock.read(tags['size'])
finally:
    fsock.close()

frames = []
pointer = 0
while pointer < len(frame_data):
    frame_id = to_string(frame_data[pointer:pointer + 4])
    pointer += 4
    size = to_integer(frame_data[pointer:pointer + 4])
    pointer += 4
    flags = frame_data[pointer:pointer + 2]
    pointer += 2
    contents = frame_data[pointer:pointer + size]
    pointer += size
    frames.append({
        'id': frame_id,
        'size': size,
        'flags': flags,
        'contents': contents,
    })
