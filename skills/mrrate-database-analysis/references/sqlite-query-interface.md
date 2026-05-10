# MR-RATE SQLite Query Interface

Use this reference when the user asks natural-language questions against a
curated MR-RATE SQLite database, especially descriptive statistics, cohort
counts, source provenance, metadata coverage, co-occurrence summaries, or
private local record review.

## Query Ritual

Before writing SQL from a natural-language request:

1. Inspect the embedded LLM query dictionary.
2. Decide the counting unit: patient, study, report, label event, or metadata
   series.
3. Prefer helper views over raw tables.
4. Tell the user the SQL that was run and the counting caveat.
5. Keep raw reports, identifiers, metadata rows, and full patient-level exports
   out of public artifacts unless the user explicitly requests private local
   inspection.

Useful descriptor commands:

```text
python scripts/query_mr_rate_db.py --workspace . --describe intents
python scripts/query_mr_rate_db.py --workspace . --describe views
python scripts/query_mr_rate_db.py --workspace . --describe examples
python scripts/query_mr_rate_db.py --workspace . --describe rules
```

Use `--format json` or `--format csv` when Codex needs structured output for a
follow-up report.

## Helper Views

The project database may include these LLM-oriented views:

| View | Grain | Use for |
| --- | --- | --- |
| `v_query_positive_labels` | one positive label per report/study | Cohorts, label searches, and source paths. |
| `v_query_patient_summary` | one row per linked patient | Patient-level descriptive statistics and cohort flags. |
| `v_query_study_summary` | one row per study | Study review, missing metadata, and positive-label summaries. |
| `v_query_pathology_stats` | one row per pathology | Prevalence by reports, studies, and linked patients. |
| `v_query_patient_pathologies` | one row per patient/pathology | Patient-level label summaries and repeat studies. |
| `v_query_infarction_cases` | one infarction label per report/study | Fast infarction cohort queries. |
| `v_query_metadata_series` | one metadata row/series | Scan protocol, manufacturer, field strength, and sequence review. |
| `v_query_sequence_stats` | one row per sequence/protocol grouping | Sequence distribution and protocol coverage. |
| `v_query_cooccurring_pathologies` | one pathology pair per study | Co-occurrence summaries. |

If these objects are missing, inspect the raw schema and tell the user that the
workspace needs the newer MR-RATE DB builder/schema refresh before helper-view
queries will work.

## Descriptor Tables

Use these descriptor tables as the LLM-facing schema guide:

- `llm_query_view_catalog`
- `llm_query_column_catalog`
- `llm_query_intent_catalog`
- `llm_query_rules`
- `llm_query_examples`
- `v_llm_query_guide`

These descriptors are intentionally more useful to a language model than raw
SQL comments because SQLite does not preserve a portable COMMENT ON schema.

## Example SQL

Direct helper-view query:

```sql
SELECT pathology_name, linked_patients, positive_studies
FROM v_query_pathology_stats
ORDER BY linked_patients DESC, positive_studies DESC;
```

Filtered summary with explicit counting unit:

```sql
SELECT COUNT(DISTINCT patient_id) AS patients_with_infarction
FROM v_query_infarction_cases
WHERE patient_id IS NOT NULL;
```

Join with metadata helper view:

```sql
SELECT ms.sequence_family,
       ms.field_strength_t,
       COUNT(DISTINCT ic.study_uid) AS infarction_studies
FROM v_query_infarction_cases ic
JOIN v_query_metadata_series ms ON ms.study_uid = ic.study_uid
GROUP BY ms.sequence_family, ms.field_strength_t
ORDER BY infarction_studies DESC;
```

Private local record preview:

```sql
SELECT ps.patient_id,
       ss.study_uid,
       ss.positive_pathologies,
       ss.metadata_series_count,
       (
         SELECT group_concat(DISTINCT ms.sequence_family)
         FROM v_query_metadata_series ms
         WHERE ms.study_uid = ss.study_uid
       ) AS sequence_families,
       substr(r.impression, 1, 350) AS impression_preview
FROM v_query_patient_summary ps
JOIN v_query_study_summary ss ON ss.patient_id = ps.patient_id
JOIN v_query_positive_labels qpl
  ON qpl.study_id = ss.study_id
 AND qpl.pathology_name = 'Cerebral infarction'
LEFT JOIN reports r
  ON r.study_id = ss.study_id
 AND r.processing_stage = 'structured'
ORDER BY ps.patient_id, ss.study_uid
LIMIT 20;
```

## Schema Publishing

When the workspace includes a generated schema guide, prefer linking it over
restating the whole database structure:

```text
docs/schema/schema.md
```

Regenerate project-local schema docs with the workspace tool when available:

```text
python tools/generate_mr_rate_schema_docs.py --db research-data/mr-rate.sqlite --output docs/schema/schema.md
```

Do not publish the SQLite database, raw CSVs, report text, patient-level rows,
or local browser/session data as part of a SkillForge contribution.
