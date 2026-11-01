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

## First implementation group (awaiting runtime approval)

- Shared frames, dialog/context palettes, Continue and Options, Party, Bag,
  Summary and the initial Storage shell use the common navy roles.
- Party current/max HP is one formatted string; the grid no longer renders
  a separator independently in each of two fields. The original split-field
  behavior is retained for other layouts/targets.
- Summary section headings are separate BG0 windows, one tile row high with
  the native 8px label font. Content windows begin on the following tile row.
  The ability name belongs to its header; its description gets the content
  area. Memo and move descriptions wrap within their actual window bounds.
- Header graphics no longer live on the underlying page bitmap where a
  foreground content window could cover them. Header tiles use 0x350..0x39f,
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
