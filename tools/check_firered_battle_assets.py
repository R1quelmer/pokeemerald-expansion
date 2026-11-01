#!/usr/bin/env python3
"""Check generated GBA pixels/palette indices, independent of PNG encoder version."""
import io
from pathlib import Path
import subprocess
import sys
from PIL import Image

root = Path(__file__).resolve().parents[1]
folder = root / 'graphics/battle_interface/firered'
expected = {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()}
subprocess.run([sys.executable, str(root / 'tools/generate_firered_battle_ui.py')], check=True)
for name, data in expected.items():
    generated = (folder / name).read_bytes()
    if name.endswith('.png'):
        old = Image.open(io.BytesIO(data))
        new = Image.open(io.BytesIO(generated))
        assert old.size == new.size and old.mode == new.mode, name
        assert old.tobytes() == new.tobytes(), name + ': pixel indices changed'
        assert old.getpalette()[:48] == new.getpalette()[:48], name + ': palette changed'
    elif name.endswith('.pal'):
        assert data.splitlines() == generated.splitlines(), name
    else:
        assert data == generated, name
print('GBA pixels, palette indices and tilemap match the committed assets')

chips = root / 'graphics/ui/firered'
before = [Image.open(chips / f'battle_type_chips{i}.png').copy() for i in (1, 2)]
subprocess.run([sys.executable, str(root / 'tools/generate_firered_type_badges.py')], check=True)
for number, old in enumerate(before, 1):
    new = Image.open(chips / f'battle_type_chips{number}.png')
    assert new.mode == 'P' and new.size == (8, 80)
    assert old.tobytes() == new.tobytes()
    assert old.getpalette()[:48] == new.getpalette()[:48]
    assert max(new.tobytes()) < 16
    for frame in range(10):
        assert not any(new.crop((0, frame * 8 + 7, 8, frame * 8 + 8)).tobytes())
assert 2 * 8 * 80 // 2 == 640  # Full decompressed sheets: 20 OBJ tiles.
print('Compact type glyphs reproduce exactly and fit the 640-byte OBJ budget')
