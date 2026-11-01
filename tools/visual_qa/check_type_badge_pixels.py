#!/usr/bin/env python3
"""Verify rendered GBA pixels, not just the type state reported by the widget."""
from pathlib import Path
import sys
from PIL import Image

root = Path(__file__).resolve().parents[2]
captures = Path(sys.argv[1])
palettes = [[tuple((int(c) >> 3) * 8 + (int(c) >> 5) for c in row.split())
             for row in (root / f'graphics/types/battle_icons{i}.pal').read_text().splitlines()[3:]]
            for i in (1, 2)]
atlases = [Image.open(root / f'graphics/ui/firered/battle_type_chips{i}.png') for i in (1, 2)]
cases = {
    51: [(13,), (13, 4)],
    52: [(11, 3), (8, 4)],
    53: [(13, 4), (13, 4), (3, 9), (19,)],
    54: [(13, 4), (13, 4), (3, 9), (19,)],
    55: [(11, 17), (15,)],
    56: [(12,), (12,)],
    57: [(8,), (15,)],
    58: [(12,), (13, 4)],
    59: [(13, 4), (13, 4)],
    60: [(8, 13), (11, 3, 13)],
    61: [(11, 3), (13, 4)],
}


def screenshot(scene):
    return Image.open(captures / f'scene-{scene:02d}-frame-{5999 if scene < 55 else 9999:04d}.png').convert('RGB')


offsets = {}
for scene, battlers in cases.items():
    image = screenshot(scene)
    origins = [(139, 69), (16, 7), (151, 94), (4, 32)] if scene in (53, 54) else [(138, 81), (16, 18)]
    for battler, types in enumerate(battlers):
        x, y = origins[battler]
        expected_glyphs = []
        for mon_type in types:
            bank = int(mon_type >= 11)
            frame = mon_type - (11 if bank else 1)
            glyph = atlases[bank].crop((0, frame * 8, 8, frame * 8 + 7))
            expected_glyphs.append([(column, row, palettes[bank][glyph.getpixel((column, row))])
                                    for row in range(7) for column in range(8)
                                    if glyph.getpixel((column, row))])
        # Selected healthboxes have a native 1–2px bounce. All chips must share
        # the same small offset; symbols and every opaque RGB pixel stay exact.
        matches = [(dx, dy) for dx in range(-1, 2) for dy in range(-3, 4)
                   if all(image.getpixel((x + dx + column, y + dy + 7 * slot + row)) == color
                          for slot, glyph in enumerate(expected_glyphs) for column, row, color in glyph)]
        assert matches, f'wrong rendered type glyph/color/order: scene {scene}, battler {battler}, types {types}'
        offsets[scene, battler] = matches[0]

# A dual -> mono change must uncover the clean panel, not leave old type pixels.
for scene, battler in [(51, 0), (56, 1)]:
    x, y = [(138, 81), (16, 18)][battler]
    dx, dy = offsets[scene, battler]
    x, y = x + dx, y + dy
    area = screenshot(scene).crop((x, y + 7, x + 8, y + 14))
    assert set(area.getdata()) <= {(16, 33, 57), (24, 49, 82)}, f'stale second badge in scene {scene}'

# Same PSN glyph pixels before/after HP animations. The final two background
# columns meet different native HP-bar outlines in single and double layouts.
dx, dy = offsets[53, 0]
static_status = screenshot(53).crop((151 + dx, 76 + dy, 173 + dx, 84 + dy))
dx, dy = offsets[61, 0]
animated_status = screenshot(61).crop((150 + dx, 96 + dy, 172 + dx, 104 + dy))
assert static_status.tobytes() == animated_status.tobytes(), 'HP redraw erased or covered PSN'
print('Rendered type glyphs, colors, order, removed badges and status after HP animation passed.')
