#!/usr/bin/env python3
"""Stage 3: build one image per scene (start|mid|end side by side) so Claude can view each scene in one look."""
import sys, json, pathlib
from PIL import Image, ImageDraw
out = pathlib.Path(sys.argv[1]); idx = json.load(open(out/"scene_index.json"))
(out/"sheets").mkdir(exist_ok=True)
for sc in idx["scenes"]:
    ims = [Image.open(out/f) for f in sc["frames"]]
    w,h = ims[0].size; sheet = Image.new("RGB",(w*3+20,h+30),"white"); d = ImageDraw.Draw(sheet)
    for k,(im,lab) in enumerate(zip(ims,("start","mid","end"))):
        sheet.paste(im,(k*(w+10),30)); d.text((k*(w+10)+5,8),f"scene {sc['scene']} {lab} ({sc['start']}-{sc['end']}s)",fill="black")
    sheet.save(out/"sheets"/f"scene{sc['scene']:02d}.jpg", quality=85)
print("sheets done")
