#!/usr/bin/env python3
"""Stage 3b: zoom a region of a frame. Usage: 05_zoom.py FRAME x0 y0 x1 y1 OUT [scale=3]"""
import sys
from PIL import Image
f,x0,y0,x1,y1,out = sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6]; s=int(sys.argv[7]) if len(sys.argv)>7 else 3
im=Image.open(f).crop((x0,y0,x1,y1)); im.resize((im.width*s,im.height*s),Image.LANCZOS).save(out,quality=92)
