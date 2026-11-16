#!/usr/bin/env python3
"""Stage 1: split a video into scenes and save frames. Usage: 01_scenes.py VIDEO OUTDIR [threshold]"""
import sys, json, subprocess, pathlib
from scenedetect import detect, ContentDetector
video, out = sys.argv[1], pathlib.Path(sys.argv[2])
thr = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0   # low = screen recordings change subtly
(out/"frames").mkdir(parents=True, exist_ok=True)
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",video]))
scenes = [(s.get_seconds(), e.get_seconds()) for s,e in detect(video, ContentDetector(threshold=thr, min_scene_len=15))]
if not scenes: scenes = [(0.0, dur)]
# Safety net: split any scene longer than 4s so slow UI changes are not missed
final = []
for s,e in scenes:
    n = max(1, int((e-s)//4 + (1 if (e-s)%4>1 else 0)))
    step = (e-s)/n
    final += [(s+i*step, s+(i+1)*step) for i in range(n)]
index = []
for i,(s,e) in enumerate(final,1):
    for tag,t in (("start",s+0.1),("mid",(s+e)/2),("end",e-0.1)):
        fn = out/"frames"/f"scene{i:02d}_{tag}.jpg"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{max(t,0):.2f}","-i",video,"-frames:v","1","-q:v","3",str(fn)],check=True)
    index.append({"scene":i,"start":round(s,2),"end":round(e,2),
                  "frames":[f"frames/scene{i:02d}_{t}.jpg" for t in ("start","mid","end")]})
json.dump({"video":video,"duration":dur,"scenes":index}, open(out/"scene_index.json","w"), indent=2)
print(f"{len(index)} scenes -> {out}/scene_index.json")
