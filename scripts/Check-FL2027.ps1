$ErrorActionPreference='Stop'
function Test-FL2027Executable([string]$Path) {
    if(!(Test-Path -LiteralPath $Path -PathType Leaf)){throw 'FL_2027.exe was not found beside SiderAddons. Select the FL 2027 SiderAddons folder.'}
    if(!('TouchlineFL2027.Probe' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.IO;
namespace TouchlineFL2027 {
    public static class Probe {
        public static long PaletteRva(string path) {
            using (var reader = new BinaryReader(File.OpenRead(path))) {
                if (reader.ReadUInt16() != 0x5a4d) throw new InvalidDataException("Not a Windows executable.");
                reader.BaseStream.Position = 0x3c;
                uint pe = reader.ReadUInt32();
                if (pe > reader.BaseStream.Length - 24) throw new InvalidDataException("Invalid PE header.");
                reader.BaseStream.Position = pe;
                if (reader.ReadUInt32() != 0x4550 || reader.ReadUInt16() != 0x8664) throw new InvalidDataException("FL 2027 requires a 64-bit PE executable.");
                ushort sections = reader.ReadUInt16();
                reader.BaseStream.Position = pe + 20;
                ushort optionalSize = reader.ReadUInt16();
                reader.BaseStream.Position = pe + 24;
                if (reader.ReadUInt16() != 0x20b) throw new InvalidDataException("Unsupported PE format.");
                byte[] signature = {0x10,0x10,0x10,0xff,0xff,0xff,0xff,0xff,0x00,0x44,0x93,0xff};
                int hits = 0; long found = 0;
                for (int s = 0; s < sections; s++) {
                    reader.BaseStream.Position = pe + 24 + optionalSize + 40L*s;
                    string name = System.Text.Encoding.ASCII.GetString(reader.ReadBytes(8)).TrimEnd('\0');
                    reader.ReadUInt32(); uint rva = reader.ReadUInt32(); uint size = reader.ReadUInt32(); uint offset = reader.ReadUInt32();
                    if (name != ".data") continue;
                    if (size > 64*1024*1024 || (long)offset + size > reader.BaseStream.Length) throw new InvalidDataException("Invalid palette section.");
                    reader.BaseStream.Position = offset; byte[] data = reader.ReadBytes((int)size);
                    for (int i = 0; i <= data.Length - 80*4; i++) {
                        if (data[i] != signature[0]) continue;
                        int j = 1; while (j < signature.Length && data[i+j] == signature[j]) j++;
                        if (j == signature.Length) { hits++; found = rva + (long)i; }
                    }
                }
                if (hits != 1) throw new InvalidDataException("Expected one supported UI palette in FL_2027.exe; found " + hits + ". This build requires a compatibility check.");
                return found;
            }
        }
    }
}
'@
    }
    $rva=[TouchlineFL2027.Probe]::PaletteRva($Path)
    Write-Output ('FL 2027 UI palette verified at RVA 0x{0:X}.' -f $rva)
}
