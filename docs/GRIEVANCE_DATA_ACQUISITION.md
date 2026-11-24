# DialectAlign ? Authentic Grievance Data Acquisition

Assessment date: 2026-11-24

## 1. Research objective

Acquire authentic, legally usable civic grievance text to
evaluate dialect-aware and cross-lingual classification in
Bhojpuri, Maithili, Hindi, and English.

Do not confuse synthetic examples, translated material,
general language corpora, or aggregate statistics with
authentic, independently labeled grievance narratives.

## 2. Candidate source register

### Candidate A ? CPGRAMS / DARPG

Official portal: https://pgportal.gov.in/
Open data portal: https://data.gov.in/

Evidence:
DARPG's 2019 grievance-data hackathon described
individual grievance details as restricted datasets,
with access provided to registered participants.

That historical access arrangement is not evidence
of a currently available research dataset.

Questions:
- Can a de-identified textual research extract be provided?
- What permission covers analysis, annotation and training?
- Which languages actually occur in original submissions?
- Can source, time and duplicate-group metadata be retained?
- What publication and retention restrictions apply?

Status: ACCESS NOT ESTABLISHED.
Training approval: NO.

### Candidate B ? Bihar Lok Shikayat

Official portal: https://lokshikayat.bihar.gov.in/

Evidence:
Official state grievance redressal system with direct
relevance to the Bihar regional research setting.

Questions:
- Is a privacy-preserving research partnership possible?
- Can original-language complaint texts be supplied?
- Are Bhojpuri and Maithili distinguishable in the records?
- What consent, administrative and privacy conditions apply?
- Can source identifiers support leakage-aware evaluation?

Do not scrape personal complaints or case details
without appropriate authorization.

Status: ACCESS NOT ESTABLISHED.
Training approval: NO.

### Candidate C ? CivicComp

Publication:
https://doi.org/10.1109/WiSPNET69615.2026.11489415

Potential implementation reference:
https://github.com/MeenalSinha/CivicAI

Evidence:
A 2026 paper describes Hindi-English civic complaint
categorization using material derived from municipal data
and a domain-aware translation process.

Third-party repository claims about dataset size, origin,
de-identification and licensing require verification
against the original research release.

Questions:
- Locate the authors' authoritative dataset release.
- Verify its licence, redistribution and training terms.
- Confirm authentic original-language versus translated text.
- Verify labels and original complaint provenance.
- Identify translation-pair and source-group leakage risks.
- Assess whether personally identifying details remain.

Status: PROSPECTIVE BENCHMARK; NOT VERIFIED.
Training approval: NO.

#### CivicComp author-linked release audit

Assessment date: 2026-11-24.

Author-linked Kaggle release:
https://www.kaggle.com/datasets/shyamtripathi373/civiccomp-hien-hindienglish-civic-complaints

Publication DOI:
https://doi.org/10.1109/WiSPNET69615.2026.11489415

The dataset documentation inspected manually declares:

- Dataset name: CivicComp-HiEn.
- Licence: CC BY-SA 4.0.
- Claimed origin: BBMP civic complaints, Bengaluru.
- Languages: English, Hindi, and Hinglish.
- Parallel columns: complaint_en, complaint_hi,
  complaint_hinglish.
- Shared complaint identifier: id.
- Complaint label: category.
- Published splits: train, dev, and test.
- Privacy processing: rule-based PII removal.
- Hindi and Hinglish: multilingual expansions of
  English complaint material.

The licence declaration is not yet independently checked
against the actual LICENSE.txt and source rights.

Reported split counts:

| Split | Complaint triplets |
|---|---:|
| Train | 8,000 |
| Dev | 1,600 |
| Test | 1,600 |
| Arithmetic total | 11,200 |

Three language variants per triplet imply 33,600 text
instances if these reported split counts are correct.

The same documentation separately claims 16,000 aligned
triplets and 48,000 text instances.

The IEEE publication also reports 48,000 complaints,
but its abstract contains a language breakdown that
requires clarification.

Actual CSV row counts have not been verified.

Research implications:

- The dataset may support Hindi-English-Hinglish
  cross-lingual complaint classification benchmarks.
- Language variants sharing an ID must remain in the
  same partition for leakage-aware evaluation.
- Translated Hindi and Hinglish must not be described
  as independent native-language complaint submissions.
- This dataset provides no documented Bhojpuri or
  Maithili coverage.
- The original BBMP records' provenance and applicable
  permissions remain to be verified.
- Rule-based PII removal is not proof of anonymization.
- Original labels and quality-control claims require
  independent assessment.

Next evidence required:

1. Exact row counts from the published CSV files.
2. Actual LICENSE.txt and applicable source permissions.
3. File-level version and provenance information.
4. Whether IDs and translation groups are split safely.
5. Privacy and label-quality verification.

Decision: PROSPECTIVE BENCHMARK.
Training approval: NO.

#### CivicComp Kaggle release inspection

Assessment date: 2026-11-24.

Author-linked release:
https://www.kaggle.com/datasets/shyamtripathi373/civiccomp-hien-hindienglish-civic-complaints

The inspected LICENSE.txt declares CC BY-SA 4.0.

It identifies the original creators as Vivek Mathew and
Haji Shariefullah, with modifications attributed to the
CivicComp research team:

- Shyam Tripathi
- Kothamsu Hridayesh
- K. Ashwini
- Kritika Agrahari

Institution: Amrita Vishwa Vidyapeetham, Chennai Campus.
Claimed original source: https://newdata.opencity.in

These are release-document claims. The specific original
OpenCity resources and their applicable rights have not
yet been matched to individual CivicComp records.

The README describes parallel English, Hindi, and
Hinglish complaint triplets, category labels, and fixed
train, development, and test splits.

The README's split counts total 11,200 triplets and
33,600 language instances, whereas it separately claims
16,000 triplets and 48,000 language instances.

The Kaggle preview appears to expose a different schema,
including:

- Sy_No
- Complaint_Title
- Text_en
- Text_hi
- Text_hinglish
- primary_category
- secondary_category
- Severity
- Model_Name

Exact column names require confirmation from the file
header. The observed unique-value counts of 30,752,
27,798, and 30,158 do not establish total row counts.

The preview also displayed ERROR values in at least
one profiled field. Their location, frequency, and
meaning have not been independently verified.

Before eligibility assessment, verify:

1. Actual CSV filename, schema, and number of rows.
2. Whether claimed train/dev/test files really exist.
3. Identifier uniqueness and translation-group integrity.
4. Missing values, error placeholders, and label quality.
5. Exact upstream OpenCity resource and source licence.
6. Privacy, attribution, and downstream-use obligations.

Current decision: PROSPECTIVE BENCHMARK.
Model-training approval: NOT ESTABLISHED.

### Candidate D ? Consented field-data partnership

Potential route:
Collaboration with an authorized institution,
research organization or community partner.

No such dataset or agreement is currently established.

Requirements:
- Voluntary, documented informed consent.
- Clear research and withdrawal conditions.
- Appropriate ethics and privacy review.
- Original language or dialect recording.
- Secure collection and access restrictions.
- Independent annotation and disagreement review.
- No implication that participation affects public benefits.

Status: PROPOSED ONLY.
Training approval: NO.

## 3. Language evidence requirements

For each eligible source, record:

- Original language and script.
- Native text versus translation or transliteration.
- Language-identification uncertainty.
- Regional or dialect provenance where supportable.
- Speaker, translation and collection grouping where available.

Do not fabricate Bhojpuri or Maithili authenticity
by translating standard Hindi complaints.

## 4. Mandatory acquisition gates

Before obtaining complaint-level text:

1. Verify the original source and dataset version.
2. Establish permitted access and use.
3. Assess personal-data and consent implications.
4. Confirm safe storage and retention requirements.
5. Define a legitimate research objective.
6. Record any redistribution or model-release restrictions.

Before training:

1. Establish an authentic task-relevant labeled sample.
2. Define grievance and non-grievance criteria.
3. Audit class and language distribution.
4. Audit source, speaker, duplicate and translation leakage.
5. Establish separated evaluation groups and baselines.
6. Record use-specific approval and outstanding limitations.

## 5. Current acquisition decision

No authentic labeled civic grievance corpus is confirmed
as acquired and eligible for DialectAlign model training.

Existing synthetic examples remain engineering fixtures.
The Rural Women Bhojpuri candidate remains quarantined.

No source should be downloaded, scraped, annotated or
trained upon solely because it appears in this register.
