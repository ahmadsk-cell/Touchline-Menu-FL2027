"""Verify and package the curated repository with Python's standard library."""
import argparse
import hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--classic', action='store_true', help='Package the Classic edition.')
args = parser.parse_args()
manifest=json.loads((ROOT/'manifest.json').read_text())
if args.classic:
    manifest['edition'] = 'classic'
    manifest['files'] = [entry for entry in manifest['files']
                         if not entry['path'].startswith('modules/TouchlineMLDashboard')]
    launcher = ROOT / 'modules/TouchlineClassicLauncher.lua'
    manifest['files'].append({'path': launcher.relative_to(ROOT).as_posix(),
                              'sha256': hashlib.sha256(launcher.read_bytes()).hexdigest(),
                              'size': launcher.stat().st_size})
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
    out=out.with_name(f'{out.stem}-classic-preview.zip')
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):
        if args.classic and p.name=='manifest.json':
            z.writestr('manifest.json', json.dumps(manifest,indent=2)+'\n')
        elif args.classic and p.name=='README.md':
            z.write(ROOT/'docs/classic-edition.md','README.md')
        elif args.classic and p.name=='VERIFICATION.json':
            continue
        else:
            z.write(p,p.relative_to(ROOT).as_posix())
with ZipFile(out) as z:
    assert z.testzip() is None
    for entry in manifest['files']:
        assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
checksum=hashlib.sha256(out.read_bytes()).hexdigest()
sums_name = 'SHA256SUMS-classic.txt' if args.classic else 'SHA256SUMS.txt'
(dist/sums_name).write_text(f'{checksum}  {out.name}\n',encoding='ascii')
print(f'{out.name}: {out.stat().st_size:,} bytes; {len(manifest["files"])} verified payload files')
print(f'SHA-256: {checksum}')
