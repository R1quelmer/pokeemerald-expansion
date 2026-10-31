#!/usr/bin/env python3
"""Author FireRed's shared geometric frames and main-menu background (Pillow)."""
from pathlib import Path
import struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'graphics/ui/firered'
INK=(32,32,40); PAPER=(248,248,248); MUTED=(224,224,232)
RED=(192,40,64); BLUE=(48,168,224); VIOLET=(112,80,184)
AMBER=(232,160,40); GREEN=(48,192,112)

def palette(path, colors):
    path.write_text('JASC-PAL\n0100\n16\n'+'\n'.join('%d %d %d'%c for c in colors)+'\n',newline='\n')

def save(path, im, colors):
    im.putpalette([v for c in colors for v in c]+[0]*(768-3*len(colors)))
    im.save(path,bits=4)

def frame(accent):
    im=Image.new('P',(24,24),0);d=ImageDraw.Draw(im)
    d.polygon([(5,2),(18,2),(21,5),(21,21),(2,21),(2,5)],fill=15)
    d.polygon([(5,4),(18,4),(19,5),(19,19),(4,19),(4,5)],fill=14)
    d.line((5,3,18,3),fill=13)
    d.line((3,6,3,18),fill=13)
    return im

def bag_background():
    # Retain the tile IDs used by the pocket-switch wipe and indicators.
    im=Image.new('P',(256,256),0);d=ImageDraw.Draw(im)
    d.rectangle((0,0,239,159),fill=3)
    d.polygon([(0,0),(103,0),(111,8),(111,101),(0,101)],fill=4)
    d.polygon([(0,0),(111,0),(111,27),(102,31),(0,31)],fill=0)
    d.polygon([(0,104),(103,104),(111,112),(111,151),(0,151)],fill=1)
    d.polygon([(112,8),(231,8),(239,16),(239,143),(231,151),(112,151)],fill=0)
    d.rectangle((112,16,231,143),fill=1)
    d.line((112,9,230,9),fill=4)
    d.polygon([(0,88),(16,72),(16,88),(32,72),(32,101),(0,101)],fill=5)
    d.line((0,155,239,155),fill=4)
    cols=[INK,PAPER,INK,MUTED,AMBER,(248,200,112),GREEN,(152,224,184),BLUE,
          (160,208,240),PAPER,INK,MUTED,VIOLET,PAPER,INK]
    tiles=[Image.new('P',(8,8),0) for _ in range(44)]
    for i,c in [(11,3),(17,1),(23,3),(43,4)]: tiles[i]=Image.new('P',(8,8),c)
    ids={tiles[i].tobytes():i for i in [0,11,17,23,43]};tm=[]
    for y in range(32):
        for x in range(32):
            tile=im.crop((8*x,8*y,8*x+8,8*y+8));key=tile.tobytes()
            if key not in ids: ids[key]=len(tiles);tiles.append(tile)
            tm.append(ids[key])
    assert len(tiles)<320, 'Bag graphics would overlap BG2 tilemap'
    atlas=Image.new('P',(128,((len(tiles)+15)//16)*8),0)
    for i,tile in enumerate(tiles):atlas.paste(tile,(i%16*8,i//16*8))
    save(OUT/'bag_background.png',atlas,cols)
    (OUT/'bag_background.bin').write_bytes(struct.pack('<1024H',*tm))
    text=[INK,INK,PAPER,(168,168,184),AMBER,RED,(180,180,180),GREEN,
          BLUE,(248,200,112),PAPER,VIOLET,(192,160,224),BLUE,RED,(248,144,160)]
    (OUT/'bag.pal').write_text('JASC-PAL\n0100\n32\n'+'\n'.join('%d %d %d'%c for c in cols+text)+'\n',newline='\n')

def storage_shell():
    # Keep every controller-addressed tile and glyph at its original index.
    # The source preview uses two palette banks; hardware pixels use the low nibble.
    im=Image.open(ROOT/'graphics/pokemon_storage/menu.png').point(lambda p:p&15)
    colors=[INK,INK,INK,MUTED,INK,BLUE,MUTED,INK,INK,BLUE,BLUE,
            INK,PAPER,PAPER,PAPER,BLUE]
    corner=Image.new('P',(8,8),1);d=ImageDraw.Draw(corner)
    d.polygon([(4,0),(7,0),(7,7),(0,7),(0,4)],fill=5)
    d.polygon([(5,2),(7,2),(7,7),(2,7),(2,5)],fill=14)
    edge=Image.new('P',(8,8),14);d=ImageDraw.Draw(edge)
    d.line((0,0,7,0),fill=1);d.line((0,1,7,1),fill=5)
    for tile,img in [(11,corner),(12,edge),(13,corner.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),
                     (28,Image.new('P',(8,8),14)),(29,Image.new('P',(8,8),14))]:
        im.paste(img,(tile%16*8,tile//16*8))
    save(OUT/'storage_menu.png',im,colors)
    palette(OUT/'storage_interface.pal',colors)
    gray=colors.copy();gray[5]=MUTED;gray[14]=MUTED
    palette(OUT/'storage_inactive.pal',gray)
    scroll=[INK,INK,PAPER,INK,BLUE,BLUE,RED,RED,INK,(40,40,48),INK]+[(0,0,0)]*5
    palette(OUT/'storage_canvas.pal',scroll)
    text=[INK,PAPER,INK,PAPER]+[(0,0,0)]*6+[PAPER,INK,MUTED,BLUE,PAPER,INK]
    palette(OUT/'storage_text.pal',text)
    party=[INK,INK,(24,96,136),INK,BLUE,(24,96,136),MUTED,BLUE,PAPER,
           PAPER,BLUE,(24,96,136),BLUE,INK,BLUE,INK]
    palette(OUT/'storage_party.pal',party)

def main():
    frames=OUT/'frames';frames.mkdir(parents=True,exist_ok=True)
    colors=[(0,0,0),PAPER,INK,MUTED,RED,(248,144,160),GREEN,(152,224,184),
            BLUE,(160,208,240),PAPER,INK,MUTED,RED,PAPER,INK]
    for i in range(1,21):
        cols=colors.copy();cols[13]=[RED,BLUE,AMBER,VIOLET,GREEN][(i-1)%5]
        save(frames/f'{i}.png',frame(cols[13]),cols)
    # The standard frame is often loaded with the standard text palette rather
    # than the frame's own palette. Its indices must use the shared roles.
    std=frame(RED)
    save(frames/'std.png',std,colors)
    palette(frames/'std.pal',colors)
    palette(frames/'dexnav_pal.pal',colors)
    for name in ['message_box','signpost']:
        original=Image.open(ROOT/f'graphics/text_window/{name}.png')
        # Keep all 14/5 tile masks and their order for message/sign renderers.
        remap={11:15,12:14,13:13,14:15} if name=='message_box' else {11:15,15:13}
        im=original.point(lambda p:remap.get(p,p))
        save(frames/f'{name}.png',im,colors)
    for i in range(1,5):
        original=ROOT/f'graphics/text_window/text_pal{i}.pal'
        cols=[tuple(map(int,l.split())) for l in original.read_text().splitlines()[3:]]
        cols[1:4]=[PAPER,INK,MUTED]
        cols[10:16]=colors[10:16]
        palette(frames/f'text_pal{i}.pal',cols)

    # Background uses its own BG1 charblock and palette; no window allocation
    # is changed. A quiet canvas, a left red rail and angular corner panels.
    im=Image.new('P',(256,256),1);d=ImageDraw.Draw(im)
    d.rectangle((0,0,239,159),fill=2)
    d.polygon([(0,0),(71,0),(0,71)],fill=0)
    d.polygon([(0,0),(14,0),(0,14)],fill=3)
    d.polygon([(150,159),(239,70),(239,159)],fill=4)
    d.polygon([(211,159),(239,131),(239,159)],fill=3)
    d.line((0,154,117,154),fill=5,width=1)
    d.line((0,157,114,157),fill=5,width=1)
    cols=[INK,PAPER,(232,232,240),RED,MUTED,(160,160,176)]+[(0,0,0)]*10
    tiles=[];ids={};tilemap=[]
    for y in range(32):
        for x in range(32):
            tile=im.crop((x*8,y*8,x*8+8,y*8+8));key=tile.tobytes()
            if key not in ids:ids[key]=len(tiles);tiles.append(tile)
            tilemap.append(ids[key])
    assert len(tiles)<224, 'BG tiles overlap main-menu BG map'
    atlas=Image.new('P',(128,((len(tiles)+15)//16)*8),1)
    for i,tile in enumerate(tiles):atlas.paste(tile,((i%16)*8,(i//16)*8))
    save(OUT/'main_background.png',atlas,cols)
    palette(OUT/'main_background.pal',cols)
    (OUT/'main_background.bin').write_bytes(struct.pack('<1024H',*tilemap))
    text=[PAPER,INK,INK,PAPER,RED,(248,144,160),GREEN,(152,224,184),BLUE,
          (160,208,240),PAPER,INK,PAPER]+[(0,0,0)]*3
    palette(OUT/'main_text.pal',text)
    option=[(0,0,0),PAPER,INK,PAPER,BLUE,PAPER,INK,PAPER,INK,BLUE]+[(0,0,0)]*6
    palette(OUT/'options_text.pal',option)
    bag_background()
    storage_shell()
    party_colors=[(0,0,0),(40,40,48),(32,32,40),PAPER,INK,RED,MUTED,
                  (40,40,48),(40,40,48),GREEN,(112,232,152),BLUE,
                  (144,208,240),RED,(248,144,160),PAPER]
    for hide_hp in [False, True]:
        card=Image.new('P',(112,32),0);cd=ImageDraw.Draw(card)
        cd.polygon([(4,0),(107,0),(111,4),(111,27),(107,31),(0,31),(0,4)],fill=4)
        cd.polygon([(4,1),(107,1),(110,4),(110,27),(106,30),(1,30),(1,4)],fill=1)
        cd.line((5,1,106,1),fill=5)
        cd.line((1,5,1,29),fill=5)
        if not hide_hp:
            cd.rectangle((31,24,80,28),fill=4)
        save(OUT/('party_card_no_hp.png' if hide_hp else 'party_card.png'),card,party_colors)
    print(f'Generated FireRed shared frames and main-menu background: {len(tiles)} tiles')

if __name__=='__main__':main()
