"""Palette roles for native secondary screens; no tile IDs or geometry change."""
from PIL import Image
import struct
from firered_ui_theme import NAVY, PANEL, RAISED, BORDER, BLUE, CYAN, TEXT, SUBTEXT, WARNING, AMBER


def generate(root, out, write_palette):
    def read(path):
        return [tuple(map(int, line.split())) for line in (root / path).read_text().splitlines()[3:]]

    def png_palette(path):
        p = Image.open(root / path).getpalette()
        return [tuple(p[i:i + 3]) for i in range(0, len(p), 3)]

    selector = png_palette('graphics/summary_screen/move_select.png')[:16]
    selector[1:16] = [CYAN, BLUE, BORDER, CYAN, BLUE, BORDER, CYAN, BLUE,
                     BORDER, CYAN, BLUE, BORDER, CYAN, BLUE, BORDER]
    write_palette(out / 'summary_selector.pal', selector)

    card = [NAVY, PANEL, RAISED, PANEL, BORDER, TEXT, BORDER, NAVY,
            BLUE, BORDER, BLUE, BLUE, BORDER, SUBTEXT, PANEL, BLUE]
    for name in ['blue', 'green', 'bronze', 'silver', 'gold']:
        colors = read(f'graphics/trainer_card/frlg/{name}.pal')
        colors[:16] = card
        for start in [16, 32]:
            colors[start] = NAVY
            colors[start + 10:start + 16] = [AMBER, (248, 216, 120), BLUE, BORDER, PANEL, BORDER]
        write_palette(out / f'trainer_{name}.pal', colors)
    female = read('graphics/trainer_card/frlg/female_bg.pal')
    female[0] = NAVY
    female[10:16] = [AMBER, (248, 216, 120), BLUE, BORDER, PANEL, BORDER]
    write_palette(out / 'trainer_female.pal', female)
    write_palette(out / 'trainer_text.pal', [NAVY, PANEL, TEXT, PANEL, CYAN, PANEL,
        TEXT, PANEL, BLUE, PANEL, PANEL, TEXT, BORDER, BLUE, PANEL, BORDER])
    # Separate bitmap label ink from the repeated white paper stripe.
    atlas = Image.open(root / 'graphics/trainer_card/frlg/tiles.png').point(lambda p: p & 15)
    for y in range(40, 48):
        for x in range(96, 128):
            if atlas.getpixel((x, y)) == 14:
                atlas.putpixel((x, y), 5)
    atlas.putpalette([v for color in card for v in color] + [0] * 720)
    atlas.save(out / 'trainer_tiles.png', bits=4)

    naming = [NAVY, PANEL, PANEL, BORDER, BORDER, RAISED, PANEL, BLUE,
              BORDER, PANEL, NAVY, NAVY, CYAN, PANEL, PANEL, PANEL]
    write_palette(out / 'naming_menu.pal', naming)
    keyboard = read('graphics/naming_screen/keyboard.pal')
    keyboard[:4] = [NAVY, TEXT, PANEL, BORDER]
    keyboard[13:16] = [PANEL, PANEL, PANEL]
    write_palette(out / 'naming_keyboard.pal', keyboard)
    buttons = [NAVY, TEXT, PANEL, BORDER, BLUE, RAISED, CYAN, BORDER,
               BLUE, BORDER, CYAN, BORDER, CYAN, BORDER, PANEL, PANEL]
    write_palette(out / 'naming_buttons.pal', buttons)
    cursor = read('graphics/naming_screen/cursor.pal')
    cursor[:4] = [NAVY, CYAN, BLUE, BORDER]
    cursor[12] = cursor[14] = PANEL
    write_palette(out / 'naming_cursor.pal', cursor)
    for name in ['upper', 'lower', 'others']:
        colors = read(f'graphics/naming_screen/page_swap_{name}.pal')
        colors[:4] = [NAVY, TEXT, PANEL, BORDER]
        colors[11:16] = [BORDER, BORDER, BLUE, BLUE, CYAN]
        write_palette(out / f'naming_page_{name}.pal', colors)

    # Dex print functions use slot 15 for foreground and slot 3 for shadow.
    # Slot 1 also supplies bitmap text. Keep both bright; native mon palettes
    # and the geographical area map are independent and are not recolored.
    for source, target in [('bg_hoenn', 'dex_hoenn'), ('bg_national', 'dex_national'),
                           ('search_results_bg', 'dex_results')]:
        colors = read(f'graphics/pokedex/{source}.pal')
        for start in range(0, len(colors), 16):
            colors[start:start + 16] = [NAVY, PANEL, BLUE, PANEL, RAISED, BORDER,
                NAVY, BORDER, NAVY, PANEL, PANEL, CYAN, RAISED, BORDER, SUBTEXT, TEXT]
        write_palette(out / f'{target}.pal', colors)
    # Sprite labels keep bright slot 1 independently of the old white BG.
    write_palette(out / 'dex_interface.pal', [NAVY, TEXT, BLUE, PANEL, RAISED,
        BORDER, NAVY, BORDER, NAVY, PANEL, CYAN, CYAN, RAISED, BORDER, SUBTEXT, TEXT])
    colors = read('graphics/pokedex/search_menu.pal')
    for start in range(0, len(colors), 16):
        colors[start:start + 16] = [NAVY, PANEL, PANEL, PANEL, TEXT, BORDER, NAVY,
            RAISED, BLUE, BORDER, CYAN, BLUE, RAISED, BORDER, CYAN, TEXT]
    write_palette(out / 'dex_search.pal', colors)
    cry = png_palette('graphics/pokedex/cry_screen_bg.png')[:16]
    cry[:3] = [NAVY, PANEL, BORDER]
    cry[8:16] = [BLUE, BLUE, CYAN, CYAN, SUBTEXT, SUBTEXT, TEXT, TEXT]
    write_palette(out / 'dex_cry.pal', cry)
    meter = png_palette('graphics/pokedex/cry_meter.png')[:16]
    meter[:5] = [NAVY, CYAN, NAVY, PANEL, BLUE]
    meter[5:16] = [PANEL, PANEL, RAISED, RAISED, BORDER, BORDER, BLUE, BLUE, SUBTEXT, SUBTEXT, TEXT]
    write_palette(out / 'dex_meter.pal', meter)

    shop = [NAVY, PANEL, RAISED, BORDER, BLUE, BORDER, NAVY, BLUE,
            CYAN, RAISED, PANEL, BORDER, AMBER, (184, 136, 48), (248, 216, 120), NAVY]
    write_palette(out / 'shop.pal', shop)

    oak = png_palette('graphics/oak_speech/bg_tiles.png')[:64]
    oak[0] = NAVY
    oak[1:9] = [NAVY, NAVY, PANEL, PANEL, RAISED, RAISED, PANEL, PANEL]
    oak[16:26] = [NAVY, BLUE, BLUE, BORDER, BORDER, RAISED, RAISED, PANEL, PANEL, NAVY]
    oak[32:42] = [NAVY, BORDER, BLUE, RAISED, PANEL, PANEL, SUBTEXT, BORDER, BLUE, PANEL]
    oak[48] = NAVY
    write_palette(out / 'oak_background.pal', oak)
    for source, bank in [('battle', 3), ('contest', 1)]:
        data = (root / f'graphics/summary_screen/effect_{source}.bin').read_bytes()
        tiles = list(struct.unpack('<80H', data))
        # Remove the legacy bitmap heading now owned by a BG0 window.
        # Preserved tile 0x34 is solid panel color 12.
        tiles[10:20] = [(bank << 12) | 0x34] * 10
        (out / f'summary_effect_{source}.bin').write_bytes(struct.pack('<80H', *tiles))
