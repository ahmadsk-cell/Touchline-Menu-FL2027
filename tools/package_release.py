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


def localized_strings(source, replacements):
    """Replace approved records while retaining all other stock strings."""
    original = unpack(source)
    count, table = struct.unpack_from('<II', original)
    groups = [struct.unpack_from('<III', original, table + i * 12) for i in range(count)]
    before = records(original)
    expected = {}
    by_group = {}
    for group, key, english, translated in replacements:
        assert (group, key) not in expected
        assert before[group, key][1] == english.encode('ascii') + b'\0', (group, key, english)
        replacement = translated.encode('ascii') + b'\0'
        expected[group, key] = (len(replacement) - 1, replacement)
        by_group.setdefault(group, {})[key] = replacement

    data = bytearray()
    previous_end = 0
    directory = []
    for start, size, group in groups:
        assert start >= previous_end, group
        data.extend(original[previous_end:start])
        offset = len(data)
        bank = bytearray(original[start:start + size])
        if group in by_group:
            entries = struct.unpack_from('<I', bank)[0]
            for index in range(entries):
                record = 8 + 12 * index
                key = struct.unpack_from('<I', bank, record)[0]
                replacement = by_group[group].get(key)
                if replacement is not None:
                    struct.pack_into('<HHI', bank, record + 4, len(replacement), len(replacement) - 1, len(bank))
                    bank.extend(replacement)
        data.extend(bank)
        # Preserve the alignment of every group that follows this bank.
        data.extend(bytes((size - len(bank)) % 16))
        directory.append((offset, len(bank), group))
        previous_end = start + size
    data.extend(original[previous_end:])
    for index, entry in enumerate(directory):
        struct.pack_into('<III', data, table + index * 12, *entry)
    assert records(data) == before | expected
    compressed = zlib.compress(data, 9)
    return source[:8] + struct.pack('<II', len(compressed), len(data)) + compressed


ROOT=Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
edition = parser.add_mutually_exclusive_group()
edition.add_argument('--classic', action='store_true', help='Package the Classic edition.')
edition.add_argument('--locale', choices=('es', 'fr', 'ar', 'it', 'pt-br', 'ru', 'id', 'tr'),
                     help='Package a localized dashboard.')
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
if args.locale in ('ar', 'ru', 'tr'):
    # Let these locales render native text using the game's own fonts. Known
    # Touchline overrides are backed up and removed when upgrading.
    stock_text_fonts = {
        'LPsm_fnt.bin', 'XLPsm_fnt.bin', 'matchBold_fnt.bin',
        'match_fnt.bin', 'pes_fnt.bin', 'plname_fnt.bin',
    }
    overrides = [entry for entry in manifest['files']
                 if Path(entry['path']).name in stock_text_fonts]
    assert {Path(entry['path']).name for entry in overrides} == stock_text_fonts
    for entry in overrides:
        manifest['retired'].append({'path': entry['path'], 'known_sha256': [entry['sha256']]})
    manifest['files'] = [entry for entry in manifest['files'] if entry not in overrides]
files=[]
localized = {}
for entry in manifest['files']:
    p=(ROOT/entry['path']).resolve()
    assert p.is_relative_to(ROOT),entry['path']
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],entry['path']
    assert p.stat().st_size==entry['size'],entry['path']
    files.append(p)
if args.locale:
    locale_root = ROOT/'locales'/args.locale
    names = (
        'livecpk/TouchlinePrologue2/common/menu/general/topModeSelectDMM.bin',
        'modules/TouchlineMLDashboard.lua',
        'modules/TouchlineMLDashboard/modeMainMenuFl.bin',
        'modules/TouchlineMLDashboard/modeMainMenuBAL.bin',
    )
    localized = {name: (locale_root/Path(name).name).read_bytes() for name in names}
    if args.locale == 'id':
        overrides = json.loads((locale_root/'english-labels.json').read_text(encoding='utf-8'))
        localized[english_strings] = localized_strings((ROOT/english_strings).read_bytes(), overrides)
    for entry in manifest['files']:
        data = localized.get(entry['path'])
        if data is not None:
            entry.update(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
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
elif args.locale:
    out=out.with_name(f'{out.stem}-{args.locale}-preview.zip')
    guidance = {
        'es': 'Selecciona **Español** como idioma del texto en los ajustes del juego.\n\n',
        'fr': 'Sélectionnez **Français** comme langue des textes dans les paramètres du jeu.\n\n',
        'it': (
            '# Touchline Menu — Anteprima italiana\n\n'
            'Chiudi FL 2027 e Sider. Estrai tutto il contenuto dello ZIP, avvia **Install.cmd** '
            'e seleziona la cartella **SiderAddons** che contiene `sider.ini`. Avvia il gioco '
            'e imposta **Italiano** come lingua dei testi.\n\n'
            'Per disinstallare, chiudi il gioco e Sider e segui le [istruzioni di ripristino]'
            '(#restore-the-previous-setup).\n\n'
        ),
        'pt-br': (
            '# Touchline Menu — Prévia em português do Brasil\n\n'
            'Feche o FL 2027 e o Sider. Extraia todo o conteúdo do ZIP, execute **Install.cmd** '
            'e selecione a pasta **SiderAddons** que contém o arquivo `sider.ini`. Inicie o jogo '
            'e selecione **Português do Brasil** como idioma dos textos.\n\n'
            'Para desinstalar, feche o jogo e o Sider e siga as [instruções de restauração]'
            '(#restore-the-previous-setup).\n\n'
        ),
        'ru': (
            '# Touchline Menu — Русская версия (предварительная)\n\n'
            'Закройте FL 2027 и Sider. Полностью распакуйте ZIP, запустите **Install.cmd** '
            'и выберите папку **SiderAddons** с файлом `sider.ini`. Запустите игру '
            'и выберите **Русский** в настройках языка текста.\n\n'
            'Для удаления закройте игру и Sider, затем следуйте [инструкции по восстановлению]'
            '(#restore-the-previous-setup).\n\n'
        ),
        'id': (
            '# Touchline Menu — Pratinjau Bahasa Indonesia\n\n'
            'Tutup FL 2027 dan Sider. Ekstrak seluruh isi ZIP, jalankan **Install.cmd**, '
            'lalu pilih folder **SiderAddons** yang berisi `sider.ini`. Setelah memulai game, '
            'pilih **English** sebagai bahasa teks.\n\n'
            'Pratinjau ini menerjemahkan menu utama Touchline, dasbor Liga Master dan Jadi Legenda, '
            'serta beberapa label bawaan. Dialog dan teks game lainnya tetap berbahasa Inggris.\n\n'
            'Untuk menghapus mod, tutup game dan Sider, lalu ikuti [petunjuk pemulihan]'
            '(#restore-the-previous-setup).\n\n'
        ),
        'tr': (
            '# Touchline Menu — Türkçe önizleme\n\n'
            'FL 2027 ve Sider’ı kapatın. ZIP dosyasının tamamını çıkarın, **Install.cmd** dosyasını '
            'çalıştırın ve `sider.ini` dosyasını içeren **SiderAddons** klasörünü seçin. Oyunu başlatın '
            've metin dili olarak **Türkçe** seçin.\n\n'
            'Modu kaldırmak için oyunu ve Sider’ı kapatıp [geri yükleme adımlarını]'
            '(#restore-the-previous-setup) izleyin.\n\n'
        ),
        'ar': (
            '# Touchline Menu — النسخة العربية التجريبية\n\n'
            'أغلق اللعبة وبرنامج Sider، ثم فك ضغط الملف بالكامل وشغّل **Install.cmd**. '
            'اختر مجلد **SiderAddons** الذي يحتوي على ملف `sider.ini`. '
            'بعد تشغيل اللعبة، اختر **العربية** كلغة للنص من إعدادات اللغة.\n\n'
            'تتضمن هذه النسخة القوائم الرئيسية ولوحتي الدوري الاحترافي وكن أسطورة باللغة العربية. '
            'تستخدم القوائم والحوارات الأصلية ترجمة اللعبة وخطوطها.\n\n'
            'لإلغاء التثبيت، أغلق اللعبة وبرنامج Sider واستخدم **Uninstall.ps1** مع مجلد **SiderAddons** '
            'ومسار النسخة الاحتياطية الذي عرضه المثبّت. [خطوات الاستعادة](#restore-the-previous-setup).\n\n'
        ),
    }
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    locale_details = {
        'ar': ('العربية', 'arabic', 'Stock Arabic localization and text fonts'),
        'it': ('Italiano', 'italian', 'Stock game localization for built-in dialogs and submenus'),
        'pt-br': ('Português do Brasil', 'brazilian_portuguese', 'Stock game localization for built-in dialogs and submenus'),
        'ru': ('Русский', 'russian', 'Stock Russian localization and text fonts'),
        'id': ('English', 'indonesian', 'Selected labels in the English language slot'),
        'tr': ('Türkçe', 'turkish', 'Stock Turkish localization and text fonts'),
    }
    if args.locale in locale_details:
        language, name, game_text = locale_details[args.locale]
        readme = readme.replace('English game text. This package includes an English string-table override.',
                                f'Select **{language}** in the game’s text language settings.')
        verification = json.loads((ROOT/'VERIFICATION.json').read_text(encoding='utf-8'))
        verification[f'{name}_preview'] = {
            'artwork': 'Seven main menu scenes and both career dashboards',
            'game_text': game_text,
            'routing': 'Passed simulated Sider checks with the FL 2027 executable',
            'in_game_rendering': 'Pending',
        }
        localized['VERIFICATION.json'] = (json.dumps(verification, indent=2)+'\n').encode('utf-8')
    localized['README.md'] = (guidance[args.locale] + readme).encode('utf-8')
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):
        relative = p.relative_to(ROOT).as_posix()
        if (args.classic or args.locale) and relative=='manifest.json':
            z.writestr('manifest.json', json.dumps(manifest,indent=2)+'\n')
        elif relative in localized:
            z.writestr(relative, localized[relative])
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
sums_name = ('SHA256SUMS-classic-midnight-preview.txt' if args.classic else
             f'SHA256SUMS-{args.locale}-preview.txt' if args.locale else 'SHA256SUMS.txt')
(dist/sums_name).write_text(f'{checksum}  {out.name}\n',encoding='ascii')
print(f'{out.name}: {out.stat().st_size:,} bytes; {len(manifest["files"])} verified payload files')
print(f'SHA-256: {checksum}')
