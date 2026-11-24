# DialectAlign ? Source Eligibility Assessment

## 1. Purpose

This document evaluates external dataset sources for potential use in
DialectAlign, a research project investigating dialect-aware and
cross-lingual civic grievance understanding.

A dataset's presence in the local corpus does not imply permission
to train, redistribute, publish, or deploy models using its contents.

## 2. Current Inventory

The locally acquired Bhojpuri aggregate contains 386,032 records
across 13 source partitions.

The licences below are declarations in aggregate metadata, not
independently verified permissions.

| Source | Records | Aggregate licence declaration | Status |
|---|---:|---|---|
| fish_food | 215813 | CC-BY-4.0 | QUARANTINED |
| jnu_bhltr | 79884 | CC BY-NC-SA 4.0 | QUARANTINED |
| eng_bho | 26909 | CC-BY-4.0 | QUARANTINED |
| bhojpuri_lr_v3 | 21811 | CC-BY-4.0 | QUARANTINED |
| hplt | 17778 | CC0 | QUARANTINED |
| wikipedia | 7603 | CC BY-SA 4.0 | QUARANTINED |
| kumar_bhojpuri | 6567 | CC-BY-4.0 | QUARANTINED |
| iit_bhu | 5254 | CC BY-NC-SA 4.0 | QUARANTINED |
| fleurs_bhojpuri | 2708 | CC-BY-4.0 | QUARANTINED |
| google_smol | 844 | CC-BY-4.0 | QUARANTINED |
| glotcc | 567 | CC-BY-4.0 | QUARANTINED |
| rural_women | 211 | CC-BY-4.0 | QUARANTINED |
| ud_bhtb | 83 | CC BY-SA 4.0 | QUARANTINED |

## 3. URL Traceability

All 386,032 records contain syntactically valid HTTP(S) URL metadata.

However, each source partition has exactly one unique URL
shared by all records in that partition.

Therefore, the URL metadata establishes collection-level attribution
rather than individual record-level URL traceability.

URL validity does not prove document authenticity, accessibility,
licensing, consent, or research-use eligibility.

## 4. Known Licensing Concerns

### fish_food

Previous upstream comparison identified substantial exact-text
overlap with Goldfish Bhojpuri material.

The investigated upstream material declared CC BY-NC-SA terms,
whereas the aggregate declares CC-BY-4.0.

The discrepancy requires original-source rights verification.

### rural_women

The aggregate declares CC-BY-4.0.

The investigated upstream Rural Women Bhojpuri dataset declares
CC BY-SA 4.0.

Privacy processing has been completed for the 211 local records
under a single-reviewer workflow, but independent privacy
verification and secondary-use eligibility remain unresolved.

### Other partitions

Original-source licences, applicable attribution obligations,
permitted downstream uses, and provenance granularity have not
yet been fully established.

An open or permissive aggregate declaration must not be assumed
to override rights associated with underlying material.

## 5. Research Suitability

Licensing and scientific suitability are separate decisions.

Each source requires assessment of:

1. Original publisher and source version.
2. Original-source licensing and any applicable restrictions.
3. Consent and privacy obligations, where applicable.
4. Language and dialect authenticity.
5. Text quality and possible contamination.
6. Duplicate and translation overlap.
7. Suitability for linguistic analysis.
8. Suitability for authentic civic grievance classification.
9. Permitted model-training and redistribution uses.
10. Evidence supporting the final eligibility decision.

General language resources must not automatically be classified
as authentic civic grievance datasets.

## 6. Eligibility Decision Rules

QUARANTINED:
Research-use eligibility has not been established.

ELIGIBLE:
Documented evidence supports a specified research use,
with applicable conditions recorded.

EXCLUDED:
The source is unsuitable or prohibited for the specified use.

Eligibility must be assessed per intended use, rather than
assuming a single approval applies to every downstream activity.

## 7. Immediate Research Priorities

- Verify source-specific licences and original publishers.
- Investigate upstream record-level provenance where possible.
- Resolve the fish_food and rural_women licence discrepancies.
- Assess linguistic quality and grievance-domain suitability.
- Document permitted uses and unresolved restrictions.
- Seek authentic, appropriately licensed civic grievance records.

## 8. Current Decision

No source partition is approved for model training.

All 13 partitions remain QUARANTINED.

This assessment is an evolving evidence record, not a legal
compliance certificate or guarantee of anonymization.
