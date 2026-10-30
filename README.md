
# DialectAlign: Cross-Lingual Civic Grievance Triage

## Overview

DialectAlign is a low-resource NLP framework designed to classify and route regional dialect civic complaints. This repository contains the data pipelines, model architectures, and inference endpoints necessary for cross-lingual triage.

## Directory Taxonomy

* `configs/`: Model hyperparameters and pipeline configurations (YAML).
* `data/`: Raw and processed data storage (Untracked).
* `notebooks/`: Exploratory Data Analysis (EDA).
* `scripts/`: Execution scripts for scraping and deployment tasks.
* `src/`: Core logic (data processing, model definitions, training loops).
* `tests/`: Pytest suite for unit and integration testing.

## Environment Setup

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
