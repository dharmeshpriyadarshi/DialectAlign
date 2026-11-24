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
