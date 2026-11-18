# Touchline Menu Classic for FL 2027

Classic uses the original Master League and Become a Legend menus, navigation, and actions with Touchline’s palette and backgrounds. It also includes the Touchline main menu and the rest of the shared theme. The dashboard uses the game’s own career screens to display fixtures, club badges, transfers, and followers.

Close Football Life and Sider, extract the complete Classic ZIP, and run **Install.cmd**. Enter the full path to the **SiderAddons** folder that contains `sider.ini`. Start the game through your usual FL 2027 shortcut. Classic is a complete theme package and can replace an existing Touchline dashboard installation.

In Master League, **System → Touchline** replaces the original “.” row and opens or restores `SiderAddons\TouchlineCompanion\Touchline.exe`.

In Become a Legend, **System → Prologue** appears at the end of System when `Prologue.exe` is installed in `SiderAddons\PrologueCompanion`, `SiderAddons\Prologue`, `SiderAddons\TouchlineCompanion`, or directly in `SiderAddons`. The two apps are separate installations. The Classic preview uses the English Touchline theme assets.

The installer prints the backup folder. To restore the previous installation, close the game and Sider, then run this from PowerShell in the extracted package.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Uninstall.ps1 -SiderDir 'D:\SP Football Life 2027\SiderAddons' -BackupDirectory 'D:\SP Football Life 2027\SiderAddons\TouchlineMenu-backups\YOUR-BACKUP-FOLDER'
```

Use your own installation and backup paths. The original career menus need FL 2027 and Sider with LiveCPK enabled. The app shortcut also uses Sider’s LuaJIT extensions and checks the game’s native menu functions before enabling itself.
