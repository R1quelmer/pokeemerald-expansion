# FireRed battle UI, phase 1

FireRed selects a separate skin in `src/graphics.c`. Emerald and LeafGreen
continue to select the original assets. No battle rules, maps, Pokemon sprites,
controller input handling or gimmick code are changed.

## Visual design

- Flat off-white health panels, charcoal angular outlines and a red edge rail.
- High-contrast dark message/prompt panel with red accents.
- White action menu; purple move-panel and blue PP/type-panel accents.
- Four-pixel HP fill, retaining green/yellow/red thresholds and animations.
- Flat blue EXP fill, retaining the existing eight-segment progression.
- Single, double, Safari and optional opponent-percentage healthbox variants.

Name, level, gender, status, caught icon, numeric HP, Mega/other gimmick level
indicators and trigger buttons use their existing rectangles and coordinates.
Long names, four-digit HP, Z-Move details and move information keep the engine's
existing fitting logic. Status text retains its per-battler dynamic palette
entries, allowing different status conditions in double battles.

## Source and regeneration

`graphics/battle_interface/firered/` contains indexed 4bpp PNGs, JASC palettes
and the 32x64 BG tilemap. The source images have the same dimensions as the
originals, including the unused transparent areas required by sprite sheets.

To regenerate these assets (Pillow is an authoring dependency only):

```sh
python3 tools/generate_firered_battle_ui.py
make firered -j$(nproc)
```

`graphics_file_rules.mk` concatenates the two FireRed textbox palettes. All
other assets use the existing conversion and compression rules.

## Allocation audit

- BG atlas remains 128x128 / 256 tiles / 8192 uncompressed bytes. Only 82 tile
  slots are populated, below the first message window at tile 0x90 (144).
- Map remains 4096 bytes / 32x64 tiles, with the same three screen pages.
- Fixed cursor indices 1/2, 28/29, 30/31, erase tile 0x16 and confirmation-frame
  tiles 0x22..0x2a retain their positions and pixel masks.
- Healthbox sprite-sheet sizes, metatile arrangement, tile tags, OBJ count and
  palette tags are unchanged. Every PNG index is below 16.
- Healthbox index 2 is still the printable surface; indices 9/10 retain gender
  colors, 11 is EXP, and 12..15 remain reserved for per-battler status colors.
- No additional EWRAM/IWRAM allocations or per-frame operations are introduced.

## Emulator acceptance checks

Asset validation and successful ROM compilation cannot establish every runtime
visual interaction. Check the following in an emulator before calling the skin
visually approved:

- Oak's first battle, catching tutorial, wild/trainer battles and Safari mode.
- Each action and move cursor, yes/no prompts, switching and returning from Bag.
- HP animation at all three colors, EXP and level-up, level 100, long nicknames,
  three-digit level and four-digit HP.
- Double/multi and 2-vs-1 battles; numeric-HP toggle; different simultaneous
  status conditions; optional opponent HP percentages.
- Mega, Z-Moves (long names/effect details), Dynamax and Terastallization;
  trigger animation, level indicator, move info and type/effectiveness/PP colors.

The CI workflow also runs on `feat/firered-hack-base`, using independent clean
jobs for FireRed, Emerald and LeafGreen, so builds never share target assets.
ROM binaries are neither committed nor uploaded by this change.
