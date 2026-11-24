# DialectAlign — Data Provenance and Research-Use Status

## 1. Purpose

This document records known data sources, provenance investigations, privacy processing, licensing concerns, and unresolved research-use conditions for DialectAlign.

Documentation of a source does not constitute permission to use it. All external research data remains quarantined until the applicable eligibility checks are completed.

## 2. Dataset Categories

| Category | Current status | Permitted project role |
|---|---|---|
| Synthetic civic examples | Available | Engineering tests only |
| Aggregated Bhojpuri text corpus | Acquired locally; under audit | Quarantined linguistic resource |
| Rural Women Bhojpuri transcripts | Privacy-processed; under eligibility review | Quarantined candidate resource |
| Government grievance records | Not acquired | No current research use |
| NGO grievance or parallel corpora | Not acquired | No current research use |
| Maithili grievance records | Not acquired | No current research use |

Synthetic samples must not be presented as evidence of real-world grievance classification performance.

## 3. Aggregated Bhojpuri Corpus

Local source: `data/external/bhojpuri_corpus/BhojpuriCorpus.parquet`

The acquired dataset contains 386,032 records across 13 declared source partitions.

Completed exploratory work includes source-level counts, missingness checks, duplicate checks, text-quality indicators, initial vocabulary analysis, and selected upstream provenance comparisons.

The aggregate's metadata is not sufficient to establish independent permission for every underlying source.

### 3.1 Fish-food / Goldfish overlap

The earlier audit found 213,440 exact matches between 215,813 `fish_food` records and the locally inspected upstream Goldfish text collection.

The aggregate reports CC-BY for this partition, while the investigated upstream material carries a CC-BY-NC-SA declaration.

This licensing discrepancy is unresolved. Matching text does not establish that the aggregate licence supersedes the applicable upstream terms.

No training eligibility is granted on the basis of the aggregate licence alone.

## 4. Rural Women Bhojpuri

Upstream source:
https://huggingface.co/datasets/ai4bharat/Rural_Women_Bhojpuri

Relevant publication: Joshi et al. (2025), arXiv:2506.09653.

The aggregate contains 211 records attributed to this source.

A normalized-text comparison matched all 211 local records to inspected upstream `train_real` records and found no exact matches in the inspected `benchmark` split. This does not establish speaker-level independence or prove that every upstream partition has been exhaustively audited.

The aggregate declares CC-BY; the investigated upstream dataset declares CC-BY-SA-4.0. Applicable obligations require source-specific review.

The source publication describes collection and consent practices, but this alone does not establish permission for every proposed secondary use, model-training activity, redistribution, or deployment.

These transcripts are authentic language material, not automatically authentic civic grievances.

### 4.1 Privacy processing

Completed processing of the 211 local records:

- 211 records manually reviewed.
- 176 records marked CLEAR by the reviewer.
- 35 records subjected to targeted redaction.
- 53 sensitive-span replacements in the final redacted versions.
- 35 redacted records approved after manual validation and remediation.
- Zero residual matches in the final tested regex-pattern screening.

The original source data remains unchanged. Review decisions, redactions, validations, and backups are stored locally under the Git-ignored `data/` directory.

Privacy validation was performed through the current single-reviewer workflow. It does not guarantee anonymization, rule out contextual re-identification, or constitute independent privacy verification.

The automated screening also has limitations, particularly for spoken identifiers, indirect identifiers, and contextual disclosure.

### 4.2 Current decision

Research-use status: QUARANTINED.

Privacy processing alone does not authorize model training, publication, public redistribution, or deployment.

## 5. Civic Grievance Data Acquisition

No verified CPGRAMS grievance dataset has been incorporated into the research corpus.

A government data-access request was made, but acquisition and permission have not been confirmed.

No NGO grievance corpus has been verified as acquired with documented secondary-use consent.

Until suitable authentic labelled grievances are obtained, supervised grievance-classification experiments must not be represented as empirical research results.

## 6. Data Eligibility Requirements

Before approving a source for a specific research use, document:

1. Original publisher and acquisition route.
2. Source version, collection period, and retrieval evidence.
3. Applicable source-specific licence and attribution obligations.
4. Consent scope and permitted downstream uses, where relevant.
5. Language authenticity, script characteristics, and domain suitability.
6. Privacy risks and review evidence.
7. Duplicate, translation, speaker, and source overlap risks.
8. Annotation suitability and quality limitations.
9. Explicit approval or exclusion decision for the proposed use.

A source can be suitable for linguistic analysis but unsuitable for supervised grievance classification.

## 7. Reproducibility and Data Protection

Keep source data, privacy review files, redacted transcripts, and validation records outside Git.

Commit code, documentation, aggregate statistics, configuration, and tests only after checking that they contain no personal information or restricted source content.

Preserve original data separately from derived data. Record processing parameters and hashes when generating research artifacts.

Any training, validation, and test partitions must be constructed using a leakage-aware protocol before model fitting.

## 8. Outstanding Work

- Review licence and permission obligations for selected external sources.
- Determine whether the Rural Women Bhojpuri material is eligible for the proposed secondary use.
- Obtain independent privacy review where feasible.
- Assess authentic grievance data availability and annotation suitability.
- Prepare a quarantined candidate corpus with explicit lineage.
- Establish the annotation and experimental evaluation protocols.

Overall external-data research-use status: NOT YET APPROVED.

This document reports current evidence and outstanding questions; it is not a certification of legal compliance or anonymization.
