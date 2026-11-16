#!/usr/bin/env python3
"""Stage 4: write scene_notes.md skeleton, with the transcript lines that fall inside each scene, for Claude to fill after LOOKING at each sheet."""
import sys, json, pathlib
out = pathlib.Path(sys.argv[1]); idx = json.load(open(out/"scene_index.json"))
tr = json.load(open(out/"transcript.json"))["segments"] if (out/"transcript.json").exists() else []
L = ["# Scene notes\n"]
for sc in idx["scenes"]:
    said = [f"[{t['start']}s] {t['text']}" for t in tr if t["end"]>=sc["start"] and t["start"]<=sc["end"]]
    L += [f"## Scene {sc['scene']} ({sc['start']}s-{sc['end']}s)", f"Sheet: sheets/scene{sc['scene']:02d}.jpg",
          "**Said:** " + (" / ".join(said) or "(silence or no transcript)"),
          "**On screen (only what is readable):** TODO", "**Action (what changed start->end):** TODO",
          "**Numbers / labels read exactly:** TODO", "**Unreadable / unsure:** TODO", "**Purpose of this scene:** TODO\n"]
open(out/"scene_notes.md","w").write("\n".join(L)); print("skeleton written")
