# Skill Catalog

This file is the source of truth for the Agent Skills Marketplace catalog.
Update this file when a skill is added, renamed, removed, or materially changed.

## Available Skills

### `get-youtube-media`

Search YouTube for learning or research topics, collect captions/transcripts,
save restartable retrieval queues, and optionally download MP4 or audio files
for videos the user is authorized to save.

Use it when you want to turn YouTube videos or search results into reusable
local transcript artifacts.

```text
Use $get-youtube-media to search YouTube for "how to read an MRI for brain lesions",
save a restartable queue for the top 10 results, and transcribe the top 3 videos.
```

### `project-retrospective`

Create or update a durable project retrospective log. The skill records what you
asked, what Codex understood, what Codex did, key findings, your response when
available, and what went right, wrong, or was missed.

Use it when you want a project to remember more than the final code diff.

```text
Use $project-retrospective to update this project's retrospective.

Create or update a retrospective log for this project. Capture what I asked,
what you understood, what you did, the key findings, my response if available,
and what went right, wrong, or was missed. If there is no existing retrospective,
create one at retrospectives/interaction_log.md. Keep it concise, candid, and
useful for someone returning to this project later.
```
