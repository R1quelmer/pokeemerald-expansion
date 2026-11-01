# FireRed navy UI direction

This direction supersedes the light/red visual checkpoint documented in
firered-visual-overhaul.md. The light reference defines composition and real
GBA proportions; the dark concept defines colors, contrast and finish only.
The target remains 240x160. No overworld art changes are in scope.

## Shared roles

Colors are quantized to GBA steps in tools/firered_ui_theme.py:
navy #081020, panel #102038, raised #183050, border #284870,
blue #2870B8, cyan #40C0F0, text #E8F0F8, secondary #98B0D0.
Cyan is reserved for selection and small highlights. Red/green/yellow retain
semantic uses such as gender, status, low HP and type graphics.
All production resource changes are FireRed-specific.

## Runtime findings and current implementation

- Shared frames, dialog/context palettes, Continue and Options, Party, Bag,
  Summary and the initial Storage shell use the common navy roles.
- Party current/max HP is one formatted string; the grid no longer renders
  a separator independently in each of two fields. The original split-field
  behavior is retained for other layouts/targets.
- Summary section headings are separate BG0 windows, two tile rows high with
  native 12px text. Content windows begin below those reserved rows.
  The ability name belongs to its header; its description gets the content
  area. Memo and move descriptions wrap within their actual window bounds.
- Header graphics no longer live on the underlying page bitmap where a
  foreground content window could cover them. Header tiles use 0x350..0x3ef,
  after the relearn prompt (800..821), below the BG0 1024-tile boundary.
- The original 240 dynamic Summary graphics and pagination palette reservation
  remain preserved; battle tutorial tile reservations remain unchanged.
- Storage information rows reserve a footer for markings with an 8px screen
  margin; selected sprite palettes stay independent of the interface theme.
- The actual FireRed Oak scene uses Poliwhirl for loading, palette, Pokeball
  animation and cry. LeafGreen retains its original introductory species.
- QA captures the actual introductory scene and records the field BG0 map
  before/after opening Pause to identify any residual frame by layer data.

## Remaining groups

Trainer Card, Naming, Pokedex, shops and remaining secondary screens need the
same treatment. Battle UI and the real rival intro need a navy pass and fresh
runtime inspection. Full/empty/long lists, names, levels and unusual species
must be exercised. No screen is complete merely because its build passes.

## First emulator pass (9f2bfb9)

FireRed visual QA run 41261545671 completed successfully. Actual screenshots
confirmed single Party HP separators and Oak releasing Poliwhirl. Inspection
also found clipped Summary headers: the narrow font advertises an 8px advance
but draws 12px glyphs. Headers now reserve 16px, with separate content windows,
and the paragraph helper accounts for occupied glyph heights. Palette slot 0
in the six Summary background banks now explicitly uses navy. Stats columns
use a consistent 12px baseline. Move PP uses a bounded plain PP current/max
string and a font measured within its 48px window.

The alleged frame behind Pause was checked by dumping the real BG0 map before
and after opening it. Both dumps contain zero non-empty entries outside the
menu rectangle (x19..29, y0..18). The sliver at its left is the house staircase
on the field layer, not an uncleared dialog window. No covering box was added.

Secondary palette resources now include Trainer Card variants, Naming pages,
Dex list/search/cry, shop and Oak backgrounds. Battle palettes use navy while
preserving gender, HP, status and tutorial tile reservations. QA scenes 32..42
exercise levels 1/9/10/99/100, wide names, faint/status/items, long ability/move
names, full storage, full/empty bag, shop confirmation, nickname navigation,
Dex subpages and a normal battle. These additions await their next emulator
pass; successful compilation alone does not approve their appearance.

## Second emulator pass (92fcb37)

Run 41263118356 captured all 43 scenes successfully. Info headers and ability
names are readable, Party edge cases fit and populated/empty bag lists render.
Inspection found two more ownership conflicts: the stats windows extended a
blank sixth tile row over EXPERIENCE, and move-selection cleanup cleared the
EFFECT header with the portrait window. Stats windows now stop before the
header; move detail headers are restored after cleanup and hidden when their
panel closes. The legacy bitmap EFFECT heading is removed from the FireRed
sliding map. Long list move names use ellipses, with the complete selected
move name printed in the 160px section header.

Dex interface labels now have an independent OBJ palette so its old white BG
slot can become navy. Search field slot 3, Naming paper slot 1 and Trainer Card
paper stripe slot 14 become panel colors. Trainer bitmap BADGES ink is moved
to its own text slot before recoloring, preserving the native atlas/tile IDs.
Scenes 43/44 additionally check a maximum-length trainer name, 999:59 time,
maximum money, all badges, the female card and a full box name. Scene 41 now
advances through wild-battle text into commands and the move list. The next
emulator pass must approve these corrections before final delivery.
