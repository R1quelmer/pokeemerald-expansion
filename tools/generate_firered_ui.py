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
    option=[(0,0,0),PAPER,BLUE,(24,96,136),(128,208,240),BLUE,INK,MUTED,INK,BLUE]+[(0,0,0)]*6
    palette(OUT/'options_text.pal',option)
    print(f'Generated FireRed shared frames and main-menu background: {len(tiles)} tiles')

if __name__=='__main__':main()
