# Changelog

## 2.2.4 — FL 2027

- Added the slim Touchline launcher to Master League and the matching Prologue launcher to Become a Legend. Each uses its separately installed companion app.
- Widened the Master League news panel and improved controller movement between the top tabs and dashboard cards.
- Added the native Go to Next Season action to Play Match when the game enables it and there is no active transfer deadline or playable fixture.
- Updated the English release and Spanish and French previews.
- Added Arabic, Italian, Brazilian Portuguese, Russian, and Indonesian previews for the main menu, Master League, and Become a Legend. The Indonesian preview uses the English text language setting.
- Added a gold focus highlight to the Classic Midnight career tabs.

## 2.2.3 — FL 2027

- In Master League, Play Match opens the game's Transfer Deadline Day screen when the Forward Time menu enables it. Verified in a 31 August save.
- Included the fix in the English release and the Spanish and French previews.

## 2.2.2 — FL 2027

- In Become a Legend, Next Match uses the game’s Next action on days when Play Match is unavailable, including between fixtures and on career event days.
- Fixed overlapping follower counts on the Master League dashboard.
- Calendar and Top Transfer can display a known club’s badge when its name is unavailable.
- Applied the dashboard fixes to the Spanish preview.

## 2.2.1 — FL 2027

- In Master League, Play Match uses the game's Next action to resume time between fixtures when it is available.
- If backup creation fails, the installer reports the full folder path and explains that it stopped before writing menu files or Sider settings.
- Added troubleshooting steps for unwritable SiderAddons folders and Windows-protected Desktop or OneDrive locations.

## 2.2.0 — FL 2027

- Added a player-focused Become a Legend dashboard with My Data and Career Records in the top bar.
- Added Next Match, Skip Match, Schedule and Top Transfer shortcuts. Match shortcuts respect the native availability checks, and the selected match button uses the Standings pulse.
- Removed the club-color bar behind the badge. Followers and sponsors have separate space, and follower counts have room for millions.
- Kept standings on the right and streamlined the schedule at the bottom to show competition and club badges, dates, and scores or kickoff times.
- Top Transfer uses the career's currency and highest recorded fee for the active transfer window.

## 2.1.0 — FL 2027 — 2026-11-15

- Bundled the tested Touchline Master League Dashboard 1.2.23 into the full theme and installer.
- Added the horizontal six-tab navigation with dropdowns aligned beneath their tabs, plus match actions, the fixture calendar, standings, top scorers and news.
- Included the Top Transfer, training, notifications, youth, followers and Favourite Players cards. The Favourite Players card shows the first favourite's name with the Touchline crown.
- Included the separate Become a Legend theme with the game's career layout and navigation.
- Upgrades replace active dashboard preview entries and back up the old files and Sider settings for restoration.

## 2.0.0 — FL 2027 — 2026-11-02

- Dedicated FL 2027 repository and release, based on Touchline Menu 1.1.6.
- Startup movie now uses `movie/intro/FL2027.usm`, matching the FL 2027 executable and game archive.
- Installer checks the target executable and palette signature before installation.
- Installer disables stock `switcher\SPcolor.lua` to prevent palette conflicts; uninstall restores its prior setting.
- English text table rebased on FL 2027, preserving its current version labels and text; only the squad-type spelling correction is reapplied.
- Existing menu artwork, dark panels, readability fixes and corrected icons are retained.

## Earlier FL 2026 releases

## 1.1.6

- Fixed the unreadable Master League Information popup and Staff Report screen: their pale lavender panels are now charcoal with champagne lines, so the ivory text shows.
- Changed the lavender titles on both screens to champagne.

## 1.1.5

- Swapped the Manager Offers and Results and Squad List icons to their correct menu entries.
- Preserved the dark Management Career panels and original icon quality.

## 1.1.4

- Fixed the remaining white Management Career panels: dark normal state and charcoal selected state.
- Preserved all six career/offer icons and native menu behavior.

## 1.1.3

- Added supplied icons for Past Glories, Favorite Players, Manager Offers, Results and Squad List, Club Teams and National Teams.
- Preserved the metallic artwork when a career menu tile is selected.
- Replaced the old teal category icons on the Manager Offers page.

## 1.1.2

- Swapped the MyClub and Gallery icons across all seven main-menu scenes.
- Preserved menu actions, backgrounds, labels and all other theme assets.

## 1.1.1

- Smaller download: the release ZIP now carries only what installs, uninstalls and explains the theme.
- Artwork masters and prompts, README screenshots, tests and the packaging tool remain in the repository.
- Theme files are unchanged from 1.1.0.

## 1.1.0

- Standalone distribution: Football Life and Sider are the only runtime requirements.
- Included the 89 fonts and secondary assets previously supplied by a fallback menu pack.
- Bundled the credited color runtime with its own configuration folder.
- Removed external MenuC1987 and UIColors installation checks.
- Installer supports a clean Sider configuration and disables duplicate legacy menu/color entries when upgrading, with reversible backups.
- Preserved the reviewed visuals, Schedule fix, typing dialog and #040B12 backgrounds.

## 1.0.0

First public release of the current installed Touchline / Prologue menu theme.

- Reordered seven-item main menu with matching portrait scenes and mode descriptions.
- `#040B12` information backgrounds with restrained smoke and champagne details.
- Premium default Game Plan icons, custom negotiation and status icons, loading/saving indicators and Touchline intro movie.
- Current working Schedule and search-entry files, plus improved team-rating and unselected-row readability.
- Omitted the obsolete standalone teamPower override.
- Portable installation with checksum validation, backups, rollback on copy failure and restoration support.
