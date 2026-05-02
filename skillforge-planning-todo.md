# SkillForge TODO

Updated: 2026-05-02 13:49 America/New_York

Source of truth:

- Product requirements: `requirements.md`
- User entrypoint: `README.md`
- Peer discovery seed: `peer-catalogs.json`

## Now

- [x] **Write MVP requirements**
  - Why: The build needs a clear contract before implementation.
  - Artifact: `requirements.md`

- [x] **Separate README from planning docs**
  - Why: README should be a user-facing entrypoint, not a requirements document.
  - Artifact: `README.md`
  - Decision: Use "Codex Promptable" for natural-language usage and "CLI API" for deterministic tool calls.

- [x] **Seed peer catalog list**
  - Why: MVP federation is a simple list of known peer skill libraries.
  - Artifact: `peer-catalogs.json`

- [ ] **Define generated catalog schema**
  - Why: The Python tool, README/site generation, peer search, and install flow all depend on this contract.
  - Next action: Draft `skills.json`, per-skill metadata JSON, checksum fields, source URL fields, and Codex install target fields.

- [ ] **Decide final skill storage layout**
  - Why: Current repo still contains older plugin-oriented paths; SkillForge needs a clean MVP catalog layout.
  - Next action: Choose whether canonical skills live under `skills/<skill-id>/` or another simple root-level path.

## Next

- [ ] **Scaffold `skillforge` Python package**
  - Why: MVP install/search/upload flow is `python -m skillforge`, not a Codex plugin marketplace command.
  - Required commands: `validate`, `upload`, `download`, `search`, `info`, `install`, `list`, `doctor`.

- [ ] **Implement local skill validation**
  - Why: Upload and install both depend on structural validation.
  - Checks: `SKILL.md` exists, valid frontmatter, required metadata, folder/name match, referenced files exist, suspicious file types flagged.

- [ ] **Implement catalog generation**
  - Why: Agents need machine-readable discovery.
  - Outputs: `skills.json`, per-skill JSON metadata, optional `llms.txt`.

- [ ] **Implement Codex install**
  - Why: The first useful product behavior is finding and installing a skill into Codex.
  - Scope: support `--scope global` and `--scope project --project <path>`.

- [ ] **Implement search**
  - Why: SkillForge must support both exact install and task-based discovery.
  - Scope: exact ID, keyword/task search, source catalog, local catalog first; peer catalogs after local search works.

## Watch

- [ ] **Review HTML catalog draft**
  - Why: Website comes after README and schema, but the mockup can guide generated catalog fields.
  - Artifact: `docs/skillforge-catalog-draft.html`

- [ ] **Plan peer catalog adapters**
  - Why: Some peers publish static indexes; others are GitHub repos that need adapter logic.
  - Next action: Classify each `peer-catalogs.json` entry as static index, GitHub skill repo, GitHub catalog repo, or disabled.

- [ ] **Backlog trust/risk model**
  - Why: Important for company use, but explicitly not MVP.
  - Later: risk labels, trust labels, dynamic risk evaluation, human review, enterprise allowlists.

- [ ] **Backlog non-Codex platforms**
  - Why: NeMoClaw and Cursor matter later, but Codex is MVP.
  - Later: NeMoClaw packaging, Cursor install targets, multi-agent compatibility badges.

- [ ] **White paper track**
  - Why: The MVP can become the concrete reference implementation for the white paper.
  - Later: outline, standards landscape, reference architecture, NVIDIA enterprise extension.

