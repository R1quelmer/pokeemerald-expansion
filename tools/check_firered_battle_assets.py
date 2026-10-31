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
