# Project Homepage Change Log

## 2026-06-18 - Document YouTube ASR Fallback

What changed: Updated the project README search example to mention local ASR
fallback for YouTube transcripts, and updated the `get-youtube-media` skill
documentation and catalog metadata with when and how to run local
NeMo/Nemotron ASR.

Why: Captionless YouTube videos need a restartable, documented fallback path
after manual and automatic YouTube captions are unavailable.

Validation performed:

- Compiled the updated YouTube media scripts with `py_compile`.
- Ran `python -m skillforge validate skills\get-youtube-media --json`.
- Rebuilt the SkillForge catalog with `python -m skillforge build-catalog --json`.
- Ran a full URL fallback smoke test that downloaded authorized audio and
  generated a local ASR transcript plus JSON sidecars.

Follow-up:

- Review ASR output before clinical, research, or quoted use because local ASR
  can introduce recognition errors.
