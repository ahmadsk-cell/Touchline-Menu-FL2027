"""Exercise the real installer and restore scripts in disposable fake Sider folders."""
import hashlib,json,struct,subprocess,unittest,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'test-output'/uuid.uuid4().hex
MANIFEST=json.loads((ROOT/'manifest.json').read_text())

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)

def executable_fixture():
    """A tiny PE64 with a complete palette, for installer preflight only."""
    data=bytearray(1024)
    data[:2]=b'MZ';struct.pack_into('<I',data,0x3c,0x80)
    data[0x80:0x84]=b'PE\0\0'
    struct.pack_into('<HH',data,0x84,0x8664,1)
    struct.pack_into('<H',data,0x94,0xf0)
    struct.pack_into('<H',data,0x98,0x20b)
    data[0x188:0x190]=b'.data\0\0\0'
    struct.pack_into('<IIII',data,0x190,512,0x1000,512,512)
    data[0x200:0x20c]=bytes.fromhex('101010ffffffffff004493ff')
    return data
def snapshot(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and 'TouchlineMenu-backups' not in p.parts}
def ps(script,*args):
    return subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),*map(str,args)],capture_output=True,text=True)

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.game=RUN/self._testMethodName/'SiderAddons'
        put(self.game/'sider.ini',b'[sider]\r\n; user settings\r\nlivecpk.enabled = 1\r\nlua.enabled = 1\r\n')
        put(self.game.parent/'FL_2027.exe',executable_fixture())
        put(self.game/'livecpk/Unrelated/example.bin',b'preserve this other mod')

    def install(self):
        result=ps(ROOT/'Install.ps1','-SiderDir',self.game)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return sorted((self.game/'TouchlineMenu-backups').iterdir())[-1]

    def restore(self,backup):return ps(ROOT/'Uninstall.ps1','-SiderDir',self.game,'-BackupDirectory',backup)

    def test_fresh_install_and_restore(self):
        before=snapshot(self.game);backup=self.install()
        for entry in MANIFEST['files']:self.assertEqual(sha(self.game/entry['path']),entry['sha256'])
        ini=(self.game/'sider.ini').read_text()
        self.assertIn('cpk.root = ".\\livecpk\\TouchlinePrologue2"',ini)
        self.assertIn('lua.module = "TouchlineMenuColors.lua"',ini)
        self.assertFalse((self.game/'livecpk/MenuC1987').exists())
        self.assertFalse((self.game/'modules/UIColors.lua').exists())
        result=self.restore(backup);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(snapshot(self.game),before)

    def test_upgrade_preserves_existing_files_in_backup(self):
        target=self.game/'livecpk/TouchlinePrologue2/common/menu/general/schedule.bin'
        put(target,b'previous working schedule')
        put(self.game/'modules/UIColors.lua',b'-- user original module\n')
        put(self.game/'content/ui-colors/map_exe.txt',b'original shared palette')
        put(self.game/'livecpk/MenuC1987/preserve.bin',b'original pack')
        put(self.game/'livecpk/UIColors/preserve.bin',b'original colors')
        ini=self.game/'sider.ini';put(ini,ini.read_bytes()+b'cpk.root = ".\\livecpk\\TouchlinePrologue2"\r\ncpk.root = ".\\livecpk\\MenuC1987"\r\ncpk.root = ".\\livecpk\\UIColors"\r\nlua.module = "UIColors.lua"\r\n')
        before=snapshot(self.game);backup=self.install()
        self.assertEqual((self.game/'sider.ini').read_text().count('TouchlinePrologue2'),1)
        active=[line for line in (self.game/'sider.ini').read_text().splitlines() if not line.lstrip().startswith(';')]
        self.assertFalse(any('MenuC1987' in line or '"UIColors.lua"' in line or 'livecpk\\UIColors' in line for line in active))
        self.assertEqual((self.game/'content/ui-colors/map_exe.txt').read_bytes(),b'original shared palette')
        result=self.restore(backup);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(snapshot(self.game),before)

    def test_restore_refuses_later_changes_without_partial_restore(self):
        backup=self.install();put(self.game/'content/touchline-menu/map_exe.txt',b'later user change')
        before=snapshot(self.game);result=self.restore(backup)
        self.assertNotEqual(result.returncode,0);self.assertIn('Changed since installation',result.stderr)
        self.assertEqual(snapshot(self.game),before)

    def test_unknown_retired_override_is_preserved(self):
        put(self.game/'livecpk/TouchlinePrologue2/common/menu/parts/teamPower.bin',b'user-owned modification')
        before=snapshot(self.game);result=ps(ROOT/'Install.ps1','-SiderDir',self.game)
        self.assertNotEqual(result.returncode,0);self.assertIn('independently edited',result.stderr)
        self.assertEqual(snapshot(self.game),before)

    def test_corrupt_payload_rejected_before_install(self):
        package=RUN/'corrupt-package'
        for name in ['Install.ps1','scripts/Common.ps1','scripts/Check-FL2027.ps1']:put(package/name,(ROOT/name).read_bytes())
        entry=dict(MANIFEST['files'][0]);put(package/entry['path'],b'corrupt')
        put(package/'manifest.json',json.dumps({'version':'test','files':[entry],'retired':[]}).encode())
        before=snapshot(self.game);result=ps(package/'Install.ps1','-SiderDir',self.game)
        self.assertNotEqual(result.returncode,0);self.assertIn('checksum failed',result.stderr)
        self.assertEqual(snapshot(self.game),before)
        self.assertFalse((self.game/'TouchlineMenu-backups').exists())

    def test_fl2027_stock_palette_module_disabled_and_restored(self):
        ini=self.game/'sider.ini'
        put(ini,ini.read_bytes()+b'lua.module = "switcher\\SPcolor.lua"\r\nlua.module = "switcher\\SPclassics.lua"\r\nlua.module = "MLRuntime.lua"\r\nlua.module = "common\\movieintro.lua"\r\n')
        before=snapshot(self.game);backup=self.install()
        active=[line for line in ini.read_text().splitlines() if not line.lstrip().startswith(';')]
        self.assertFalse(any('SPcolor.lua' in line for line in active))
        for name in ['SPclassics.lua','MLRuntime.lua','common\\movieintro.lua']:
            self.assertTrue(any(name in line for line in active))
        self.assertTrue((self.game/'livecpk/TouchlinePrologue2/movie/intro/FL2027.usm').is_file())
        self.assertFalse((self.game/'livecpk/TouchlinePrologue2/movie/intro/FL2026.usm').exists())
        result=self.restore(backup);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(snapshot(self.game),before)

    def test_unsupported_executable_rejected_before_install(self):
        data=executable_fixture();data[0x200]=0
        put(self.game.parent/'FL_2027.exe',data)
        before=snapshot(self.game)
        result=ps(ROOT/'Install.ps1','-SiderDir',self.game)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('supported UI palette',result.stderr)
        self.assertEqual(snapshot(self.game),before)
        self.assertFalse((self.game/'TouchlineMenu-backups').exists())

if __name__=='__main__':unittest.main(verbosity=2)
