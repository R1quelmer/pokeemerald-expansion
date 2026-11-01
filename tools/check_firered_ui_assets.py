#!/usr/bin/env python3
"""Verify authored UI data, independent of PNG encoder and line endings."""
import importlib.util
from pathlib import Path
import struct
import tempfile

from PIL import Image


def main():
    root = Path(__file__).resolve().parents[1]
    folder = root / 'graphics/ui/firered'
    spec = importlib.util.spec_from_file_location('firered_ui', root / 'tools/generate_firered_ui.py')
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    with tempfile.TemporaryDirectory() as temp:
        generator.OUT = Path(temp)
        generator.main()
        generated = {p.relative_to(temp) for p in Path(temp).rglob('*') if p.is_file()}
        committed = {p.relative_to(folder) for p in folder.rglob('*') if p.suffix in ('.png', '.pal', '.bin')}
        assert generated == committed, 'Generated UI file inventory differs from repository'
        for relative in sorted(generated):
            actual, expected = Path(temp) / relative, folder / relative
            if relative.suffix == '.png':
                with Image.open(actual) as a, Image.open(expected) as b:
                    assert a.mode == b.mode == 'P', relative
                    assert a.size == b.size and a.tobytes() == b.tobytes(), relative
                    assert a.getpalette()[:48] == b.getpalette()[:48], relative
                    assert max(a.tobytes()) <= 15, relative
                    assert a.width % 8 == a.height % 8 == 0, relative
            elif relative.suffix == '.pal':
                assert actual.read_text().splitlines() == expected.read_text().splitlines(), relative
                lines = actual.read_text().splitlines()
                assert lines[:2] == ['JASC-PAL', '0100'], relative
                assert int(lines[2]) == len(lines) - 3, relative
            else:
                assert actual.read_bytes() == expected.read_bytes(), relative

    for name, limit in [('main_background', 224), ('bag_background', 320)]:
        with Image.open(folder / (name + '.png')) as atlas:
            count = atlas.width * atlas.height // 64
            assert count <= limit, name + ': BG map allocation overlap'
        tilemap = (folder / (name + '.bin')).read_bytes()
        assert len(tilemap) == 2048, name
        assert all((tile & 1023) < count for tile in struct.unpack('<1024H', tilemap)), name

    with Image.open(folder / 'bag_background.png') as atlas:
        # Runtime pocket transitions write these tile IDs directly.
        for tile, color in [(11, 3), (17, 1), (23, 3), (43, 4)]:
            x, y = tile % 16 * 8, tile // 16 * 8
            assert set(atlas.crop((x, y, x + 8, y + 8)).tobytes()) == {color}, tile
    for original, generated in [('tiles', 'summary_tiles'), ('iv_ev_tiles', 'summary_iv_ev_tiles')]:
        with Image.open(root / f'graphics/summary_screen/{original}.png') as before, Image.open(folder / f'{generated}.png') as after:
            assert after.width * after.height // 64 < 576, generated
            assert after.crop((0, 0, 128, 120)).tobytes() == bytes(p & 15 for p in before.tobytes()), generated + ': fixed controller tiles changed'
    for page in ['info', 'info_egg', 'skills', 'battle_moves', 'contest_moves']:
        data = (folder / f'summary_{page}.bin').read_bytes()
        assert len(data) == 2048, page
        with Image.open(folder / 'summary_tiles.png') as atlas:
            count = atlas.width * atlas.height // 64
        assert all((tile & 1023) < count for tile in struct.unpack('<1024H', data)), page
        if page in ('info', 'info_egg'):
            tilemap = struct.unpack('<1024H', data)
            assert all(tilemap[y * 32 + x] >> 12 == 4 for y in range(2) for x in range(11, 19)), 'Pagination palette lost'
    print('FireRed UI pixels, palettes, tilemaps and runtime tile reservations verified')


if __name__ == '__main__':
    main()
