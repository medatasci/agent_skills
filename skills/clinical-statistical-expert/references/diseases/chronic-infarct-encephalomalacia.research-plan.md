# Chronic Infarct / Encephalomalacia Disease Chapter Research Plan

Use this as the first prospective test of the
`clinical-statistical-expert` disease chapter workflow.

Unlike `gliosis.research-plan.backtest.md`, this file is intended to precede
the disease chapter and guide source collection, evidence extraction, content
drafting, and review.

## Scope Definition

- Disease or finding: chronic infarct / encephalomalacia in the brain.
- Brain-specific scope: chronic postischemic tissue loss, encephalomalacia,
  gliotic margin or surrounding gliosis, ex vacuo change, vascular territory or
  watershed distribution, chronic hemorrhagic residua, interval stability, and
  mimic-aware distinction from nonspecific gliosis and mass-like lesions.
- Primary imaging modality: MRI.
- Important secondary modalities: CT, DWI/ADC, FLAIR, T1, T2, SWI/GRE,
  contrast-enhanced MRI, vascular imaging, perfusion imaging, and prior imaging.
- Included variants, phenotypes, stages, or subtypes: chronic territorial
  infarct, lacunar infarct, watershed infarct, chronic hemorrhagic infarct,
  cystic encephalomalacia, cortical laminar necrosis when relevant, Wallerian
  degeneration when source support is present, and chronic postsurgical or
  posttraumatic tissue loss only when needed for mimic comparison.
- Excluded related entities: acute stroke diagnosis, emergent triage,
  treatment selection, final etiology adjudication, and patient-level prognosis.
- Intended use: test whether the disease research plan template can generate a
  source-grounded chapter that distinguishes chronic infarct/encephalomalacia
  from gliosis and common mimics.
- Explicit non-use: clinical diagnosis, stroke treatment, triage, or replacing
  expert interpretation.

## Chapter Goals

1. Known-diagnosis characterization goal: describe what chronic infarct and
   encephalomalacia look like on MRI and CT when prior infarct is known or
   suspected.
2. Differential or mimic-aware review goal: distinguish chronic infarct /
   encephalomalacia from gliosis without cavitation, low-grade glioma,
   demyelinating plaque, postoperative change, posttraumatic
   encephalomalacia, and nonspecific chronic small-vessel disease.
3. Clinical-statistical translation goal: map lesion type, vascular territory,
   chronicity, interval stability, hemorrhagic residua, and uncertainty to
   cohort labels, endpoints, covariates, confounders, adjudication, and claims.
4. Report-language extraction goal: capture Findings-style and
   Impression-style language for chronic infarct, encephalomalacia, gliosis,
   ex vacuo dilatation, and remote ischemic injury.
5. Figure or visual-teaching goal: identify examples that show chronic
   territorial infarct, cystic encephalomalacia, lacunar infarct, ex vacuo
   change, chronic hemorrhagic infarct, and gliosis-like mimics.

## Research And Writing Checkpoint

Date/time: 2026-05-07

Current phase: source search planning.

### What Has Been Done

- Selected chronic infarct / encephalomalacia as the first prospective
  differential-disease test.
- Created this research plan before creating the disease chapter.
- Identified the key reason for the test: chronic infarct and encephalomalacia
  are close to gliosis but should not be collapsed into generic gliotic change.

### What Worked

- The updated research-plan template gives clear prompts for scope, goals,
  differential diagnosis, report language, treatment/outcome context,
  confounders, and claim boundaries.
- Chronic infarct / encephalomalacia should have enough authoritative source
  material to test the workflow without making the first prospective disease
  too broad.

### What Did Not Work

- Source evidence has not been collected yet.
- Figure evidence has not been collected yet.
- No disease chapter should be drafted until source and figure evidence records
  are started.

### Problems Or Risks Before Continuing

- Chronic infarct, encephalomalacia, gliosis, lacunar infarct, chronic small
  vessel disease, and posttraumatic encephalomalacia can overlap in report
  language.
- Acute/subacute stroke material may dominate searches even though this chapter
  focuses on chronic residual findings.
- Broad stroke guidelines may not describe the chronic imaging appearance in
  enough detail; radiology teaching and textbook-style imaging sources will
  likely be needed.

### What Needs To Change

- Create the source evidence and figure evidence records before drafting.
- Search specifically for chronic, remote, old, encephalomalacia, ex vacuo,
  gliosis, and interval-stability language.
- Preserve distinctions between imaging appearance, vascular etiology, and
  research label confidence.

### Current Confidence

Draft.

### Next Action

Create `chronic-infarct-encephalomalacia.sources.json` and start source
research using broad authoritative imaging and stroke sources.

## Source Selection Principle

Use broad authoritative sources for broad imaging and clinical-course claims,
including textbook-style brain imaging references, professional society stroke
or imaging guidance, and clinician-facing radiology teaching resources.

Use narrow sources only for narrow claims such as inter-reader variability,
advanced imaging, automated segmentation, radiomics, or special infarct
subtypes.

## Search Strategy

Initial searches should include:

```text
chronic infarct brain MRI encephalomalacia radiology
remote infarct MRI encephalomalacia ex vacuo FLAIR
old cerebral infarct MRI chronic findings
chronic infarct differential diagnosis gliosis low grade glioma
encephalomalacia brain MRI radiology teaching
lacunar infarct chronic MRI gliosis
chronic hemorrhagic infarct SWI GRE MRI
ACR appropriateness criteria chronic stroke MRI
stroke imaging chronic infarct textbook MRI
```

## Terminology And Alias Extraction

| Term or phrase | Type | Source | Meaning or use | Ambiguity or mapping note |
| --- | --- | --- | --- | --- |
| chronic infarct | disease/finding phrase | pending | Remote ischemic injury visible as chronic residual change. | May be used without specifying tissue loss or vascular territory. |
| remote infarct | report phrase | pending | Prior infarct, usually chronic. | "Remote" implies timing but not necessarily mechanism certainty. |
| encephalomalacia | imaging/sequela term | pending | Tissue loss or softening/cavitation after injury. | Etiology may be vascular, traumatic, surgical, infectious, or other. |
| ex vacuo dilatation | imaging phrase | pending | Ventricular or sulcal enlargement from adjacent volume loss. | Supports chronicity but not specific etiology. |
| gliosis | tissue response/report phrase | pending | Reactive gliotic change adjacent to or within chronic injury. | Should not be used as the sole label for chronic infarct when infarct pattern is present. |

## Required Evidence Extraction Focus

| Topic | Source | Key points | Disease.md section | Confidence | Open questions |
| --- | --- | --- | --- | --- | --- |
| Chronic infarct appearance | pending |  | What To Look For | pending |  |
| Encephalomalacia and ex vacuo change | pending |  | Locations And Structural Appearance | pending |  |
| Vascular territory and lacunar patterns | pending |  | Differential Diagnosis And Mimics | pending |  |
| Chronic hemorrhagic residua | pending |  | Primary Imaging Modality | pending |  |
| Gliosis versus chronic infarct wording | pending |  | Report Language Patterns | pending |  |
| Interval stability | pending |  | Serial Imaging Assessment And Interval Change | pending |  |
| Cohort labels and confounders | pending |  | Statistical Implications | pending |  |

## Required Differential Diagnosis Matrix Targets

| Comparator | Why it can look similar | Planned discriminator focus |
| --- | --- | --- |
| Gliosis without clear encephalomalacia | Both may show chronic FLAIR signal abnormality. | Tissue loss, vascular-territory pattern, ex vacuo change, prior imaging, etiology language. |
| Chronic small vessel ischemic disease | Both may be chronic white matter abnormalities. | Lesion size, distribution, lacunar cavities, confluent white matter disease, vascular risk context. |
| Low-grade glioma | Both can be T2/FLAIR hyperintense and nonenhancing. | Expansion, mass effect, growth, cortical/subcortical pattern, perfusion/spectroscopy, interval change. |
| Demyelinating plaque | Both can be FLAIR hyperintense. | Ovoid/periventricular/callosal morphology, dissemination, enhancement, clinical context. |
| Posttraumatic encephalomalacia | Both can have tissue loss and gliosis. | Injury history, location pattern, hemorrhagic shear injury, cortical contusion distribution. |
| Postoperative cavity or treatment bed | Both can show tissue loss and gliosis. | Surgical history, treatment field, enhancement, recurrence/treatment-effect context. |

## Required Treatment, Response, And Outcome Extraction Focus

- Determine when secondary stroke-prevention guidance matters as context for
  outcomes but not as direct imaging interpretation.
- Capture how chronicity, prior treatment, reperfusion history, hemorrhagic
  transformation, and rehabilitation status may affect longitudinal endpoints.
- Identify when stable chronic infarct is an imaging baseline finding versus an
  active endpoint.

## Required Statistical Translation Focus

- Cohort labels: chronic infarct present/absent, infarct type, vascular
  territory, lacunar versus territorial, hemorrhagic residua, encephalomalacia,
  uncertainty, and adjudication status.
- Endpoints: new infarct, infarct progression, lesion burden, interval change,
  functional outcome linkage, and incidental chronic infarct burden.
- Covariates and confounders: age, vascular risk factors, prior stroke history,
  time since event, scanner/protocol, lesion size/location, treatment history,
  and reader/adjudication process.
- Sensitivity analyses: exclude uncertain chronic lesions, separate lacunar
  from territorial infarcts, stratify by vascular territory, and separate
  baseline chronic findings from incident events.

## Template Coverage Check

| Expected chapter section | Planned evidence source | Status | Gap or action |
| --- | --- | --- | --- |
| Goals | this research plan | planned |  |
| Source Review Status | source evidence record and source review notes | planned | create source evidence record |
| Figure Evidence | figure evidence record | planned | create figure evidence record |
| Common Names And Aliases | terminology extraction | planned | expand after source search |
| Scope | this research plan | planned |  |
| Clinical Context | broad clinical and imaging sources | planned |  |
| Known-Diagnosis Review Frame | imaging sources and report-language extraction | planned |  |
| What To Look For | textbook-style and radiology teaching sources | planned |  |
| Report Language Patterns | radiology teaching and report-like examples | planned |  |
| Primary Imaging Modality | imaging sources and professional criteria | planned |  |
| Other Modalities And When They Matter | imaging and stroke sources | planned |  |
| Locations And Structural Appearance | imaging sources and figure evidence | planned |  |
| Differential Diagnosis And Mimics | matrix targets above | planned |  |
| Treatment, Response, And Outcome Context | stroke guidance and longitudinal sources | planned |  |
| Common Covariates And Confounders | statistical translation focus | planned |  |
| Expert Use And Claim Boundaries | source review and content reviewer | planned |  |
| Related Disease Files | gliosis; future demyelination and low-grade glioma chapters | planned | cross-reference after chapters exist |
| Related Statistical Method Files | cohort definition, misclassification, longitudinal analysis | planned | decide whether method files are needed |

## Maturity Decision

This prospective test should not be marked mature until source evidence,
figure evidence, source review notes, disease chapter, content review, and HTML
preview all exist and the final chapter can be traced back to this plan.
