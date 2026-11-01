# FireRed battle type badges

FireRed shows persistent, colored type glyphs next to each active healthbox. The
feature is restricted to `FIRERED`; Emerald and LeafGreen keep their previous
move-selection type-icon behavior and configuration.

## Source of truth

`SpriteCB_HealthboxTypeIcons` calls `GetBattlerTypes(battler, FALSE, types)`.
This is the battle engine's current defensive typing, not the species table.
It accounts for the three live `gBattleMons[battler].types` slots, Roost, and
Terastallization. Ordinary Tera returns a single defensive type. Stellar Tera
retains the engine's underlying defensive types; the existing gimmick indicator
continues to identify the active Terastallization.

Slots are deduplicated in engine order, omitting `TYPE_NONE` and removed
`TYPE_MYSTERY` slots. A genuinely typeless battler gets the native question-mark
glyph. A third distinct type from Forest's Curse or Trick-or-Treat is supported.
The HUD shows actual typing, including an opponent's actual types under Illusion;
it does not implement the optional seen/caught/disguise information restrictions
of the old move-selection-only widget.

## Layout and lifecycle

`CreateBattlerHealthboxSprites` creates a three-sprite badge group for each normal
healthbox. Player badges form a short horizontal row at the upper-left corner,
clear of the Mega/Tera trigger's slide corridor. Right-flank player badges are
aligned to avoid the other healthbox. Opponent badges stack at the right edge;
a third badge sits beside the lower one.

The group follows the actual healthbox's position, slide/bounce offsets,
visibility and OAM priority. It uses `GetBattlerPosition`, rather than treating
a battler ID as a screen position. Native healthbox geometry, text, HP, EXP,
status and gimmick rendering are unchanged. Safari's non-Pokémon player box does
not create a badge group.

One controller per healthbox checks the three effective types each frame. This
bounded check avoids missing changes from less common abilities, forms or moves.
Its cache only switches an atlas frame/palette when a type changes; it performs
no per-frame decompression, allocation, palette upload or pixel rendering. Old
slots become invisible when the type count shrinks. The existing battle/menu
sprite resets handle the group's lifetime, like other healthbox attachments.

## Assets and resource budget

- Reuses `graphics/types/battle_icons1.png`, `battle_icons2.png` and their existing
  palettes. No new type art or 18 separate graphic/palette sets.
- Reuses `gTypesInfo[type].useSecondTypeIconPalette` and native animation frames.
- Two shared tagged OBJ palettes, independent of the battler count. No fixed
  palette-slot writes and no modification of Pokémon, HP or BG palettes.
- Two 640-byte 4bpp sheets: **1,280 bytes / 40 OBJ tiles** total. Both source
  sheets are 8×160, including sheet 2's blank last frame. The entire decompressed
  stream is reserved to avoid writing past the allocation.
- Three 8×16 OAM sprites per healthbox, maximum 12. The visible glyph is smaller
  than its OAM frame. Sprite creation/allocation failures are checked.
- FireRed's old temporary `LoadTypeIcons` path is bypassed, preventing duplicate
  widgets and competing ownership/freeing of these shared resources.

## Emulator validation

`src/firered_visual_qa.c` adds scenes 51–61 for mono/dual typing, four-battler
Double/Multi layouts, Charizard X Mega Evolution, Soak, Protean, Water Tera,
Stellar Tera, Forest's Curse and Roost. The Double fixture also includes a wide
12-character nickname, level 100 and poison.

The mGBA runner reads the exact player action-controller pointer exported only
in the QA cartridge. It advances native intro messages, waits at real menus,
selects Fight, toggles the native gimmick with START and executes the real move.
It freezes at the next action menu after one turn. The fresh QA save grants all
eight badges so level-50/100 fixtures obey rather than napping. Dynamic fixtures give the
opponent a sleep status to avoid interference. Tera fixtures provision a charged
Orb only under `FIRERED && VISUAL_QA`; production charge rules are unchanged.

The capture log records displayed type slots, actual species and active gimmick
for each battler. `tools/visual_qa/check_type_badges.py` checks mono/dual order,
deduplication, four battlers, and the required native mechanic transitions.
Real screenshots still require visual inspection for layout, contrast and
rendering defects; passing this log check alone is not visual approval.

Build with `make firered -j$(nproc)`. The `FireRed visual QA` workflow builds a
separate clean `VISUAL_QA=1` cartridge and exports screenshots/logs, never the ROM.
