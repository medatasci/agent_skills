# Citation Practices

Use this reference before adding or revising scholarly manuscript prose.

## Default Style

For `project_publication.html`, default to inline numeric bracket citations:
`[1]`, `[2]`, `[3]`. Citations may be plain text or hyperlinks to reference
anchors, for example `<a href="#ref-jang-2023">[3]</a>`. Keep the visible
bracket number next to the claim it supports.

Author-year wording can appear in the sentence, but it does not replace the
inline bracket citation. Example:

```html
<p>Jang et al. reported two medical-image Turing tests with six readers and
mean authenticity-classification accuracies of 67.42% and 69.92% [3].</p>
```

## Claims That Need Inline Citations

Add inline citations for:

- prior-work summaries,
- published statistics or numeric findings,
- statements that a paper showed, found, reported, demonstrated, or concluded,
- comparisons between this project and external methods,
- dataset, model, benchmark, or software facts learned from external sources,
- literature-derived safety, privacy, ethics, or memorization claims.

Local project artifacts can cite local files, experiment ids, figure ids, table
ids, or update records instead of bibliographic references, but the evidence
must still be visible near the claim.

## Missing Sources

If the source is known but not yet in `publication_references.bib`, add the
BibTeX entry before finalizing the prose. If the source cannot be verified in the
current turn, mark the sentence with `[citation needed: short source label]` and
list the citation gap in the wrap-up. Do not leave literature claims uncited and
do not invent references.

## Audit Expectations

Before handing off manuscript edits that touch Background, Related Work,
Discussion, or literature-derived claims:

1. Check that every paragraph with prior-work claims has inline bracket
   citations.
2. Check that specific statistics have citations in the same sentence or next
   sentence.
3. Check that every bracket citation maps to an entry in the References section
   or `publication_references.bib`.
4. Check that references listed for the related-work section are cited in the
   prose or table.
5. Run `scripts/audit_inline_citations.py` when available and fix or report any
   warnings.
