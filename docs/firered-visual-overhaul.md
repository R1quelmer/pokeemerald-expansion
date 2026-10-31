# FireRed visual overhaul — working specification

## Scope and status

This is an ongoing overhaul. A successful build is not visual approval.
The first deliverable fixes the first-battle frame collision and adds opt-in
emulator screenshots. Menus and overworld remain pending until implemented
and inspected; this document does not claim that they are redesigned.

| Area | Controller / asset entry points | Status |
| --- | --- | --- |
| Battle and intro | battle_bg.c, battle_interface.c, battle_controller_oak_old_man.c; graphics/battle_interface/firered | First-battle fix prepared; emulator review pending |
| Title | title_screen_frlg.c; graphics/title_screen_frlg/firered | Audit complete; design pending |
| Continue/New Game | main_menu.c; graphics/ui/firered/main_* | New composition prepared; runtime review pending |
| Pause/save | start_menu.c; shared text_window.c frames | Audit complete; redesign pending |
| Options | option_menu.c; graphics/ui/firered/options_text.pal | Header, row dividers and accents prepared; runtime review pending |
| Party | party_menu.c, data/party_menu.h; graphics/party_menu | Audit complete; redesign pending |
| Summary | pokemon_summary_screen.c; graphics/summary_screen | Audit complete; redesign pending |
| Bag | item_menu.c; graphics/bag | Audit complete; redesign pending |
| Dex | pokedex.c / pokedex_plus_hgss.c, config/pokedex.h | Variant selection must be respected; redesign pending |
| Trainer Card | trainer_card.c; graphics/trainer_card/frlg | FRLG-specific implementation; redesign pending |
| Naming | naming_screen.c; graphics/naming_screen | Shared controller; redesign pending |
| PC/storage | pokemon_storage_system.c; graphics/pokemon_storage | Shared controller; redesign pending |
| Messages/signs/shop | text_window.c, field_message_box.c, shop.c | FireRed geometric frames prepared; runtime review pending |
| Overworld | data/maps, data/layouts, data/tilesets, graphics/tilesets | Prototype pending UI consolidation |

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
This explains the supplied corruption; runtime confirmation is still required.

## Emulator fixtures

`make clean && make firered -j$(nproc) VISUAL_QA=1` builds a test-only ROM.
The normal build does not compile the fixtures. `gVisualQaScene` selects a
screen when the main menu first opens: 0 main menu, 1 options, 2 party,
3 summary, 4 bag, 5 dex, 6 card, 7 naming, 8 PC, 9 first-battle flags.

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
