---
name: video-to-scenes
description: Use when a screen recording or tutorial video must be understood accurately. Splits it into scenes, extracts frames and a timestamped transcript, has Claude LOOK at each scene, then builds a verified scene-by-scene understanding and a skill/script spec from it. Do not rely on transcript alone.
---
# Video-to-Scenes (ICM)
**Why:** Claude cannot reliably understand a video from audio/transcript alone. ICM = Interpreted Context Methodology: break the video into small, labelled chunks (context), have Claude interpret each chunk, then synthesise.

## Folders (the "context")
- `scripts/` numbered tools. `stages/` one instruction file per stage. `templates/` output shapes.
- Work folder per video: `work/<video-name>/` holds `frames/`, `sheets/`, `scene_index.json`, `transcript.*`, `scene_notes.md`, `understanding.md`.

## Stages (run in order, do not skip)
1. `scripts/01_scenes.py VIDEO WORK` - scene cuts + start/mid/end frames. MUST also split any scene > 4s.
2. `scripts/02_transcribe.py VIDEO WORK` - timestamped speech. If the model cannot download, mark transcript NOT AVAILABLE; never invent speech.
3. `scripts/03_contact_sheets.py WORK` - one image per scene.
4. `scripts/04_notes_skeleton.py WORK` - empty notes with the matching speech.
5. **LOOK** at every `sheets/sceneNN.jpg` with the Read tool. Fill `scene_notes.md`. See `stages/05_read_scenes.md`.
6. Synthesise `understanding.md` from `templates/understanding.md`. Then check it with `stages/06_verify.md`.
7. Turn the verified understanding into the skill / script / extraction rules for that kind of video.

## Lessons from the first test (video1)
- Screen recordings and filmed phones have few hard cuts: the scene detector found 1 scene, so the 4-second split did all the work. Keep that rule.
- Small phone text is unreadable in a normal frame. ADD a zoom step: crop the region and upscale 3x (PIL), then read the crop.
- Speech model download can be blocked by the network. Fallback: say transcript NOT AVAILABLE; use burned-in captions and zoomed frames. Never invent speech.
- Always compare start vs end of each scene: the changing number is the story.
- Judge claims by how the real system works, not by what the video says. A demo that matches is not proof.

## Rules
- MUST write only what is visible or audible. Unreadable = write `UNREADABLE`. MUST NOT guess numbers, names or tickers.
- MUST quote on-screen numbers exactly as shown, with the scene number.
- MUST separate **seen**, **heard**, **inferred**. Inferred items are labelled `INFERRED`.
- MUST NOT merge scenes before each has its own note.
- If speech and screen disagree, write both and flag `CONFLICT`.
