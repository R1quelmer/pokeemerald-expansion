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
healthbox. Badges stack in a narrow rail inside the left edge on both sides.
The visible 8×7 glyphs occupy at most 21px vertically, fitting native Double/Multi
boxes without touching Pokémon sprites, adjacent boxes or the Mega/Tera trigger.

The group follows the actual healthbox's position, slide/bounce offsets,
visibility and OAM priority; it never treats a battler ID as a screen position.
The box dimensions, HP, EXP, level and gimmick positions remain native. Name and
status move 8px right; the caught-ball marker uses the same inset when there is
no status. The native font-fitting logic still applies. Exceptionally wide names
that cannot fit even the narrowest font get a visible ellipsis with gender
preserved, avoiding overlap with Lv100. The nickname data and other menus retain
the full name. Safari's non-Pokémon player box does not create a badge group.
The HP-text erase rectangle starts after the inset status label, so healing and
damage animations cannot clear its final glyph. Four-digit HP text still fits
inside the remaining 48px region.

One controller per healthbox checks the three effective types each frame. This
bounded check avoids missing changes from less common abilities, forms or moves.
Its cache only switches an atlas frame/palette when a type changes; it performs
no per-frame decompression, allocation, palette upload or pixel rendering. Old
slots become invisible when the type count shrinks. The existing battle/menu
sprite resets handle the group's lifetime, like other healthbox attachments.

## Assets and resource budget

- Derives two compact atlases from `graphics/types/battle_icons1.png` and
  `battle_icons2.png`, retaining their existing indexed colors and type symbols.
  `tools/generate_firered_type_badges.py` reproduces the 8×7 glyphs using nearest
  pixel sampling. No separate graphic/palette set for each type.
- Reuses `gTypesInfo[type].useSecondTypeIconPalette` and the existing palettes.
- Two shared tagged OBJ palettes, independent of the battler count. No fixed
  palette-slot writes and no modification of Pokémon, HP or BG palettes.
- Two 320-byte 4bpp sheets: **640 bytes / 20 OBJ tiles** total. Both compact
  sheets are 8×80, including sheet 2's blank last frame. The entire decompressed
  stream is reserved to avoid writing past the allocation.
- Three 8×8 OAM sprites per healthbox, maximum 12. The visible glyph is smaller
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
The Roost fixture also has poison, exercising the status label through healing,
temporary type removal, restoration, and end-of-turn HP loss.

The capture log records displayed type slots, actual species and active gimmick
for each battler. `tools/visual_qa/check_type_badges.py` checks mono/dual order,
deduplication, four battlers, and the required native mechanic transitions.
Real screenshots still require visual inspection for layout, contrast and
rendering defects; passing this log check alone is not visual approval.
`check_type_badge_pixels.py` also compares actual mGBA pixels with each type's
indexed glyph/palette on both sides, including four-battler layouts, checks
that a removed second badge leaves a clean panel, and compares the native PSN
tiles before/after healing and poison damage. This catches an OAM frame failing
to update even when the cached type and palette reference are correct.

Build with `make firered -j$(nproc)`. The `FireRed visual QA` workflow builds a
separate clean `VISUAL_QA=1` cartridge and exports screenshots/logs, never the ROM.
