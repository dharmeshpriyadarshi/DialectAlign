
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "bhojpuri_corpus"
    / "BhojpuriCorpus.parquet"
)

REQUIRED_COLUMNS = {"id", "text", "source", "license", "url"}

QUARANTINED_SOURCES = {"fish_food"}

RANDOM_SEED = 42
SAMPLE_SIZE = 5

LATIN_PATTERN = r"[A-Za-z]"
DEVANAGARI_PATTERN = r"[\u0900-\u097F]"
CORRUPTION_PATTERN = r"\uFFFD|\x00"
HTML_PATTERN = r"<[^>]+>|&(?:amp|nbsp|lt|gt|quot|#\d+);"


def load_corpus():
    """Load the corpus and validate its schema."""

    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Corpus not found: {DATA_PATH}"
        )

    df = pd.read_parquet(DATA_PATH)

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return df


def audit_source(source_name, source_df):
    """Perform an independent audit of a source partition."""

    total_records = len(source_df)
    text = source_df["text"]

    missing_text = int(text.isna().sum())

    valid_text = text.dropna().astype(str)
    empty_mask = valid_text.str.strip().eq("")

    empty_text = int(empty_mask.sum())
    nonempty_text = valid_text[~empty_mask]

    word_counts = nonempty_text.str.split().str.len()

    duplicate_text = int(nonempty_text.duplicated().sum())

    latin_count = int(
        nonempty_text.str.contains(
            LATIN_PATTERN, regex=True
        ).sum()
    )

    devanagari_count = int(
        nonempty_text.str.contains(
            DEVANAGARI_PATTERN, regex=True
        ).sum()
    )

    corruption_count = int(
        nonempty_text.str.contains(
            CORRUPTION_PATTERN, regex=True
        ).sum()
    )

    html_count = int(
        nonempty_text.str.contains(
            HTML_PATTERN, regex=True
        ).sum()
    )

    valid_count = len(nonempty_text)

    def percentage(count):
        return round(
            100 * count / valid_count, 2
        ) if valid_count else 0.0

    status = (
        "QUARANTINED"
        if source_name in QUARANTINED_SOURCES
        else "PENDING REVIEW"
    )

    print("\n" + "=" * 75)
    print(f"SOURCE: {source_name}")
    print(f"REVIEW STATUS: {status}")
    print("=" * 75)

    print("\n--- RECORD INTEGRITY ---")
    print(f"Total records: {total_records:,}")
    print(f"Missing text: {missing_text:,}")
    print(f"Empty text: {empty_text:,}")
    print(f"Nonempty text: {valid_count:,}")
    print(f"Exact duplicate texts: {duplicate_text:,}")

    print("\n--- DECLARED LICENCE DISTRIBUTION ---")
    print(
        source_df["license"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\n--- SOURCE URL DISTRIBUTION ---")
    print(
        source_df["url"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\n--- TEXT LENGTH DISTRIBUTION ---")

    if not word_counts.empty:
        print(
            word_counts.describe(
                percentiles=[0.25, 0.50, 0.75, 0.95]
            ).round(2).to_string()
        )
    else:
        print("No nonempty text available.")

    print("\n--- SCRIPT AND QUALITY INDICATORS ---")

    print(
        f"Latin character presence: "
        f"{latin_count:,} ({percentage(latin_count)}%)"
    )

    print(
        f"Devanagari character presence: "
        f"{devanagari_count:,} "
        f"({percentage(devanagari_count)}%)"
    )

    print(f"Potential corruption indicators: {corruption_count:,}")
    print(f"Possible HTML artifacts: {html_count:,}")

    print("\n--- REPRODUCIBLE TEXT SAMPLES ---")

    samples = nonempty_text.sample(
        n=min(SAMPLE_SIZE, valid_count),
        random_state=RANDOM_SEED
    )

    for number, sample in enumerate(samples, start=1):
        print(f"\n[{number}] {sample[:300]}")

    return {
        "source": source_name,
        "records": total_records,
        "missing": missing_text,
        "empty": empty_text,
        "duplicates": duplicate_text,
        "median_words": (
            round(float(word_counts.median()), 2)
            if not word_counts.empty else None
        ),
        "latin_pct": percentage(latin_count),
        "devanagari_pct": percentage(devanagari_count),
        "corruption_flags": corruption_count,
        "html_flags": html_count,
        "status": status,
    }


def main():
    """Execute the complete source-level corpus audit."""

    df = load_corpus()

    print("=" * 75)
    print("DIALECTALIGN — BHOJPURI SOURCE-LEVEL AUDIT")
    print("=" * 75)

    print(f"Dataset: {DATA_PATH}")
    print(f"Total records: {len(df):,}")
    print(f"Total sources: {df['source'].nunique()}")

    audit_results = []

    for source_name, source_df in df.groupby(
        "source", dropna=False
    ):
        result = audit_source(source_name, source_df)
        audit_results.append(result)

    summary = pd.DataFrame(audit_results)

    print("\n" + "=" * 75)
    print("CONSOLIDATED SOURCE AUDIT SUMMARY")
    print("=" * 75)

    print(
        summary.sort_values(
            "records", ascending=False
        ).to_string(index=False)
    )

    print("\nAudit completed.")
    print("Original corpus remains unchanged.")
    print("No source has been automatically approved.")


if __name__ == "__main__":
    main()
