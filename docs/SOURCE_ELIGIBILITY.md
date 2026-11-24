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

#### Reproduced local overlap audit

Audit date: 2026-11-24.

Local inputs:

- Aggregate: `data/external/bhojpuri_corpus/BhojpuriCorpus.parquet`
- Upstream: `data/external/goldfish_bhojpuri/bho_deva.txt`

Verified results:

| Measure | Result |
|---|---:|
| Local fish_food records | 215,813 |
| Upstream nonempty lines | 262,243 |
| Unique normalized upstream lines | 262,178 |
| Normalized exact-text matches | 213,440 |
| Local records without exact matches | 2,373 |
| Exact-match proportion | 98.90% |
| Aggregate source URLs | 1 |

Text matching used Unicode NFC normalization and whitespace
normalization.

Input SHA-256 fingerprints:

- Aggregate Parquet: `04a0f2b64736df1efc9f32774b97bfe5e571d0a22af329819c756ed53745a135`
- Goldfish text: `86251b009c5af92fcc4e1060a39e308958a5f967353301cc9ea55b0001a2f9be`

The overlap supports substantial textual correspondence, not
complete record-level provenance or legal authorization.

Unmatched records require further investigation. Differences
may reflect source versions, preprocessing, or other origins.

Eligibility decision: QUARANTINED.

#### Normalization sensitivity investigation

Audit date: 2026-11-24.

A follow-up comparison investigated the 2,373 records that did
not match the inspected Goldfish source under NFC and whitespace
normalization.

| Comparison | Records |
|---|---:|
| Initial NFC exact matches | 213,440 |
| Initially unmatched | 2,373 |
| Additional NFKC matches | 0 |
| Additional punctuation/whitespace-insensitive matches | 2,095 |
| Remaining unmatched after relaxed checks | 278 |

All 2,373 initially unmatched records had distinct NFC-normalized
texts.

The initially unmatched texts had a median length of 41
characters and a 90th-percentile length of 105 characters.

The remaining 278 texts had a median length of 43 characters
and a 90th-percentile length of 134 characters.

The additional 2,095 correspondences are diagnostic only.
Removing punctuation and whitespace can produce accidental
matches and does not independently establish record lineage.

The remaining 278 records may differ because of preprocessing,
source versions, or other origins. Their provenance remains
unresolved.

This investigation does not establish training permission,
redistribution rights, or complete record-level attribution.

Eligibility decision: QUARANTINED.

### rural_women

The aggregate declares CC-BY-4.0.

The investigated upstream Rural Women Bhojpuri dataset declares
CC BY-SA 4.0.

Privacy processing has been completed for the 211 local records
under a single-reviewer workflow, but independent privacy
verification and secondary-use eligibility remain unresolved.


#### Upstream publication and consent evidence

Verification date: 2026-11-24.

Primary dataset:
https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri

Dataset card revision examined:
https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri/blob/b8058d00de0bc4d89beeb568f6ca431848a9fe14/README.md

Primary publication:
Joshi et al. (2025), "Recognizing Every Voice: Towards
Inclusive ASR for Rural Bhojpuri Women."
https://arxiv.org/html/2506.09653

Verified source-level findings:

- Original dataset licence declaration: CC BY-SA 4.0.
- Aggregate licence declaration: CC-BY-4.0.
- Original purpose: inclusive Bhojpuri ASR research.
- The source contains real and synthetic speech material.
- The paper reports informed consent during data collection.
- The consent description does not independently verify the
  precise scope of every permitted secondary research use.
- Source domains include health, agriculture, government
  schemes, finance, and everyday conversation.
- Service-related utterances are not automatically grievances.

Local processing evidence:

- 211 candidate transcripts have undergone the existing
  privacy review and redaction workflow.
- 176 were marked clear and 35 required redaction.
- All 35 redacted records were subsequently approved within
  the same-reviewer workflow.
- Independent privacy verification has not occurred.
- These records have not been approved for model training.

Outstanding questions:

1. Confirm applicable licensing and attribution obligations.
2. Clarify secondary-use and redistribution conditions.
3. Independently assess privacy risks where appropriate.
4. Establish speaker and source leakage safeguards.
5. Assess linguistic relevance separately from grievance labels.

Eligibility decision: QUARANTINED.

#### Quarantined candidate structural audit

Audit date: 2026-11-24.

The published, privacy-processed candidate was inspected
using aggregate statistics only. No transcript contents
were displayed.

| Measure | Result |
|---|---:|
| Candidate records | 211 |
| Unique record IDs | 211 |
| Empty normalized texts | 0 |
| Unique normalized texts | 211 |
| Duplicate excess rows | 0 |
| Bhojpuri language records | 211 |
| Reviewer-cleared records | 176 |
| Redacted and reviewer-approved records | 35 |
| Minimum text length | 13 characters |
| Median text length | 84 characters |
| Maximum text length | 270 characters |
| Records marked QUARANTINED | 211 |

Research interpretation:

- The candidate has no detected empty texts, repeated
  normalized texts, or duplicate record identifiers.
- These findings support structural readiness for a
  possible future annotation workflow.
- They do not establish linguistic authenticity or
  grievance-domain relevance.
- Internal uniqueness does not establish independence
  from upstream datasets, speakers, or translations.
- Single-reviewer privacy approval does not guarantee
  anonymization.
- Permission for secondary use remains unresolved.
- No grievance labels have been assigned or inferred.

Current suitability decisions:

- Structural readiness: PASS.
- Linguistic research eligibility: NOT ESTABLISHED.
- Civic grievance classification eligibility: NOT ESTABLISHED.
- Model-training eligibility: NOT APPROVED.

Overall eligibility decision: QUARANTINED.
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
