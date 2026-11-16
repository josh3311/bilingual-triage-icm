#!/usr/bin/env python3
"""Stage 2: timestamped transcript. Usage: 02_transcribe.py VIDEO OUTDIR  (writes transcript.json, transcript.txt)"""
import sys, json, pathlib
from faster_whisper import WhisperModel
video, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(video, vad_filter=True, word_timestamps=False)
rows = [{"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip()} for s in segs]
json.dump({"language":info.language,"segments":rows}, open(out/"transcript.json","w"), indent=2)
open(out/"transcript.txt","w").write("\n".join(f"[{r['start']:6.1f}-{r['end']:6.1f}] {r['text']}" for r in rows))
print(info.language, len(rows), "segments")
