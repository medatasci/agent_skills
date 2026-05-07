# Gliosis Disease Chapter Source Review

Research artifact for `docs/clinical-statistical-expert/diseases/gliosis.md`.

## Scope Definition

- Disease or finding: gliosis in the brain.
- Brain-specific scope: structural brain MRI appearance, anatomic distribution,
  mimic-aware interpretation, disease-course framing, and statistical
  implications.
- Primary imaging modality: MRI.
- Important secondary modalities: CT, EEG, PET/SPECT, MEG, pathology, vascular
  imaging, perfusion, spectroscopy, SWI/GRE, DWI/ADC.
- Included contexts: posttraumatic, postischemic, postsurgical, posttreatment,
  postinfectious, inflammatory/demyelinating, seizure-related, hippocampal
  sclerosis, Wallerian degeneration, and nonspecific chronic white matter
  change when the source supports the claim.
- Explicit non-use: this review does not establish final clinical
  adjudication, etiology, prognosis, or management.

## Research And Writing Checkpoint - Expanded Evidence Pass

Date/time: 2026-05-07

Current phase: source review, evidence extraction, image search, chapter
revision.

### What Has Been Done

- Created a prototype gliosis chapter before this pass.
- Added disease research, review, and figure-evidence templates for the
  clinical-statistical-expert workflow.
- Searched for authoritative gliosis, MRI, encephalomalacia, epilepsy,
  hippocampal sclerosis, and mimic-related sources.
- Reviewed high-yield sections from textbook-style NCBI Bookshelf/Springer
  chapters, ACR Appropriateness Criteria, Radiology Assistant, StatPearls/NCBI,
  and narrow technical studies.
- Captured one reusable NCBI figure locally through `python -m skillforge
  figure-evidence`.
- Downloaded source pages into the ignored local SkillForge source cache where
  access allowed it, and recorded cache status in `gliosis.sources.json`.
- Expanded the figure-evidence manifest to 54 image candidates across trauma,
  epilepsy, perinatal stroke, demyelination/MS, chronic infarct, tumor mimic,
  radiation/posttreatment effect, and other neurologic contexts.
- Added source records for additional authoritative or broad sources including
  NCBI Bookshelf, Radiology Assistant, MAGNIMS/CMSC/NAIMS MS MRI guidance, ACR
  demyelinating disease criteria, and broad PMC review articles.
- Added treatment-response and outcome-context sources for underlying-cause
  framing, including RANO 2.0 for glioma response/progression, EANO diffuse
  glioma guidance, AHA/ASA secondary stroke prevention guidance, and AAN
  disease-modifying therapy guidance for multiple sclerosis.

### What Worked

- NCBI Bookshelf/Springer provided the strongest open textbook-style material
  for posttraumatic encephalomalacia with gliosis and hippocampal sclerosis.
- The NCBI TBI figure is licensed under CC BY 4.0 and can be saved locally.
- ACR provides a useful modality-selection anchor for seizures and epilepsy.
- Radiology Assistant provides practical sequence-level teaching language for
  cortical/glial scars and hippocampal sclerosis.
- Narrow technical papers are useful for distinguishing "routine clinical
  appearance" from advanced MRI, radiomics, or low-grade-glioma mimic claims.

### What Did Not Work

- Gliosis is usually described as a tissue response or imaging finding rather
  than a single disease, so no single broad "gliosis textbook chapter" was
  found.
- Some good visual sources are educational but require reuse review before
  local image storage.
- Search results returned many narrow case reports and specialty papers that
  should not be used as the basis for broad claims.
- The current review does not yet document a full line-by-line 100-page source
  extraction.
- Radiopaedia returned HTTP 406 for automated source-page download.
- Springer/Nature pages downloaded as client-challenge pages rather than full
  article pages, so they remain URL-first sources until accessed another way.

### Problems Or Risks Before Continuing

- Broad claims can be overextended if they are based on narrow studies.
- Etiologic heterogeneity is a major risk: posttraumatic, vascular,
  demyelinating, postsurgical, radiation-related, and hippocampal-sclerosis
  gliosis should not be collapsed without a reason.
- Routine MRI can infer gliosis but does not directly prove cellular
  astrogliosis.
- Image reuse must be recorded per image, not assumed from search thumbnails.
- Some quoted teaching resources use operational clinical language; the disease
  chapter should preserve expert-facing nuance.

### What Needs To Change

- Mark the chapter as an evidence-backed draft, not a mature chapter.
- Replace the placeholder figure section with recorded local figure evidence.
- Add a source-review link and open gaps to the chapter.
- Keep narrow studies in a separate source category and label their claims as
  narrow.
- Add ACR narrative URL rather than relying on a secondary journal landing page
  or patient-facing summary.
- Treat source downloads as local reproducibility cache unless redistribution
  rights are explicit. Do not commit full source pages by default.

### Current Confidence

Developing. The chapter is more grounded after this pass, but it still needs a
deeper source-to-report-language extraction pass and expert review before being
treated as mature.

### Next Action

Review the 51 link-only figure candidates for exact figure relevance and reuse
status, then extract more disease-course and report-style language from the
expanded source set.

## Source Selection Principle Applied

This pass used authoritative, relevant sources matched to claim breadth:

- Broad claims were preferentially grounded in textbook-style chapters,
  professional criteria, and clinician-facing radiology teaching material.
- Narrow technical claims were limited to their specific technical domain, such
  as radiomics differentiation or advanced MRI correlation with astrogliosis.
- Consumer-facing summaries were not used as primary support for technical
  claims.

## Source Archive And Local Cache

Tracked source manifest:
`docs/clinical-statistical-expert/diseases/gliosis.sources.json`.

Local source cache root:
`.skillforge/source-cache/clinical-statistical-expert/gliosis/2026-05-07`.

The local cache is ignored by git. It is meant to help future updates on this
machine, not to redistribute source pages publicly. Full source pages should not
be committed unless redistribution is explicitly permitted and recorded. Public
repo artifacts should preserve source URLs, citation metadata, reuse status,
claims supported, and local cache status.

Current archive status after the expanded source-archive and image-evidence pass:

- Source manifest schema: `1.0`.
- Source entries recorded: 38.
- Source pages cached locally: 28, including one source whose figure is also
  saved in the repo.
- Download-failed or URL-first source records: 9.
- Source page needing download review: Nature Reviews multidimensional MRI
  astrogliosis still appears to be a client-challenge download and should be
  treated as URL-first until manually reviewed.
- Local embeddable figures: 3.
- Link-only figure candidates: 51.
- Total figure candidates recorded: 54.

Refinement checkpoint:

- What is working: context-specific searches by etiology or mimic are producing
  strong sources. Productive contexts include posttraumatic encephalomalacia,
  chronic infarct, hippocampal sclerosis, demyelination/MS differential,
  treatment effect/radiation necrosis, low-grade glioma mimic, and
  postoperative longitudinal change.
- What is not working: broad "gliosis MRI" searches quickly return duplicate
  or thin material; generic image search thumbnails rarely provide enough
  source context; some publisher pages block automated downloads or return
  client-challenge pages.
- Refined approach: continue source extraction by clinical context, record all
  promising figures as link-only first, save images locally only when reuse
  terms are explicit, and separate broad clinical sources from narrow case
  reports or technical studies.

Initial download status before schema normalization:

- Cached locally: NCBI TBI chapter, NCBI TBI figure page, NCBI epilepsy imaging
  chapter, NCBI hippocampal sclerosis figure page, NCBI/StatPearls MTLE page,
  ACR Seizures and Epilepsy narrative, Radiology Assistant epilepsy MRI page,
  Frontiers PET/MR review, MRI Online encephalomalacia page.
- Downloaded but needs review: Springer/BMC radiomics article and Nature
  Reviews astrogliosis page downloaded as client-challenge pages rather than
  full source pages.
- URL-only after failed automated download: Radiopaedia gliosis and
  encephalomalacia pages.

## Searches Run

```text
gliosis brain MRI neuroradiology textbook FLAIR encephalomalacia
gliosis MRI encephalomalacia radiology teaching FLAIR
site:ncbi.nlm.nih.gov/books gliosis MRI brain
site:radiologyassistant.nl gliosis MRI brain
ACR Appropriateness Criteria seizures epilepsy MRI CT
ACR Appropriateness Criteria Seizures and Epilepsy MRI usually appropriate
site:acsearch.acr.org seizures epilepsy MRI appropriateness criteria
gliosis MRI Radiopaedia article
gliosis radiology MRI Radiopaedia encephalomalacia
reactive gliosis mimicking tumor recurrence MRI PMC
gliosis low grade glioma MRI differential radiology
gliosis MRI FLAIR brain encephalomalacia
gliosis brain MRI Radiology Assistant ulegyria
hippocampal sclerosis gliosis MRI FLAIR
gliosis MRI FLAIR brain encephalomalacia image case
site:radiopaedia.org gliosis MRI FLAIR encephalomalacia
site:radiologyassistant.nl gliosis FLAIR MRI image ulegyria
NCBI Bookshelf brain imaging epilepsy hippocampal sclerosis gliosis FLAIR
posttraumatic gliosis encephalomalacia FLAIR MRI textbook
gliosis neuroimaging review MRI astrogliosis PET MR
```

## Source Review Log

| Source | Source type | Claim breadth supported | Approx. depth | Sections read | Key claims supported | Disease.md sections informed | Limitations |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| NCBI Bookshelf/Springer, `Traumatic Neuroemergency: Imaging Patients with Traumatic Brain Injury` | Textbook-style chapter | Broad for TBI sequelae; narrow for posttraumatic gliosis | 40 page-equivalent chapter triaged; posttraumatic sequelae read closely | Imaging techniques, intra-axial lesions, posttraumatic sequelae, Fig. 7.11 | Encephalomalacia is tissue loss after trauma; gliotic scar/rim is best seen as FLAIR hyperintensity; MRI adds sensitivity after CT in selected trauma contexts | Primary Imaging Modality; Locations And Structural Appearance; Stable Or Chronic Residual Findings; Figure Evidence | TBI-specific; should not generalize all gliosis from trauma |
| NCBI Bookshelf/Springer, `Imaging the Patient with Epilepsy or Seizures` 2024-2027 | Textbook-style chapter | Broad for epilepsy imaging and hippocampal sclerosis | 35 page-equivalent chapter triaged; protocol and hippocampal sclerosis sections read closely | Epilepsy protocol, lesion location, hippocampal sclerosis, Fig. 10.5 | Dedicated MRI protocols improve lesion detection; hippocampal sclerosis shows T2/FLAIR hyperintensity and atrophy; encephalomalacia and gliosis are structural etiologies in epilepsy cohorts | Primary Imaging Modality; Hippocampus; Mimics; Statistical Implications | Epilepsy-specific; not a general gliosis chapter |
| ACR Appropriateness Criteria, `Seizures and Epilepsy` narrative | Professional society criteria | Broad for modality selection in seizure/epilepsy scenarios | Criteria narrative and rating tables reviewed | Variant tables and supporting definitions | MRI and CT appropriateness depends on clinical scenario; MRI is usually appropriate for several seizure contexts, while CT is usually appropriate in trauma/emergent initial settings | Other Modalities; Clinical Context; Missing Information | Seizure/epilepsy focus; does not directly define gliosis |
| Radiology Assistant, `Epilepsy - Role of MRI` | Radiology teaching resource | Broad practical teaching for epilepsy imaging; narrow for ulegyria/glial scars | Long teaching page triaged; MTS and cortical/glial scars read closely | MRI epilepsy protocol, mesial temporal sclerosis, cortical/glial scars | FLAIR is useful for gliotic hyperintensity; 3D T1 helps structural cortex review; MTS combines hippocampal signal change and volume loss | Primary Imaging Modality; Locations And Structural Appearance; Hippocampus | Educational resource, not formal guideline; image reuse requires review |
| NCBI Bookshelf/StatPearls, `Mesial Temporal Lobe Epilepsy` | Clinical training chapter | Broad for MTLE and hippocampal sclerosis context | Chapter sections triaged; histopathology and imaging context reviewed | Etiology, histopathology, diagnostic evaluation, care-team context | Hippocampal sclerosis includes neuronal loss and reactive astrogliosis; MTLE requires integrated EEG, imaging, and clinical interpretation | Hippocampus; Other Modalities; Known-Diagnosis Review Frame | Disease-specific; use for hippocampal sclerosis, not generic gliosis |
| BMC Medical Imaging/Springer, `Multiparametric MRI radiomics for the differentiation of brain glial cell hyperplasia from low-grade glioma` | Narrow technical primary study | Narrow | Article abstract, introduction, methods/results summary reviewed | Glial hyperplasia can be hard to distinguish from low-grade glioma; radiomics model performance is study-specific | Similar-Presentation Diseases; Statistical Implications | Single retrospective study; not a broad clinical source |
| Nature Reviews Neurology, `Multidimensional MRI detects astrogliosis` | Research highlight | Narrow technical/supporting | Research highlight reviewed | Advanced multidimensional MRI may correlate with astrogliosis markers in research context | Other Modalities; Statistical Implications | Not routine clinical imaging guidance |
| Frontiers in Cellular Neuroscience, `Gliosis and Neurodegenerative Diseases: The Role of PET and MR Imaging` | Review article | Narrow to glial activation and neurodegeneration | Article identified for future extraction | PET/MR can study glial activation in neurodegenerative contexts | Other Modalities; advanced biomarkers | Not routine structural MRI appearance; deeper extraction still needed |
| Radiopaedia, `gliosis` and `encephalomalacia` | Radiology reference article | Candidate support, not primary in this pass | Search result/source page identified | Useful terminology and examples likely available | Candidate future support for aliases and examples | Access/reuse and citation details need review before use |

Additional source candidates added after the initial table:

| Source | Source type | Claim breadth supported | Why added | Disease.md sections informed | Next extraction need |
| --- | --- | --- | --- | --- | --- |
| NCBI Bookshelf/Springer, `Neuroimaging Update on Traumatic Brain Injury` 2024-2027 | Textbook-style chapter | Broad for chronic traumatic encephalomalacia, gliosis, and SWI context | Updates the prior TBI chapter with chronic hemorrhagic encephalomalacia and a reusable CC BY 4.0 figure | Stable Or Chronic Residual Findings; Serial Imaging Assessment And Interval Change; Report Language Patterns | Extract updated report-style phrases and contrast with the 2020 chapter |
| NCBI Bookshelf, `Neuroimaging in Perinatal Stroke and Cerebrovascular Disease` | Textbook-style chapter | Broad for chronic infarct, encephalomalacia, gliosis, and FLAIR context in perinatal stroke | Adds a nontraumatic vascular/developmental source with chronic-stage language | Natural History And Clinical Course; Stable Or Chronic Residual Findings | Extract chronic-stage imaging language and figure rights |
| NCBI Bookshelf, `Neurovascular Reactivity in Tissue Scarring Following Cerebral Ischemia` | Textbook-style chapter | Broad for post-ischemic astrogliosis and glial scarring mechanisms | Supports biological mechanism and why imaging labels infer rather than prove cellular gliosis | Natural History And Clinical Course; Statistical Implications | Keep mechanism claims separate from routine MRI appearance claims |
| PMC, `Imaging markers of cerebrovascular pathologies` | Review article | Broad for chronic macroinfarct imaging markers and gliotic FLAIR rim | Adds chronic infarct language that maps well to radiology-report phrasing | Primary Imaging Modality; Stable Or Chronic Residual Findings; Report Language Patterns | Extract FLAIR rim and chronic macroinfarct wording |
| PMC, `A systematic approach to detection of epileptogenic foci on imaging` | Radiology review article | Broad practical imaging description for gliosis in epilepsy imaging | Directly describes gliosis on T1, T2, FLAIR, ADC, and CT and includes a candidate Figure 20 | What To Look For; Report Language Patterns; Similar-Presentation Diseases | Full review needed because it is highly relevant to report-language extraction |
| PMC, `Neuroimaging Findings of the Post-Treatment Effects of Radiation and Chemotherapy of Malignant Primary Glial Neoplasms` | Radiology review article | Broad for posttreatment effect, radiation necrosis, pseudoprogression, and recurrence mimic framing | Adds treatment-bed and recurrence-mimic context | Similar-Presentation Diseases; Evidence Of Active Disease, Progression, Or Recurrence | Extract posttreatment FLAIR/enhancement language and active-process red flags |
| PMC, `Neuroradiological evaluation of demyelinating disease` | Review article | Broad for demyelinating lesion imaging and mimic context | Adds chronic plaque and demyelinating-mimic context | Similar-Presentation Diseases; Report Language Patterns | Extract chronic versus active plaque descriptors |
| Radiology Assistant, `Multiple Sclerosis 2.0` | Radiology teaching resource | Broad practical teaching for MS lesion pattern and differential diagnosis | Adds clinician-facing differential language for white matter lesion pattern recognition | Locations And Structural Appearance; Similar-Presentation Diseases | Review images as link-only candidates and extract practical decision rules |
| ACR Appropriateness Criteria, `Demyelinating Diseases` | Professional society criteria | Broad for modality selection in suspected demyelinating disease | Adds society-level modality-selection support for MS/demyelination contexts | Other Modalities; Missing Information To Ask For | Extract modality and contrast-use guidance |
| PMC, `Angiocentric glioma mimicking encephalomalacia` | Narrow case report | Narrow for tumor mimic of encephalomalacia and gliosis | Adds a cautionary mimic where a lesion was interpreted as encephalomalacia/gliosis | Similar-Presentation Diseases; Report Language Patterns | Keep as cautionary example only, not broad guidance |
| PMC, `Quantitative MRI comparison of early and late parenchymal injury after transcallosal vs. endoscopic approaches for third ventricle colloid cysts` | Narrow clinical research article | Narrow for postoperative FLAIR abnormality and late gliosis/encephalomalacia associations | Adds longitudinal postoperative context and endpoint design material | Serial Imaging Assessment And Interval Change; Statistical Implications | Extract study-design implications, not broad disease appearance |
| RANO 2.0 glioma response criteria | Response criteria consensus update | Narrow for adult glioma response and progression assessment | Adds response/progression endpoint context for treatment-bed gliosis, pseudoprogression, and radiation-related mimic review | Treatment, Response, And Outcome Context; Statistical Implications Of Treatment And Progression | Extract only when tumor-treatment context is relevant |
| EANO diffuse glioma guidelines | Professional society guideline | Broad for adult diffuse glioma diagnosis, treatment, and follow-up | Adds guideline-based management context for treated glioma regions where gliosis, recurrence, and treatment effect overlap | Treatment, Response, And Outcome Context; Guideline-Based Management Context | Keep limited to glioma/tumor-treatment context |
| AHA/ASA secondary stroke prevention guideline | Professional society guideline | Broad for stroke/TIA prevention and outcome context | Adds vascular treatment and outcome context when gliosis is a postischemic sequela | Treatment, Response, And Outcome Context; Expected Outcomes And Prognostic Factors | Extract functional/outcome and recurrent-event framing when vascular context is central |
| AAN MS disease-modifying therapy guideline | Professional society guideline | Broad for MS treatment context | Adds demyelinating-disease treatment-status context when chronic plaques are compared with nonspecific gliosis | Treatment, Response, And Outcome Context; Common Treatment Pathways | Extract treatment-status implications only for demyelinating contexts |
| NCBI Bookshelf/Springer, `Intracranial Infection and Inflammation` | Textbook-style chapter | Broad for brain abscess MRI differential context | Adds infection/abscess mimic support, especially ring enhancement, edema, and DWI restriction as active-process clues | Differential Diagnosis And Mimics; Key Imaging Discriminators | Use for abscess mimic rows, not generic gliosis behavior |
| NCBI Bookshelf/StatPearls, `Cerebral Cavernous Malformations` | Clinical training chapter | Broad for cavernous malformation differential context | Adds cavernous malformation support, including hemosiderin/gliosis context and GRE/SWI blooming | Differential Diagnosis And Mimics; Key Imaging Discriminators | Use for hemorrhagic vascular-lesion mimic rows |

## Evidence Extraction Matrix

| Topic | Sources | Key points | Disease.md section | Confidence | Open questions |
| --- | --- | --- | --- | --- | --- |
| MRI appearance | NCBI TBI; Radiology Assistant; MRI Online candidate | Chronic gliosis is commonly inferred as T2/FLAIR hyperintensity, often adjacent to tissue loss or scarring; FLAIR helps separate CSF-like encephalomalacia from surrounding gliotic signal | Primary Imaging Modality | Developing to strong for TBI and epilepsy contexts | Need more broad neuroradiology textbook support outside trauma/epilepsy |
| Locations and structure | NCBI TBI; NCBI epilepsy 2024; Radiology Assistant | Location and morphology are central: posttraumatic basal frontal/temporal regions, hippocampus in MTS, cortical/glial scars in ulegyria, treatment beds, white matter tracts | Locations And Structural Appearance | Developing | Need more source-backed coverage of vascular, demyelinating, radiation, and postoperative contexts |
| Natural history | NCBI TBI; StatPearls MTLE; NCBI epilepsy 2024 | Gliosis usually represents chronic residual tissue response, but clinical course depends on etiology; hippocampal sclerosis is a chronic epilepsy-associated substrate | Natural History And Clinical Course | Developing | Need deeper disease-course extraction for each etiology |
| Active progression | BMC radiomics; narrow mimic sources; chapter reasoning | Growth, mass effect, nodular enhancement, restricted diffusion, and high perfusion argue against uncomplicated stable gliosis and raise mimic/active-process concern | Evidence Of Active Disease, Progression, Or Recurrence | Developing | Need broad radiology-source support for each red flag |
| Stable or chronic findings | NCBI TBI Fig. 7.11; NCBI TBI posttraumatic sequelae | Chronic posttraumatic encephalomalacia can show tissue loss with surrounding FLAIR-bright gliosis; local volume loss and stability support chronicity | Stable Or Chronic Residual Findings | Strong for posttraumatic examples; developing broadly | Need examples for nontraumatic chronic gliosis |
| Response or resolution | General clinical reasoning from etiology | Gliosis may persist after edema, enhancement, or active inflammation improves; response endpoints must separate active process from scar | Improvement, Treatment Response, Or Resolution | Draft | Need direct sources for treatment-response language |
| Treatment, response, and outcomes | RANO 2.0; EANO diffuse glioma; AHA/ASA stroke prevention; AAN MS DMT; posttreatment imaging review | Gliosis is not usually a standalone treatment target; treatment response and outcome context should be organized by underlying cause and disease-specific criteria | Treatment, Response, And Outcome Context | Developing | Need deeper source extraction for each etiology and guideline population |
| Serial imaging | NCBI TBI; NCBI epilepsy 2024; ACR | Prior imaging and clinical scenario shape interpretation; protocol/read expertise affects lesion detection | Serial Imaging Assessment And Interval Change | Developing | Need formal inter-reader/protocol-variation sources |
| Differential diagnosis and mimics | BMC radiomics; Radiology Assistant; NCBI epilepsy 2024; posttreatment imaging review; NCBI infection/inflammation; NCBI cavernous malformations | Low-grade glioma, encephalomalacia, acute/subacute infarct, demyelination, treatment effect, infection, hemorrhagic lesions, small vessel disease, and seizure-related signal can overlap depending on location, timing, course, and treatment history | Differential Diagnosis And Mimics | Developing to strong | Row-level source anchors have been added; still need deeper line-by-line extraction for tumor, demyelination, and treatment-bed categories |
| Covariates and confounders | AHA/ASA stroke prevention; AAN MS DMT; RANO 2.0; EANO diffuse glioma; ACR seizure/epilepsy; chapter reasoning | Etiology, age, vascular risk, treatment history, time from event/treatment, prior imaging, clinical indication, scanner/protocol, and reader expertise can bias interpretation and cohort labels | Common Covariates And Confounders | Developing | Need disease-context mini-tables and formal reliability references |
| Statistical implications | NCBI epilepsy 2024; BMC radiomics; chapter reasoning | Cohort labels need etiology, anatomic location, endpoint definition, adjudication, and sensitivity analysis because gliosis is heterogeneous and nonspecific | Statistical Implications | Developing | Need measurement/reliability sources |
| Findings-style report language | NCBI TBI 2020; NCBI TBI 2024; NCBI epilepsy 2024; PMC epileptogenic foci review; Cambridge chronic infarct | Useful findings-style descriptors include nonexpansile T2/FLAIR hyperintensity, CSF-like tissue loss, FLAIR-bright rim, volume loss, ex vacuo dilatation, lack of enhancement, lack of restricted diffusion, hippocampal atrophy, and SWI/GRE hemosiderin context | What To Look For; Report Language Patterns | Developing to strong for trauma and epilepsy; developing broadly | Need more real report examples from vascular, demyelinating, postoperative, and radiation/treatment-bed contexts |
| Impression-style report language | NCBI TBI 2020; NCBI TBI 2024; NCBI epilepsy 2024; PMC seizure pictorial review | Impression language should synthesize chronicity, likely etiology, stability, and important exclusions such as no acute infarct, mass effect, nodular enhancement, or progressive mass-like FLAIR abnormality | Report Language Patterns; Serial Imaging Assessment And Interval Change | Developing | Need source-derived impression phrases and expert review of how much uncertainty language to preserve |
| Report uncertainty and cohort-label language | PMC mTBI operational definitions; PMC posttreatment review; Radiology Assistant MS differential; chapter reasoning | Lower-confidence labels such as nonspecific T2/FLAIR hyperintensity should not be collapsed into strong gliosis labels without context, stability, or adjudication | Report Language Patterns; Statistical Implications | Developing | Need a formal label hierarchy and examples from real trial/cohort definitions |

## Image Candidate Review Log

| Image candidate | Source page | Source quality | What image appears to show | What source says it shows | Use decision | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| NCBI/Springer Fig. 7.11, posttraumatic encephalomalacia and gliosis | https://www.ncbi.nlm.nih.gov/books/NBK554351/figure/ch7.Fig11/ | Strong | Axial and coronal FLAIR MRI with tissue loss and surrounding bright signal | Posttraumatic tissue loss surrounded by gliosis, plus old diffuse axonal injury gliotic foci | save | Open Access, CC BY 4.0; directly supports chronic FLAIR gliosis adjacent to encephalomalacia |
| NCBI/Springer Fig. 10.5, hippocampal sclerosis | https://www.ncbi.nlm.nih.gov/books/NBK608615/figure/ch10.Fig5/ | Strong | Coronal FLAIR/T2/3D MPRAGE hippocampal abnormality | Typical hippocampal sclerosis with hyperintensity, atrophy, and loss of interdigitation | save | Open Access, CC BY 4.0; directly supports hippocampal sclerosis report language |
| NCBI/Springer Fig. 7.12, chronic hemorrhagic encephalomalacia | https://www.ncbi.nlm.nih.gov/books/NBK608606/figure/ch7.Fig12/ | Strong | FLAIR and SWI example of chronic hemorrhagic encephalomalacia and traumatic sequelae | Chronic hemorrhagic encephalomalacia with ex vacuo temporal horn dilatation and chronic hemorrhagic axonal injury | save | Open Access, CC BY 4.0; supports chronic traumatic sequelae and SWI correlation |
| PMC seizure pictorial review Fig. 22 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8813621/ | Strong candidate | T2/FLAIR example of encephalomalacia with adjacent hyperintensity suggesting gliosis | Encephalomalacia and gliosis in a patient with seizures | link-only | Useful direct gliosis figure; reuse status needs review before local storage |
| PMC epileptogenic foci review Fig. 20 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12811103/ | Strong candidate | T1/T2/FLAIR example described as bifrontal gliosis | Gliosis with decreased T1 signal and increased T2/FLAIR signal | link-only | Highly relevant to report-language extraction; reuse status needs review |
| PMC angiocentric glioma mimic Fig. 1 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6441711/ | Narrow but useful | Tumor mimicking encephalomalacia/gliosis with FLAIR rim | Angiocentric glioma initially interpreted as encephalomalacia/gliosis | link-only | Mimic/cautionary example only |
| PMC low-grade glioma Fig. 1 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3983820/ | Strong comparator | Low-grade glioma with T2/FLAIR hyperintensity | Low-grade glioma imaging features | link-only | Comparator, not gliosis; useful for mimic-aware section |
| NCBI perinatal stroke Fig. 6 | https://www.ncbi.nlm.nih.gov/books/NBK572005/ | Strong candidate | Chronic infarction with liquefactive change and FLAIR-visible abnormality | Chronic stage with encephalomalacia/gliosis depending on insult timing | link-only | Needs exact figure-page and reuse review before local storage |
| StatPearls ischemic stroke encephalomalacia figure | https://www.ncbi.nlm.nih.gov/books/NBK499997/figure/article-23776.image.f3/ | Useful candidate | Encephalomalacia after ischemic stroke | Encephalomalacia following ischemic stroke | link-only | CC BY-NC-ND restrictions; keep link-only for now |
| StatPearls MS FLAIR lesion burden figure | https://www.ncbi.nlm.nih.gov/books/NBK499849/figure/article-25363.image.f4/ | Useful comparator | FLAIR lesion burden in MS | Advanced lesion burden along the callososeptal interface | link-only | Comparator for demyelinating mimic; not gliosis itself |
| Radiology Assistant ulegyria/glial scars image | https://radiologyassistant.nl/neuroradiology/epilepsy/role-of-mri | Strong teaching source | Tissue loss and cortical scarring with FLAIR signal | Tissue loss and gliosis under shrunken cortex; FLAIR shows gliotic hyperintensity | link-only | Clinically useful, but local reuse needs rights review |
| Radiology Assistant MS differential image set | https://radiologyassistant.nl/neuroradiology/multiple-sclerosis/diagnosis-and-differential-diagnosis-3 | Strong teaching source | MS lesion distribution and white matter lesion differential examples | Practical MS diagnosis and differential diagnosis examples | link-only | Comparator image set; local reuse needs rights review |
| PMC posttreatment effects review image set | https://pmc.ncbi.nlm.nih.gov/articles/PMC4202820/ | Strong candidate | Radiation necrosis, treatment effect, recurrence, and posttreatment imaging patterns | Posttreatment effects of radiation and chemotherapy | link-only | Exact figure choices need review |
| PMC postoperative colloid cyst longitudinal source | https://pmc.ncbi.nlm.nih.gov/articles/PMC12696183/ | Narrow candidate | Early/late postoperative imaging or tables linking early FLAIR change to late gliosis/encephalomalacia | Postoperative parenchymal change and late structural findings | link-only | Narrow endpoint-design source, not broad appearance |
| Radiopaedia gliosis case | https://radiopaedia.org/cases/gliosis-7 | Mixed/candidate | Gliosis case example | Case-level gliosis example | link-only/needs-review | Useful as a candidate image source; case authority and reuse terms need review |
| MRI Online/Medality encephalomalacia images | https://mrionline.com/diagnosis/encephalomalacia/ | Strong teaching source | Encephalomalacia/gliosis teaching images | Distinguishes encephalomalacia and gliosis | link-only/needs-review | Useful teaching source; local reuse not established |

## Image Search Checkpoint

- Target: review at least 50 image candidates before calling the chapter image
  evidence mature.
- Current recorded image evidence: 54 candidates.
- Current local embeddable figures: 3.
- Current link-only figure candidates: 51.
- Searches run: broad gliosis MRI, gliosis FLAIR, encephalomalacia MRI,
  hippocampal sclerosis FLAIR, Radiology Assistant gliosis, Radiopaedia gliosis,
  NCBI Bookshelf figure searches, chronic infarct gliosis, demyelinating plaque
  mimic, radiation necrosis/treatment effect, postoperative gliosis, and
  low-grade-glioma mimic searches.
- Promising image patterns found: posttraumatic encephalomalacia with FLAIR rim,
  hippocampal sclerosis with T2/FLAIR hyperintensity and atrophy, ulegyria with
  cortical scarring and gliosis, chronic hemorrhagic traumatic encephalomalacia,
  chronic infarct/encephalomalacia, demyelinating mimics, low-grade-glioma
  mimics, posttreatment/radiation-necrosis mimics, and postoperative
  longitudinal changes.
- Images saved locally: NCBI/Springer Fig. 7.11 posttraumatic
  encephalomalacia/gliosis, NCBI/Springer Fig. 10.5 hippocampal sclerosis, and
  NCBI/Springer Fig. 7.12 chronic hemorrhagic encephalomalacia.
- Images recorded as link-only: 51 candidates from PMC seizure and
  epileptogenic-focus reviews, Radiology Assistant epilepsy/MS/white-matter
  teaching pages, NCBI perinatal stroke figures, Radiopaedia and MRI Online
  candidate examples, StatPearls comparators, chronic infarct and tumor-mimic
  sources, posttreatment/radiation-necrosis reviews, and postoperative
  longitudinal sources.
- Images rejected and why: generic thumbnails and narrow case images without
  sufficient source context were not retained.
- Source terms discovered from image pages: posttraumatic encephalomalacia,
  gliotic scar tissue, FLAIR hyperintense rim, hippocampal sclerosis, ulegyria,
  cortical and glial scars, chronic hemorrhagic encephalomalacia, ex vacuo
  dilatation, chronic macroinfarct, callososeptal MS lesions, radiation
  necrosis, and treatment effect.
- Search refinements to run next: inspect and rank the strongest link-only
  candidates, especially "routine clinical radiology report gliosis",
  "postoperative cavity gliosis FLAIR MRI", "radiation necrosis gliosis MRI
  treatment bed", "chronic infarct gliotic rim FLAIR", "gliosis versus low
  grade glioma FLAIR no enhancement", and "demyelinating plaque chronic
  gliosis FLAIR".
- Image gaps remaining: stronger locally embeddable postoperative/treatment-bed
  examples; more vascular/chronic-infarct examples with clear reuse terms; more
  demyelinating plaque comparators; and paired serial prior-versus-follow-up
  examples.

## Review Gaps

- Complete deeper extraction from at least 100 page-equivalent material before
  marking the disease chapter mature. The current archive has enough cached and
  URL-recorded material to reach that target, but the extraction is not yet
  complete line by line.
- Review at least 50 image candidates before calling figure evidence mature.
  The current manifest records 54 candidates, so the numeric target is met. The
  remaining work is qualitative: inspect the best link-only figures, confirm
  exact clinical points, record reuse limits, and decide whether any additional
  images can be embedded locally.
- Add additional broad neuroradiology textbook or textbook-style sources for
  vascular, demyelinating, postsurgical, and radiation-related gliosis.
- Review image rights for Radiology Assistant, Radiopaedia, and MRI Online
  examples before local storage. Keep link-only evidence when rights are not
  clear.
- Add source-backed claims for response/resolution and interval-change
  endpoints.
- Add more source-derived findings-style and impression-style report language,
  especially for vascular, postoperative, demyelinating, and posttreatment
  contexts.
- Add expert review after the next full-source pass.
