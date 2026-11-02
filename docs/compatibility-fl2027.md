# FL 2027 compatibility

This release targets SP Football Life 2027, installed game version 27.1.0,
using the supplied FL_2027.exe (Windows file version 27.0.0.0).

## Changes from Touchline Menu 1.1.6

- The startup movie is named `movie/intro/FL2027.usm`. That path exists in
  FL 2027's dt00_x64.cpk and is referenced by its executable. The movie content
  is unchanged; it has not been re-encoded.
- The stock `switcher/SPcolor.lua` writes green into palette entries 75, 76,
  78 and 79. The installer comments out that module so the Touchline palette
  remains consistent. Uninstall restores the prior configuration.
- English strings come from FL 2027's dt20_eng_x64.cpk. Only the spelling of
  “Choose Squad Type” is edited; all 16,478 other records are byte-exact.
- Before changing the target installation, the installer checks PE64 format
  and exactly one supported UI palette signature with space for all 80 entries.
  It does not modify FL_2027.exe on disk.

## Evidence and test scope

The inspected executable has SHA-256
`327c6df6c485f4993111f3dbb84315b49447aba5b120caf4267d7a0324983454`.
Its palette signature resolves to RVA `0x34C08D0`. The title-screen layout
has SHA-256 `e2321ea64cd659b5641f58d695d823eba23ca10151175e74304a8d4f7e7d266f`
and is byte-identical to the previously inspected FL 2026 layout.

A live Sider session reported all 80 palette assignments, “Patching complete”
and successful initialization of TouchlineMenuColors.lua. The title screen
filled the screen correctly, the portrait main menu rendered, and the career
load list, information background and Game Plan screen rendered with the theme.
The final English-table update was checked by parsing every string record.
Intro-path verification is static; complete movie playback was not observed.
The final normal-launcher session confirmed the corrected native “Game Version: 1.0”
label and successful palette initialization in a fresh Sider log. Start the game
through the usual FL 2027 shortcut with Sider active.

The installer and restoration tests cover fresh installation, upgrades,
restoring earlier files, preserving subsequent edits, rejecting corrupted
payloads, rejecting unsupported executables, and disabling/restoring the stock
palette module. The LuaJIT test verifies palette initialization and reload in
simulated memory.

These checks do not cover every competition, season, career action or third-party
menu server. Competition-specific menu packs can replace default visuals.
VirtuaRed/UML and other Football Life releases are outside this build's scope.

## Development checks

Run `python -m unittest discover -s tests -v` with Python 3 and `lupa` installed.
Installer tests require Windows PowerShell. Test executables are small PE
fixtures, not copies of the game. Run `python tools/package_release.py` to check
the manifest, build the ZIP and verify its CRC and every payload hash.

`tools/prepare_english.py` accepts an extracted FL 2027 English string table and
reapplies the single spelling correction, verifying all other records unchanged.
