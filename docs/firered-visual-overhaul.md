# FireRed visual overhaul — working specification

## Scope and status

This is an ongoing overhaul. A successful build is not visual approval.
The first deliverable fixes the first-battle frame collision and adds opt-in
emulator screenshots. Menu work is being consolidated with actual mGBA captures. Overworld remains
pending until the current menu and encounter checks are stable.

| Area | Controller / asset entry points | Status |
| --- | --- | --- |
| Battle and intro | battle_bg.c, battle_interface.c, battle_controller_oak_old_man.c; graphics/battle_interface/firered | Real lab trigger, Blue intro, battle victory and return captured cleanly |
| Title | title_screen_frlg.c; graphics/title_screen_frlg/firered | Audit complete; design pending |
| Continue/New Game | main_menu.c; graphics/ui/firered/main_* | Background and softer selection contrast captured; Continue details retained |
| Pause/save | start_menu.c; shared text_window.c frames | Wider FireRed panel/header and field-to-Bag return captured |
| Options | option_menu.c; graphics/ui/firered/options_text.pal | Legibility/contrast refined and captured; settings retain original behavior |
| Party | party_menu.c, firered_party_grid.h; graphics/ui/firered/party_card* | Grid and 1..6-party interactions captured; fainted/status/item and special layouts checked |
| Summary | pokemon_summary_screen.c; graphics/summary_screen | New neutral/red/blue/violet panels captured; pagination, move details, egg and status/item checked |
| Bag | item_menu.c; graphics/ui/firered/bag* | All pockets, accent timing, actions and normal field return captured |
| Dex | pokedex.c / pokedex_plus_hgss.c, include/config/pokedex_plus_hgss.h | Variant selection must be respected; redesign pending |
| Trainer Card | trainer_card.c; graphics/trainer_card/frlg | FRLG-specific implementation; redesign pending |
| Naming | naming_screen.c; graphics/naming_screen | Shared controller; redesign pending |
| PC/storage | pokemon_storage_system.c; graphics/pokemon_storage | FireRed shell, populated box, cursor and action menu captured |
| Messages/signs/shop | text_window.c, field_message_box.c, shop.c | Shared frames seen in menus and Oak tutorial; broader signs/shop review pending |
| Overworld | data/maps, data/layouts, data/tilesets | Prototype pending UI consolidation |

Except for explicitly selected FRLG resources (title/card/maps), controllers
and many graphics are shared with Emerald/LeafGreen. Prefer FireRed-specific
resource selection, preserve the public symbols and resource allocations,
and leave other targets on their original resources.

## Style system

- Canvas 240x160; use integer pixel positions and existing GBA font metrics.
- Ink #202028, charcoal #282830, paper #F8F8F8, muted #E0E0E8.
- Primary/trainer red #C02840; information blue #30A8E0.
- Items amber #E8A028; moves violet #7050B8; nature green #30C070.
- Angular clipped corners, narrow accent rails, flat fills and restrained
  outlines. Use color with labels/icons, never as the only state indicator.
- Maintain an 8-pixel tile grid for structure; minimum 2-pixel content padding.
- Preserve full nickname, level, HP, status and held-item/gimmick coverage.
- Design full screen composition; palette changes alone are not completion.
- Do not alter maps, collisions, warps, events or progression for decoration.
- Author a small consistent overworld set before propagating to Kanto.

## First-battle defect

`LoadBattleMenuWindowGfx()` in battle_bg.c loads the Oak/Old Man frame with
`LoadMessageBoxGfx(0, 0x30, BG_PLTT_ID(7))`. text_window.c copies 0x1c0 bytes:
14 four-bit tiles, occupying 0x30..0x3d in BG0. The original skin generator
allocated decorative tiles from 0x30 and referenced them in its border map.
The tutorial overwrote those graphics after the skin had loaded.

The skin allocator now starts at 0x40 and its deduplication excludes the
tutorial range. Validation forbids BG map references to 0x30..0x3f. Fixed
cursor/confirmation indices are retained. The atlas size remains 128x128,
the map 4096 bytes, and 98 occupied slots stay below window tile 0x90.
The first-battle-flags capture no longer has the striped border. The real
Oak lab rival encounter must still be checked through its original coordinate
trigger, trainer setup and return script before this issue is closed.

## Emulator fixtures

`make clean && make firered -j$(nproc) VISUAL_QA=1` builds a test-only ROM.
The normal build does not compile the fixtures. `gVisualQaScene` selects a
screen when the main menu first opens: 0 main menu, 1 options, 2 party,
3 summary, 4 bag, 5 dex, 6 card, 7 naming, 8 PC, 9 first-battle flags;
10 actual Oak lab rival coordinate trigger, 11..16 parties of 1..6 mons,
17 fainted/status/held-item party, 18..21 other pockets, 22..23 summary pages;
24 double layout, 25 full-multi layout, 26 Party-to-Summary flow,
27 Continue/Options return, 28 egg, 29 Summary status/item, 30 field pause/Bag return.

The headless mGBA runner captures real framebuffer PNGs from each fixture.
Fixture 9 exercises the first-battle resource allocation; it is not a complete
playthrough of Oak's lab or a substitute for reproducing the rival encounter.
The fixtures use synthetic party data and never save to a user's save file.
No ROM binary or save file is included in uploaded artifacts.

Review every captured screen for clipping, colors, cursor visibility and
state transitions before expanding changes. Screens that do not initialize
correctly must be fixed; the presence of PNGs alone is not a passing test.

## Preservation contract

Keep custom_frlg_starters.inc, customize_frlg_starters.py, make_patch.py,
modern species/gimmicks and Kanto events intact. Commit by functional area.
Run clean builds on fresh target-specific jobs. Record emulator gaps honestly.


## Checkpoint 9c43759

FireRed, Emerald and LeafGreen build jobs passed (push CI 41217774955 and PR
CI 41217779287). Native navigation assertions passed for every party size
1..6, ordinary and choose-half exits, and all directional inputs. Visual QA
41217774915 produced real screenshots of the six-card party and new bag.
These captures establish the base composition, not all interaction coverage.

Remaining observed defects: direct Summary capture has overlapping text;
old PC fixture called a field-only menu outside the overworld, returning to
the main menu. Fixture fe7f870 resets title tasks before direct menu entry,
uses the storage controller's real entry, enables a populated National Dex,
and resumes the actual lab map before its rival coordinate trigger. Review
its captures before interpreting either defect as a production regression.


## Checkpoints fe7f870 and cb348d2

The Summary overlap was caused by the isolated fixture retaining title-screen
tasks. Resetting tasks before direct entry removes it: no Summary production
controller change was required. Info, stats and moves now render cleanly.
The fixture also explicitly grants initial moves, matching normal mon creation;
its earlier empty move lists and Struggle-only battle were test-data defects.

The real Oak lab map is loaded at the pre-battle position, then DOWN activates
the existing coordinate trigger. Original approach, dialogue, trainerbattle,
Oak tutorial, battle and return scripts execute unchanged. The correct Blue
trainer and rival Fennekin are visible without the striped border; cb348d2
finished with outcome 1 (victory) and returned to the lab. This is a checkpoint
resume, not a full playthrough of the new-game/name/starter-selection sequence.

Captured all five Bag pockets and the action submenu; cancel returns to Options
in the isolated fixture. Accent updates originally used the previous pocket
during animation; moving the update after the committed pocket change fixes
that timing. The next captures must confirm every settled pocket color.

Native grid assertions and actual party screenshots cover counts 1..6, opening
actions, directional movement, cancel, fainted/poisoned mons and held items.
Double and full-multi layouts keep their original arrangements and were also
captured; no linked multiplayer session was exercised.

Clean build jobs for FireRed, Emerald and LeafGreen passed at fe7f870 and
cb348d2. Screenshot workflow 41234108386 passed. PC shell f6ad70e is being
validated separately before any further UI expansion.


## Verified code checkpoint 86e8b69

FireRed visual QA run 41235867529 completed successfully. Its actual framebuffer
captures confirm the Summary redesign and correct pagination palette, populated
move details, egg and held-item/status displays, Continue/Options round-trip,
and normal field pause -> Bag -> pause -> field. Pause uses a dark MENU header
and a wider label panel; headerless layouts keep the original row origin.

The Summary's controller preserves destination palette bits when updating
pagination tile numbers. New info/egg maps therefore retain bank 4 in that
region. The asset checker asserts this, checks pixel/palette reproducibility,
and confirms that the original 240 Summary tiles remain byte-equivalent in
hardware indices. The new atlas contains 272 tiles.

Code checkpoint 86e8b69d869219d25fbd6fb35df977d66109ad4a passed clean build jobs
for FireRed (124639406913), Emerald (124639406695) and LeafGreen (124639406939)
in CI run 41235867451. Native grid checks and asset checks passed in the visual
QA job. The general battle test job was still running when this checkpoint
was documented; its result is not claimed here.

This is a consolidated menu checkpoint, not the completion of the broad visual
overhaul. Dex, trainer card, naming, title, broader secondary screens and the
overworld proof of concept remain. No real linked multiplayer session or old
save migration was tested. No starter/rival customization or BPS source file
was modified relative to a361b25.
