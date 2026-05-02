# Research Hub YouTube Workflow Patterns

Use these patterns when a YouTube task is part of a research corpus, evidence
hub, or learning-source evaluation workflow rather than a one-off transcript.

## Search Strategy

- Start with disease- or finding-aligned queries, not only broad topic queries.
- Search both diagnosis names and imaging signs.
- Prefer radiology, neuroradiology, academic, CME, Radiopaedia-style, or
  image-interpretation teaching sources.
- Treat patient-facing videos as lower priority unless the task is communication
  or plain-language explanation.
- Record weak or zero-result searches instead of hiding them; they are useful
  evidence that written sources should carry that topic.

Useful query pattern examples:

- `<condition> MRI <key sequence> radiology lecture`
- `<condition> MRI differential radiology tutorial`
- `<finding> versus <mimic> MRI DWI FLAIR`
- `<vascular finding> MRA SWI GRE neuroradiology`

## Candidate Scoring

When ranking videos for research value, score candidates on a 25-point scale:

- 0 to 5: direct match to target labels or research questions.
- 0 to 5: radiology/neuroradiology authority.
- 0 to 5: image interpretation depth.
- 0 to 5: differential diagnosis usefulness.
- 0 to 5: transcript or teaching quality.

Promote videos that teach reusable decision rules, sequence-specific findings,
and discriminating branches. Demote videos that are high-view but mostly
patient education, news, advertising, or general wellness content.

## Transcript-First Evidence Gate

Fetch transcripts before downloading MP4s. Download video only after transcript
review shows direct rule-supporting teaching content.

The research hub used this policy:

```text
Download MP4 only after transcript evidence contains direct rule-supporting
quote text inside a 10-second caption window.
```

For evidence-backed workflows, keep:

- Search query.
- Queue path.
- Source ID.
- Title, channel, URL.
- YouTube license: `creativeCommon`, `youtube`, or `unknown`.
- Local transcript path.
- Local segments JSON path.
- Optional local video path.
- Timestamp start/end when a quote or teaching window supports a rule.
- A short note on what the source teaches and what it does not support.

## Timestamp Windows

Use the `segments.json` output to create caption windows around evidence:

- Use 10-second windows by default.
- Capture the caption text overlapping each window.
- Mark whether the direct quote appears inside the window.
- Prefer timestamped YouTube links with `t=` offsets when citing a source.

If visual evidence is needed, extract frames only from locally archived MP4/WebM
files after the transcript gate has passed. A useful frame request should
include `video_path`, `output_path`, `time_seconds`, and target width.

## Coverage And Confidence

Do not treat YouTube as clinical authority by itself. Use YouTube for teaching
heuristics and pattern-recognition examples, then validate formal claims against
written radiology references, guidelines, review articles, or datasets.

For each rule or label, record:

- Whether YouTube coverage is strong, partial, weak, or absent.
- Whether the source directly supports the discriminating branch.
- Whether written evidence is needed because YouTube coverage is too broad or
  missing.
- Confidence as educational/heuristic unless externally validated.

Common weak YouTube areas from the MRI research hub:

- Narrow mimic distinctions such as lacunar infarct versus perivascular space.
- Cerebral microbleed distribution by etiology.
- Incidental variants and uncommon cystic/extra-axial findings.
- Hyperostosis, mega cisterna magna, choroid plexus cyst, and some sellar
  variants.

## Operational Defaults

- Use queue files for any multi-video retrieval.
- Use `--license creativeCommon` or `--require-creative-commons` when reuse,
  redistribution, remixing, or publication beyond local research notes is part
  of the workflow. Provide `YOUTUBE_API_KEY` for reliable license checks; treat
  `unknown` as not reusable.
- Keep request sleeps nonzero for batches.
- Keep raw captions and segment JSON; they are needed for later timestamp
  windows.
- Keep search-result JSON/Markdown next to the queue file.
- Keep selected transcripts in a separate folder from broad search transcripts.
- Use stable source IDs when adding videos to a registry, such as
  `yt-brain-tumors-metastases-gbm` or `yt-dwi-adc`.
