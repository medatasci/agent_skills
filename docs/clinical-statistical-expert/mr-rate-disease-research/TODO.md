# MR-RATE Disease Research Task List

Created: 2026-05-07T23:39:48Z

Source of truth:
- https://github.com/forithmus/MR-RATE/blob/main/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/06_pathology_classification/data/pathologies_snomed_map.json
- Source modified date reported by GitHub connector: 2026-04-01T12:21:27Z

## Count Check

The prompt refers to 32 disease categories. The current MR-RATE mapping file contains 37 mapped categories. This task list includes all 37 categories so that source-file categories are not silently dropped. If a later decision restricts the scope to 32, update `manifest.json` with the exclusion rationale.

## Restart Rules

- Treat `manifest.json` as the authoritative state file.
- Work one disease and one phase at a time.
- After each disease phase, update status, run log, source evidence, and gaps.
- Existing chapters for cerebral infarction and gliosis should be updated rather than overwritten.
- Do not claim a disease is mature until source depth, figure review depth, differential matrix, and template review are recorded.

## Global Phases

1. scope-and-query-pack
2. authoritative-source-discovery
3. source-review-and-notes
4. image-candidate-review
5. differential-matrix
6. chapter-draft-or-update
7. template-review
8. html-preview
9. evaluate-and-gap-list

## Disease Work Queue

| Rank | Status | Disease / Finding | Original MR-RATE Name | Cluster | Ontology | Research Plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | final_thorough_research_target_met_needs_human_review | Cerebral infarction | Ischemic infarct | ischemic_vascular | 432504007 | `diseases/cerebral-infarction/research-plan.md` |
| 2 | final_thorough_research_target_met_needs_human_review | Lacunar infarct | Lacunar infarct | ischemic_vascular | 81037000 | `diseases/lacunar-infarct/research-plan.md` |
| 3 | final_thorough_research_target_met_needs_human_review | Watershed infarct | Watershed infarct | ischemic_vascular | 47559000 | `diseases/watershed-infarct/research-plan.md` |
| 4 | final_thorough_research_target_met_needs_human_review | Cerebral hemorrhage | Intracerebral hemorrhage | hemorrhagic_vascular | 274100004 | `diseases/cerebral-hemorrhage/research-plan.md` |
| 5 | final_thorough_research_target_met_needs_human_review | Silent micro-hemorrhage of brain | Cerebral microbleeds | hemorrhagic_vascular | 723857007 | `diseases/silent-micro-hemorrhage-of-brain/research-plan.md` |
| 6 | final_thorough_research_target_met_needs_human_review | Cavernous hemangioma | Cavernous malformation | hemorrhagic_vascular | 416824008 | `diseases/cavernous-hemangioma/research-plan.md` |
| 7 | final_thorough_research_target_met_needs_human_review | Subdural intracranial hemorrhage | Extra-axial hematoma | hemorrhagic_vascular | 35486000 | `diseases/subdural-intracranial-hemorrhage/research-plan.md` |
| 8 | final_thorough_research_target_met_needs_human_review | Intracranial aneurysm | Intracranial aneurysm | hemorrhagic_vascular | 128609009 | `diseases/intracranial-aneurysm/research-plan.md` |
| 9 | final_thorough_research_target_met_needs_human_review | Metastatic malignant neoplasm to brain | Brain metastasis | neoplasm_mass | 94225005 | `diseases/metastatic-malignant-neoplasm-to-brain/research-plan.md` |
| 10 | final_thorough_research_target_met_needs_human_review | Intracranial meningioma | Meningioma | neoplasm_mass | 302820008 | `diseases/intracranial-meningioma/research-plan.md` |
| 11 | final_thorough_research_target_met_needs_human_review | Glioma | Glioma | neoplasm_mass | 393564001 | `diseases/glioma/research-plan.md` |
| 12 | final_thorough_research_target_met_needs_human_review | Schwannoma | Schwannoma | neoplasm_mass | 985004 | `diseases/schwannoma/research-plan.md` |
| 13 | final_thorough_research_target_met_needs_human_review | Pituitary adenoma | Pituitary adenoma | neoplasm_mass | 254956000 | `diseases/pituitary-adenoma/research-plan.md` |
| 14 | authoritative_source_discovery_started | Lipoma of brain | Intracranial lipoma | neoplasm_mass | 15863451000119107 | `diseases/lipoma-of-brain/research-plan.md` |
| 15 | not_started | Arachnoid cyst | Arachnoid cyst | cyst_developmental_anatomic_variant | 33595009 | `diseases/arachnoid-cyst/research-plan.md` |
| 16 | not_started | Cyst of pineal gland | Pineal cyst | cyst_developmental_anatomic_variant | 413099000 | `diseases/cyst-of-pineal-gland/research-plan.md` |
| 17 | not_started | Rathke's pouch cyst | Rathke cleft cyst | cyst_developmental_anatomic_variant | 52859009 | `diseases/rathke-s-pouch-cyst/research-plan.md` |
| 18 | not_started | Choroid plexus cyst | Choroid plexus cyst | cyst_developmental_anatomic_variant | 230790004 | `diseases/choroid-plexus-cyst/research-plan.md` |
| 19 | not_started | Mega cisterna magna | Mega cisterna magna | cyst_developmental_anatomic_variant | 447739003 | `diseases/mega-cisterna-magna/research-plan.md` |
| 20 | not_started | Structure of cave of septum pellucidum | Cavum septum pellucidum | cyst_developmental_anatomic_variant | 74968005 | `diseases/structure-of-cave-of-septum-pellucidum/research-plan.md` |
| 21 | not_started | Empty sella syndrome | Empty sella | cyst_developmental_anatomic_variant | 237722004 | `diseases/empty-sella-syndrome/research-plan.md` |
| 22 | not_started | Chiari malformation | Chiari malformation | cyst_developmental_anatomic_variant | 253184003 | `diseases/chiari-malformation/research-plan.md` |
| 23 | not_started | Demyelinating disease of central nervous system | Demyelinating disease | white_matter_parenchymal_sequelae | 6118003 | `diseases/demyelinating-disease-of-central-nervous-system/research-plan.md` |
| 24 | existing_chapter_needs_cross_disease_update | Gliosis | White matter gliosis | white_matter_parenchymal_sequelae | 81415000 | `diseases/gliosis/research-plan.md` |
| 25 | not_started | Encephalomalacia | Encephalomalacia | white_matter_parenchymal_sequelae | 58762006 | `diseases/encephalomalacia/research-plan.md` |
| 26 | not_started | Cerebral edema | Cerebral edema | white_matter_parenchymal_sequelae | 2032001 | `diseases/cerebral-edema/research-plan.md` |
| 27 | not_started | Cerebral atrophy | Cerebral atrophy | white_matter_parenchymal_sequelae | 278849000 | `diseases/cerebral-atrophy/research-plan.md` |
| 28 | not_started | Cerebellar degeneration | Cerebellar atrophy | white_matter_parenchymal_sequelae | 95646004 | `diseases/cerebellar-degeneration/research-plan.md` |
| 29 | not_started | Ventriculomegaly | Ventriculomegaly | white_matter_parenchymal_sequelae | 413808003 | `diseases/ventriculomegaly/research-plan.md` |
| 30 | not_started | Herniation of nucleus pulposus | Disc herniation | spine | 84857004 | `diseases/herniation-of-nucleus-pulposus/research-plan.md` |
| 31 | not_started | Spinal cord compression | Spinal cord compression | spine | 71286001 | `diseases/spinal-cord-compression/research-plan.md` |
| 32 | not_started | Spinal stenosis | Spinal canal stenosis | spine | 76107001 | `diseases/spinal-stenosis/research-plan.md` |
| 33 | not_started | Foraminal Spinal Stenosis | Foraminal stenosis | spine | http://www.radlex.org/RID/#RID5034 | `diseases/foraminal-spinal-stenosis/research-plan.md` |
| 34 | not_started | Hemangioma of vertebral column | Vertebral hemangioma | spine | 448232005 | `diseases/hemangioma-of-vertebral-column/research-plan.md` |
| 35 | not_started | Mastoiditis | Mastoiditis | temporal_bone_skull | 52404001 | `diseases/mastoiditis/research-plan.md` |
| 36 | not_started | Chronic mastoiditis | Chronic mastoiditis | temporal_bone_skull | 80645004 | `diseases/chronic-mastoiditis/research-plan.md` |
| 37 | not_started | Hyperostosis of skull | Calvarial thickening | temporal_bone_skull | 788954009 | `diseases/hyperostosis-of-skull/research-plan.md` |

## Per-Disease Definition Of Done

- Research plan completed from the clinical-statistical-expert template.
- At least one checkpoint records what was done, what worked, what did not work, risks, and next action.
- Authoritative broad sources are identified and source evidence is recorded.
- Differential diagnosis is ordered roughly from most common to least common in the relevant MR imaging context.
- Differential diagnosis explicitly contrasts the target with relevant categories from the MR-RATE source set.
- Imaging appearance is written in radiology-report style and distinguishes Findings-style language from Impression-style synthesis.
- Disease-course, treatment/response/outcome context, covariates/confounders, and statistical implications are addressed or marked not applicable.
- Image evidence candidates are reviewed and reuse status is recorded.
- Chapter or draft output is checked against templates and rendered for human review.

## Latest Checkpoint

- 2026-05-08T01:59:47Z: Cerebral hemorrhage source-backed chapter, source manifest, figure manifest, differential matrix, and HTML preview were completed for expert review.
- 2026-05-08T02:13:54Z: Silent micro-hemorrhage of brain source-backed draft, source review, figure manifest, video manifest, differential matrix, and HTML preview were created; current counts are 18/50 sources, 10/25 figures, and 6/15 videos.
- 2026-05-08T02:57:27Z: Cerebral infarction maturity pass expanded evidence to 24/50 sources, 19/25 figures, and 10/15 videos; still not final-ready.
