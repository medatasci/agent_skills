# Skill Catalog

This file is the human-browsable SkillForge catalog for Codex users.
Skill behavior and discovery metadata live in each `skills/<skill-id>/SKILL.md`;
update this list when a skill is added, renamed, removed, or materially changed.

## Available Skills

### `skill-discovery-evaluation`

Evaluate and improve SkillForge skill discoverability before publication so
humans, agents, local search, generated catalog pages, and peer catalogs can
find the right skill.

Use it when you are creating, importing, or updating a SkillForge skill and
want to improve `SKILL.md` metadata, trigger language, aliases, example prompts,
search phrases, and publication-readiness evidence.

```text
Use $skill-discovery-evaluation to evaluate huggingface-datasets for publication,
improve its search metadata if needed, rebuild the catalog, and show the
SkillForge evaluation report.
```

### `huggingface-datasets`

Inspect Hugging Face datasets with read-only Dataset Viewer API calls for
splits, rows, search, filters, parquet URLs, sizes, and statistics.

Use it when you need to understand what is inside a Hugging Face dataset without
training a model, uploading data, or modifying a Hub repository.

```text
Use $huggingface-datasets to list the configs and splits for stanfordnlp/imdb,
preview the first rows, and explain the available columns.
```

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
