# Touchline Menu for FL 2027

A standalone charcoal, silver and champagne menu mod for **SP Football Life 2027**, with Touchline / Prologue branding, portrait main-menu scenes and quiet `#040B12` information screens. No separate menu pack or UIColors installation is required.

**[Download the latest release](https://github.com/ahmadsk-cell/Touchline-Menu-FL2027/releases/latest)** · [Installation](#installation) · [Credits](CREDITS.md)

![Verified FL 2027 title screen](docs/images/title-fl2027.png)

![Touchline main-menu scene](docs/images/main-menu.png)

## Included

- Main menu ordered as Kick-off, Master League, Become a Legend, MyClub, Gallery, Music & Audio, Settings.
- Seven portrait scenes and short introductions for Master League and Become a Legend.
- Dark information backgrounds with subtle smoke, fine gold lines and BootShapes branding.
- Silver-and-gold icons for the default Game Plan menu, negotiations, notifications and calendar events.
- Custom loading, saving and controlled-club indicators, plus the Touchline intro movie.
- Readability changes for league/team rows, team ratings and text-entry dialogs.
- The latest working Schedule and text-input files from the author's installation.

![Default Game Plan icons](docs/images/game-plan.png)

![Information background](docs/images/information-background.png)

## Requirements

- Windows with **SP Football Life 2027** and Sider, with LiveCPK and Lua enabled.
- English game text. This package includes an English string-table override.

All required theme files, fonts, secondary menu assets and the color component are included. Football Life and Sider themselves are not bundled. This build targets FL 2027. The installer checks for a 64-bit `FL_2027.exe` and a unique supported UI palette before changing files. PES 2021, VirtuaRed/UML and other Football Life versions are outside this release's compatibility scope.

Touchline and Prologue gameplay/story systems are separate projects. Their names appear in the menu artwork; this download installs the visual theme and intro only.

## Installation

1. Close Football Life and Sider.
2. Download **Touchline-Menu-FL2027-v2.0.0.zip** from [GitHub Releases](https://github.com/ahmadsk-cell/Touchline-Menu-FL2027/releases/latest) and extract it completely.
3. Double-click **Install.cmd** and enter the full path to your **SiderAddons** folder, the folder containing `sider.ini`.
4. Start Sider and Football Life again.

Alternatively, from PowerShell in the extracted package:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -SiderDir 'D:\SP Football Life 2027\SiderAddons'
```

Replace the example path with your installation. Administrator privileges are normally unnecessary if you can write to that folder.

The installer verifies the package, backs up affected files, enables the single `TouchlinePrologue2` LiveCPK root and the bundled `TouchlineMenuColors.lua` component. Its palette is isolated in `content/touchline-menu`.

When upgrading an existing setup, the installer comments out the old MenuC1987, UIColors and TouchlinePrologue roots and the separate `UIColors.lua` module to avoid duplicate menu/palette loading. Their files remain on disk, and uninstall restores the original settings. The stock `switcher\SPcolor.lua` module is also commented out because it overwrites four entries of the theme palette. Its file stays installed, and uninstall restores the original configuration. Other Sider settings, mods and saves are preserved.

Earlier development versions used the same `TouchlinePrologue2` folder. The installer backs them up and removes the obsolete `teamPower.bin` override only when its hash matches a known development copy. An independently edited copy is left for you to resolve.

## Restore the previous setup

Each installation prints its backup directory under `SiderAddons\TouchlineMenu-backups`. Close the game and Sider, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Uninstall.ps1 -SiderDir 'D:\SP Football Life 2027\SiderAddons' -BackupDirectory 'D:\SP Football Life 2027\SiderAddons\TouchlineMenu-backups\YOUR-BACKUP-FOLDER'
```

This restores overwritten files and settings and removes files created by that installation. It stops if a file has changed since installation, so later edits are not silently lost. Keep the extracted package and backup until you no longer need to restore them.

## Compatibility and troubleshooting

- **No visual changes:** restart both Sider and the game; confirm `TouchlinePrologue2` and `TouchlineMenuColors.lua` are enabled, with LiveCPK and Lua enabled.
- **Schedule or a text-entry screen is blank:** use this complete release, not an older development ZIP. If another mod overrides the same files, check LiveCPK priority. Report the game version and active menu mods with a screenshot.
- **Different icons during a licensed competition:** the premium Game Plan set targets the default menu. Competitions can provide their own menu layouts and icons.
- **Other menu mods:** they can override the same files or runtime colors. Use one default menu theme at a time. The installer backs up existing theme files and settings; it does not merge other menu layouts.
- The intro overrides `movie/intro/FL2027.usm`. Competition-specific intro movies remain controlled by the existing setup.

Compatibility checks use the supplied FL 2027 executable (file version 27.0.0.0, installed game version 27.1.0). They verify the unique palette signature, the `FL2027.usm` startup movie reference, and the unchanged title-screen layout. Installer/restore tests and a LuaJIT palette initialization/reload test are included. The aligned title screen, portrait main menu, career load list, dark information background and Game Plan screen were also observed in a live session. The final English table was verified record by record. Intro playback has not been fully observed. See `VERIFICATION.json` for the precise scope. Competition-specific themes and additional menu servers can override the default theme.

## Repository and packaging

The repository includes 155 ready-to-install game assets, the bundled color component and its configuration, portable scripts, previews, five high-resolution Game Plan icon masters and the editable information-background SVG. The release ZIP is the easiest download for players. `DEPENDENCY-AUDIT.json` records the sources of the consolidated files.

To verify and package the checked-in release using Python 3:

```text
python tools/package_release.py
```

The ZIP and its SHA-256 checksum are written to `dist/`. No extraction of your game, local credentials or personal save data is required.

See [CREDITS.md](CREDITS.md) for the underlying menu work and tools, and [CHANGELOG.md](CHANGELOG.md) for release notes.
