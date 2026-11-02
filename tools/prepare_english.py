"""Keep FL 2027's English strings, correcting only 'Choose Sqad Type'.

Supply the extracted eng/string/all.str from your FL 2027 game. No executable,
save files or extraction tools are distributed by this script.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path


def unpack(data):
    return zlib.decompress(data[16:]) if data[3:8] == b'WESYS' else data


def records(data):
    count, table = struct.unpack_from('<II', data)
    result = {}
    for i in range(count):
        start, size, group = struct.unpack_from('<III', data, table+i*12)
        total = struct.unpack_from('<I', data, start)[0]
        for j in range(total):
            key, length, chars, offset = struct.unpack_from('<IHHI', data, start+8+j*12)
            assert offset+length <= size, (group, key)
            result[(group, key)] = (chars, data[start+offset:start+offset+length])
    return result


def prepare(source, target):
    original = unpack(source.read_bytes())
    assert b'Football Life 2027\0' in original, 'Use the FL 2027 text table'
    old, new = b'Choose Sqad Type\0', b'Choose Squad Type\0'
    assert original.count(old) == 1
    data = bytearray(original)
    pos = data.index(old)
    count, table = struct.unpack_from('<II', data)
    groups = [struct.unpack_from('<III', data, table+i*12) for i in range(count)]
    group = next(i for i, (p,n,k) in enumerate(groups) if p <= pos < p+n)
    p,n,k = groups[group]
    entries = struct.unpack_from('<I', data, p)[0]
    record = next(p+8+j*12 for j in range(entries) if struct.unpack_from('<I', data, p+8+j*12+8)[0] == pos-p)
    assert struct.unpack_from('<H', data, record+4)[0] == len(old)
    delta = (len(new)+15)&~15
    data[p+n:p+n] = new+b'\0'*(delta-len(new))
    struct.pack_into('<HHI', data, record+4, len(new), len(new)-1, n)
    for i,(off,size,key) in enumerate(groups):
        struct.pack_into('<III', data, table+i*12, off+(delta if off>p else 0), size+(len(new) if i==group else 0), key)
    before, after = records(original), records(data)
    assert before.keys() == after.keys()
    changes = [key for key in before if before[key] != after[key]]
    assert len(changes) == 1
    assert before[changes[0]][1] == old and after[changes[0]][1] == new
    compressed = zlib.compress(data,9)
    target.write_bytes(b'\x00\x10\x01WESYS'+struct.pack('<II',len(compressed),len(data))+compressed)
    assert records(unpack(target.read_bytes())) == after
    return {'source':'FL 2027 dt20_eng_x64.cpk: eng/string/all.str',
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'records_preserved':len(before)-1,'records_changed':1,
            'change':'Choose Sqad Type -> Choose Squad Type',
            'all_other_records_byte_exact':True}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    print(json.dumps(prepare(args.source,root/'livecpk/TouchlinePrologue2/eng/string/all.str'),indent=2))
