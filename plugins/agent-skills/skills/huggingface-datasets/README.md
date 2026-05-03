# Hugging Face Datasets

Skill ID: `huggingface-datasets`

Inspect public Hugging Face datasets safely through read-only Dataset Viewer
workflows: configs, splits, rows, filters, search, statistics, and parquet URLs.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/huggingface-datasets

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Data, Research, AI/ML

Collection context:
This skill belongs in SkillForge's Data, Research, and AI/ML collection because
it helps agents inspect public datasets before analysis, modeling, or
documentation work.

## What This Skill Does

Hugging Face Datasets supports read-only inspection of public datasets through
the Hugging Face Dataset Viewer API. It helps Codex list configs and splits,
preview rows, inspect columns, search or filter rows, check dataset sizes, and
find parquet URLs without training a model or modifying a Hub repository.

## Why You Would Call It

Call this skill when:

- You have a Hugging Face dataset ID and want to understand what is in it.
- You need configs, splits, rows, columns, or parquet URLs before analysis.
- You want read-only dataset reconnaissance without writing to the Hub.

Use it to:

- List dataset configs, subsets, splits, and row counts.
- Preview rows and explain available columns.
- Search or filter a dataset with Dataset Viewer parameters.
- Retrieve parquet file URLs for reproducible downstream work.
- Summarize what a dataset appears to contain from metadata and sample rows.

Do not use it when:

- The user wants to train a model.
- The user wants to upload, delete, or manage Hub repositories.
- The user needs private dataset access or authenticated write operations.

## Keywords

Hugging Face, datasets, HF datasets, Dataset Viewer API, configs, splits, rows,
columns, filters, search, parquet, public dataset metadata, AI/ML, data
inspection.

## Search Terms

Hugging Face datasets, HF datasets, Dataset Viewer API, dataset preview, list
splits, dataset configs, row preview, parquet URLs, public dataset metadata,
dataset search, dataset filter, inspect a dataset, what is in this Hugging Face
dataset.

## How It Works

The skill keeps the workflow read-only:

1. Resolve the dataset ID and clarify config, subset, split, or row needs.
2. Inspect available configs and splits through Dataset Viewer endpoints.
3. Preview rows, columns, or metadata with small targeted requests.
4. Search or filter rows only when the user asks for that view.
5. Retrieve parquet URLs or size statistics when useful for downstream work.
6. Summarize what the dataset contains and explain API errors or unavailable
   viewer data clearly.

It should prefer small requests and avoid turning a data-inspection task into a
training, upload, or repository-management task.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install huggingface-datasets --scope global
python -m skillforge install huggingface-datasets --scope project --project .
python -m skillforge search "hugging face dataset rows parquet viewer" --json
python -m skillforge evaluate huggingface-datasets --json
```

Skill-specific APIs, scripts, or options:

- Hugging Face dataset ID.
- Optional config or subset.
- Optional split.
- Optional row offset and row limit.
- Optional search query or filter expression.
- Optional parquet URL request.

Configuration:

- No credential is required for public Dataset Viewer inspection.
- Network access to Hugging Face Dataset Viewer endpoints is required.

## Inputs And Outputs

Inputs can include:

- Hugging Face dataset ID.
- Optional config or subset.
- Split.
- Row offset and row limit.
- Search query.
- Filter expression.
- Parquet request.

Outputs can include:

- Dataset metadata.
- Configs and splits.
- Row previews.
- Column summaries.
- Search or filter results.
- Size statistics.
- Parquet URLs.

Output locations:

- Chat summary by default.
- User-requested local notes or files when explicitly requested.

## Limitations

Known limitations:

- The intended workflow is Dataset Viewer inspection, not model training,
  dataset uploading, or Hugging Face Hub repository management.
- Private or gated datasets require an appropriate token; the skill should not
  ask for credentials unless the user explicitly chooses that path.
- Dataset Viewer availability varies by dataset, config, and split. Some large
  or unusual datasets may not expose rows, statistics, filters, or parquet URLs.
- Row previews and searches should stay small and targeted; bulk extraction is
  better handled by a dedicated data pipeline.

Choose another skill when:

- The task is to collect YouTube or media evidence rather than inspect a
  Hugging Face dataset.
- The task is to preserve project decisions or lessons after a dataset
  investigation.

## Examples

Beginner example:

```text
Use huggingface-datasets to inspect stanfordnlp/imdb, list configs and splits,
preview a few rows, and explain the columns.
```

Task-specific example:

```text
Use huggingface-datasets to inspect MR-RATE and describe what is in the dataset.
```

Safety-aware or bounded example:

```text
Use huggingface-datasets only for read-only metadata and row preview. Do not
train a model or modify anything on the Hub.
```

Troubleshooting or refinement example:

```text
Use huggingface-datasets to explain why the Dataset Viewer request failed and
suggest the next read-only query to try.
```

## Help And Getting Started

Start with:

```text
Inspect <dataset-id>, list its configs and splits, preview a few rows, and tell
me what the columns mean.
```

Provide:

- The Hugging Face dataset ID.
- A config, subset, split, filter, or search term if you already know one.

Ask for help when:

- The Dataset Viewer API returns an error.
- A dataset has many configs and you are not sure which to inspect.
- You need parquet URLs or split sizes for downstream work.

## How To Call From An LLM

Direct prompt:

```text
Use huggingface-datasets to inspect <dataset-id>.
```

Task-based prompt:

```text
Use huggingface-datasets to show the available configs and splits, preview rows,
summarize columns, and report any parquet URLs for <dataset-id>.
```

Guarded prompt:

```text
Use huggingface-datasets, but only perform read-only public Dataset Viewer
requests and do not train, upload, or modify anything.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps inspect Hugging Face datasets.
Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "hugging face parquet dataset preview" --json
```

Show skill metadata:

```text
python -m skillforge info huggingface-datasets --json
```

Install the skill into Codex:

```text
python -m skillforge install huggingface-datasets --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate huggingface-datasets --json
```

Remove the installed skill:

```text
python -m skillforge remove huggingface-datasets --scope global --yes
```

## Trust And Safety

Risk level:
low

Permissions:

- Read-only network access to public Hugging Face Dataset Viewer endpoints.
- No credentials required for public dataset inspection.
- No Hub repository write permissions.

Data handling:
The skill retrieves public dataset metadata, row previews, split information,
and parquet URLs. It should not upload data, access private datasets, store
credentials, or modify Hub repositories.

Writes vs read-only:
The skill is read-only against Hugging Face services. Local writes should be
limited to user-requested notes, summaries, or saved command outputs.

External services:
Hugging Face Dataset Viewer API and public Hugging Face dataset metadata pages
when needed.

Credentials:
No credential is required for the intended public read-only workflow.

User approval gates:

- Ask before writing local output files beyond a chat summary.
- Stop if the user asks for private dataset access, uploads, deletes, or Hub
  repository management.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Send feedback when:

- A dataset query is slow.
- A Dataset Viewer error is unclear.
- A split or config is hard to choose.
- The examples do not match your data inspection workflow.

Promptable feedback:

```text
Send feedback on huggingface-datasets that choosing the right config was
confusing for a dataset with many subsets.
```

## Contributing

Contribution path:
Pull requests are welcome for clearer Dataset Viewer workflows, better examples,
more precise search terms, safer error handling, and updated API references.

Before opening a pull request:

- Update `skills/huggingface-datasets/SKILL.md` and this README only for
  behavior or documentation that is true for the skill.
- Run `python -m skillforge build-catalog`.
- Run `python -m skillforge evaluate huggingface-datasets --json` and include
  any remaining gaps in the PR notes.

## Author

Marc Edgar / medatasci

Maintainer status:
SkillForge-maintained example skill.

## Citations

Relevant method and API references:

- Hugging Face Dataset Viewer documentation:
  https://huggingface.co/docs/dataset-viewer/index
- Hugging Face Datasets documentation:
  https://huggingface.co/docs/datasets/index

## Related Skills

- `get-youtube-media`: inspect video and caption sources instead of Hugging
  Face datasets.
- `project-retrospective`: capture dataset investigation notes and decisions.
- `skill-discovery-evaluation`: improve this skill's README, examples,
  metadata, and search behavior.
