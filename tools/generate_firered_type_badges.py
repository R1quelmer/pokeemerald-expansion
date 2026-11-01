#!/usr/bin/env python3
"""Derive compact HUD glyphs from the engine's indexed type-icon art."""
from pathlib import Path
from PIL import Image

def generate(root, out):
    for number in (1, 2):
        source = Image.open(root / f"graphics/types/battle_icons{number}.png")
        assert source.mode == "P" and source.size == (8, 160)
        result = Image.new("P", (8, 80), 0)
        result.putpalette(source.getpalette())
        for frame in range(10):
            glyph = source.crop((0, frame * 16, 8, frame * 16 + 12))
            # Seven opaque rows plus one transparent row. Three glyphs fit in a
            # 21px rail, even in the native 25px-spaced doubles healthboxes.
            result.paste(glyph.resize((8, 7), Image.Resampling.NEAREST), (0, frame * 8))
        result.save(out / f"battle_type_chips{number}.png", optimize=True)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    generate(root, root / 'graphics/ui/firered')
