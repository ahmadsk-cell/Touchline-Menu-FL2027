"""Verify and package the curated repository with Python's standard library."""
import argparse
import hashlib,json
import struct
import zlib
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from prepare_english import records, unpack


def classic_strings(source):
    original = unpack(source)
    count, table = struct.unpack_from('<II', original)
    groups = [struct.unpack_from('<III', original, table+i*12) for i in range(count)]
    group = next(i for i, (start, _, _) in enumerate(groups)
                 if struct.unpack_from('<I', original, start+4)[0] == 11)
    start, size, name = groups[group]
    entries = struct.unpack_from('<I', original, start)[0]
    end_of_records = 8+12*entries
    label, key = b'Prologue\0', 423
    bank = bytearray(original[start:start+size])
    struct.pack_into('<I',bank,0,entries+1)
    for i in range(entries):
        record = 8+i*12
        offset = struct.unpack_from('<I',bank,record+8)[0]
        assert offset >= end_of_records
        struct.pack_into('<I',bank,record+8,offset+12)
    bank[end_of_records:end_of_records] = struct.pack('<IHHI',key,len(label),len(label)-1,size+12)
    bank.extend(label)
    delta = (len(bank)-size+15)&~15
    data = bytearray(original[:start]+bank+bytes(delta-(len(bank)-size))+original[start+size:])
    for i,(offset,length,key_name) in enumerate(groups):
        struct.pack_into('<III',data,table+i*12,offset+(delta if offset>start else 0),
                         len(bank) if i==group else length,key_name)
    before,after = records(original),records(data)
    assert (name,key) not in before
    assert after.pop((name,key)) == (len(label)-1,label)
    assert after == before
    compressed = zlib.compress(data,9)
    return source[:8]+struct.pack('<II',len(compressed),len(data))+compressed

ROOT=Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--classic', action='store_true', help='Package the Classic edition.')
args = parser.parse_args()
manifest=json.loads((ROOT/'manifest.json').read_text())
english_strings = 'livecpk/TouchlinePrologue2/eng/string/all.str'
if args.classic:
    manifest['edition'] = 'classic'
    manifest['files'] = [entry for entry in manifest['files']
                         if not entry['path'].startswith('modules/TouchlineMLDashboard')]
    for relative in ('modules/TouchlineClassicLauncher.lua', 'modules/TouchlineClassicML.bin'):
        asset = ROOT / relative
        manifest['files'].append({'path': relative,
                                  'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(),
                                  'size': asset.stat().st_size})
files=[]
for entry in manifest['files']:
    p=(ROOT/entry['path']).resolve()
    assert p.is_relative_to(ROOT),entry['path']
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],entry['path']
    assert p.stat().st_size==entry['size'],entry['path']
    files.append(p)
for name in ['README.md','CREDITS.md','CHANGELOG.md','Install.cmd','Install.ps1','Uninstall.ps1','manifest.json','VERIFICATION.json','DEPENDENCY-AUDIT.json']:
    files.append(ROOT/name)
files.extend(ROOT/name for name in ['docs/compatibility-fl2027.md','docs/FL2026-VERIFICATION.json'])
# Only what installs or explains the theme. Artwork masters, prompts, README
# screenshots, tests and this tool stay in the repository.
for folder in ['scripts']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
assert len(files)==len(set(files))
dist=ROOT/'dist';dist.mkdir(exist_ok=True)
out=dist/f"Touchline-Menu-FL2027-v{manifest['version']}.zip"
if args.classic:
    out=out.with_name(f'{out.stem}-classic-midnight-preview.zip')
    translated = classic_strings((ROOT/english_strings).read_bytes())
    entry = next(item for item in manifest['files'] if item['path']==english_strings)
    entry.update(sha256=hashlib.sha256(translated).hexdigest(),size=len(translated))
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):
        if args.classic and p.name=='manifest.json':
            z.writestr('manifest.json', json.dumps(manifest,indent=2)+'\n')
        elif args.classic and p.name=='README.md':
            z.write(ROOT/'docs/classic-edition.md','README.md')
        elif args.classic and p.name=='VERIFICATION.json':
            continue
        elif args.classic and p.relative_to(ROOT).as_posix()==english_strings:
            z.writestr(english_strings,translated)
        else:
            z.write(p,p.relative_to(ROOT).as_posix())
with ZipFile(out) as z:
    assert z.testzip() is None
    for entry in manifest['files']:
        assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
checksum=hashlib.sha256(out.read_bytes()).hexdigest()
sums_name = 'SHA256SUMS-classic-midnight-preview.txt' if args.classic else 'SHA256SUMS.txt'
(dist/sums_name).write_text(f'{checksum}  {out.name}\n',encoding='ascii')
print(f'{out.name}: {out.stat().st_size:,} bytes; {len(manifest["files"])} verified payload files')
print(f'SHA-256: {checksum}')
