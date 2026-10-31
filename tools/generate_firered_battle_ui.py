#!/usr/bin/env python3
"""Regenerate the FireRed-only battle skin (requires Pillow).

Keep the engine's tile order, sprite allocations, text rectangles and palette
roles. The shared Emerald/LeafGreen graphics are deliberately left intact.
Run from any directory: python3 tools/generate_firered_battle_ui.py
"""
from pathlib import Path
import struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "graphics/battle_interface"
DEST = SOURCE / "firered"


def save_image(name, image, palette=None):
    if palette is not None:
        image.putpalette([v for color in palette for v in color] + [0] * (768 - 3 * len(palette)))
    image.save(DEST / (name + ".png"), bits=4, optimize=False)


def save_palette(name, colors):
    (DEST / (name + ".pal")).write_text(
        "JASC-PAL\n0100\n16\n" + "\n".join("%d %d %d" % c for c in colors) + "\n")


# 12..15 are the four battlers' runtime status colors. 9/10 are gender,
# 11 is EXP. Keep these roles: UpdateStatusIconInHealthbox patches 12..15.
HEALTH = [(0, 0, 0), (32, 32, 40), (248, 248, 248), (224, 224, 232),
          (192, 40, 64), (104, 104, 120), (40, 40, 48), (192, 40, 64),
          (160, 160, 176), (48, 168, 224), (240, 104, 144), (48, 184, 232),
          (0, 0, 255), (0, 255, 0), (255, 0, 0), (106, 148, 255)]
BAR = [(0, 0, 0), (32, 32, 40), (248, 248, 248), (224, 224, 232),
       (144, 144, 160), (56, 56, 72), (40, 40, 48), (248, 208, 72),
       (248, 208, 72), (248, 208, 72), (48, 192, 112), (112, 232, 152),
       (232, 160, 40), (248, 208, 72), (208, 56, 72), (248, 104, 112)]
# Text indices are part of BattleWindowText's ABI. Message/prompt: 1/6/15;
# command/move/PP windows: 13/14/15. Do not remap dynamic type/PP colors.
MESSAGE = [(0, 0, 0), (248, 248, 248), (224, 72, 96), (32, 32, 40),
           (184, 40, 64), (248, 248, 248), (32, 32, 40), (224, 224, 232),
           (56, 56, 72), (32, 32, 40), (128, 128, 144), (104, 104, 120),
           (224, 72, 96), (184, 40, 64), (56, 56, 72), (32, 32, 40)]
MENU = [(0, 0, 0), (32, 32, 40), (104, 104, 120), (224, 224, 232),
        (40, 40, 48), (248, 248, 248), (48, 168, 224), (224, 224, 232),
        (192, 40, 64), (184, 40, 64), (112, 80, 184), (152, 120, 224),
        (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]


def healthboxes():
    names = ["healthbox_singles_player", "healthbox_singles_opponent",
             "healthbox_singles_opponent_large", "healthbox_doubles_player",
             "healthbox_doubles_opponent", "healthbox_safari"]
    for name in names:
        old = Image.open(SOURCE / (name + ".png"))
        im = Image.new("P", old.size, 0)
        d = ImageDraw.Draw(im)
        player = "player" in name or "safari" in name
        tall = old.height == 64
        left, right = (9, 102) if player else (1, 94)
        bottom = 34 if tall else 26
        # Angular silhouette, a flat paper surface and two-pixel color rail.
        outline = [(left + 5, 2), (right - 5, 2), (right, 7),
                   (right, bottom - 5), (right - 5, bottom),
                   (left, bottom), (left, 7)]
        d.polygon(outline, fill=6)
        d.polygon([(left + 5, 4), (right - 5, 4), (right - 2, 7),
                   (right - 2, bottom - 5), (right - 6, bottom - 2),
                   (left + 2, bottom - 2), (left + 2, 7)], fill=2)
        d.line((left + 6, 3, right - 6, 3), fill=7, width=1)
        d.line((left + 1, 8, left + 1, bottom - 3), fill=7, width=1)
        # Content is printed through y=15; leave the name/level row untouched.
        d.line((left + 7, 16, right - 3, 16), fill=3)
        if player and tall:
            # Keep the EXP label's exact original pixel mask; its tiles share
            # the bottom row with dynamically copied EXP segment tiles.
            for y in range(old.height):
                for x in range(old.width):
                    if old.getpixel((x, y)) == 9 and y >= 32:
                        im.putpixel((x, y), 11)
        save_image(name, im, HEALTH)

    # Repair graphics used when toggling numeric HP in doubles. Preserve their
    # tile count and opaque footprint, including the opponent percent variant.
    repairs = ["misc", "healthbox_doubles_player_frameend",
               "healthbox_doubles_player_frameend_bar",
               "healthbox_doubles_opponent_frameend",
               "healthbox_doubles_opponent_frameend_bar"]
    for name in repairs:
        im = Image.open(SOURCE / (name + ".png")).copy()
        im = im.point(lambda p: {4: 3, 5: 6, 7: 6, 8: 3}.get(p, p))
        save_image(name, im, HEALTH)
    for name, pal in [("ball_status_bar", HEALTH), ("ball_display", BAR)]:
        save_image(name, Image.open(SOURCE / (name + ".png")).copy(), pal)


def meters():
    for name, tiles, palettes in [("hpbar", 12, [(11, 10)]),
                                  ("hpbar_anim", 18, [(13, 12), (15, 14)])]:
        im = Image.open(SOURCE / (name + ".png")).copy()
        first = 3 if name == "hpbar" else 0
        for group, (light, solid) in enumerate(palettes):
            for pixels in range(9):
                x0 = (first + group * 9 + pixels) * 8
                for x in range(8):
                    for y in range(8):
                        color = 0 if y in (0, 7) else 1 if y in (1, 6) else 5
                        if x < pixels and 2 <= y <= 5:
                            color = light if y == 2 else solid
                        im.putpixel((x0 + x, y), color)
        save_image(name, im, BAR)
    im = Image.new("P", (72, 8))
    for pixels in range(9):
        for x in range(8):
            for y in range(8):
                color = 0
                if y == 0:
                    color = 3
                elif 1 <= y <= 5:
                    color = 6
                if 2 <= y <= 4 and x < pixels:
                    color = 11
                im.putpixel((pixels * 8 + x, y), color)
    save_image("expbar", im, HEALTH)
    im = Image.open(SOURCE / "misc_frameend.png").copy()
    im = im.point(lambda p: 1 if p in (3, 6) else p)
    save_image("misc_frameend", im, BAR)


def textbox():
    # Three 240x160 pages in one 32x64 BG map: message, actions, moves.
    pages = Image.new("P", (256, 512), 0)
    d = ImageDraw.Draw(pages)

    def panel(x0, y0, x1, y1, menu=False, accent=8):
        bg = 5 if menu else 15
        edge = 1 if menu else 8
        d.polygon([(x0 + 4, y0), (x1 - 4, y0), (x1, y0 + 4),
                   (x1, y1), (x0, y1), (x0, y0 + 4)], fill=edge)
        d.polygon([(x0 + 4, y0 + 2), (x1 - 4, y0 + 2),
                   (x1 - 2, y0 + 4), (x1 - 2, y1 - 2),
                   (x0 + 2, y1 - 2), (x0 + 2, y0 + 4)], fill=bg)
        d.line((x0 + 5, y0 + 2, x1 - 5, y0 + 2), fill=accent, width=2)
        # Angular tab in the top corner, outside the window print rectangles.
        d.polygon([(x1 - 17, y0 + 2), (x1 - 5, y0 + 2),
                   (x1 - 2, y0 + 5), (x1 - 20, y0 + 5)], fill=accent)

    panel(0, 112, 239, 159, accent=13)
    panel(0, 272, 125, 319, accent=13)
    panel(128, 272, 239, 319, menu=True, accent=8)
    panel(0, 432, 159, 479, menu=True, accent=10)
    panel(160, 432, 239, 479, menu=True, accent=6)
    # Deduplicate without flips, staying below the first window's tile 0x90.
    # Controllers address cursor tiles 1/2, 28/29, 30/31 and erase tile 0x16
    # directly; HandleBattleWindow uses the 0x22..0x2a nine-slice. Retain all
    # of these indices instead of allowing deduplication to renumber them.
    original = Image.open(SOURCE / "textbox.png")
    tiles = [original.crop(((i % 16) * 8, (i // 16) * 8,
                            (i % 16) * 8 + 8, (i // 16) * 8 + 8))
             for i in range(48)]
    ids = {tile.tobytes(): i for i, tile in enumerate(tiles)}
    tilemap = []
    for ty in range(64):
        for tx in range(32):
            tile = pages.crop((tx * 8, ty * 8, tx * 8 + 8, ty * 8 + 8))
            key = tile.tobytes()
            if key not in ids:
                ids[key] = len(tiles)
                tiles.append(tile)
            pal = 1 if (34 <= ty <= 39 and tx >= 16) or 54 <= ty <= 59 else 0
            tilemap.append(ids[key] | pal << 12)
    assert len(tiles) <= 0x90, "Battle BG tiles overlap message window"
    atlas = Image.new("P", (128, 128), 0)
    for i, tile in enumerate(tiles):
        atlas.paste(tile, ((i % 16) * 8, (i // 16) * 8))
    save_image("textbox", atlas, MESSAGE)
    (DEST / "textbox_map.bin").write_bytes(struct.pack("<2048H", *tilemap))
    save_palette("textbox_0", MESSAGE)
    save_palette("textbox_1", MENU)
    colors = [tuple(map(int, line.split())) for line in (SOURCE / "text.pal").read_text().splitlines()[3:]]
    colors[11:16] = [(168, 168, 184), (80, 80, 96), (32, 32, 40),
                     (248, 248, 248), (248, 248, 248)]
    save_palette("text", colors)
    print(f"FireRed battle BG: {len(tiles)} unique tiles, limit 144; map 4096 bytes")


def validate():
    for path in DEST.glob("*.png"):
        im = Image.open(path)
        original = Image.open(SOURCE / path.name)
        assert im.mode == "P" and im.size == original.size, path.name
        assert max(im.tobytes()) < 16, path.name
    assert (DEST / "textbox_map.bin").stat().st_size == 4096
    print("Validated: original dimensions, 4bpp indices, no extra OBJ tiles/palettes")


if __name__ == "__main__":
    DEST.mkdir(exist_ok=True)
    healthboxes()
    meters()
    textbox()
    validate()
