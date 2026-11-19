
import argparse
import json
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
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

BASE_URL = "https://datasets-server.huggingface.co/rows"
DATASET = "ai4bharat/Rural_Women_Bhojpuri"
CONFIG = "default"

EXPECTED_ROWS = {
    "benchmark": 444,
    "train_real": 400,
    "train_synthetic": 77967,
}

BATCH_SIZE = 100
REQUEST_DELAY = 1.0
MAX_RETRIES = 5
TIMEOUT = 60


def normalize_text(text):
    """Normalize Unicode and whitespace without altering dialect."""

    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFC", text)

    return " ".join(text.split())


def load_local_records():
    """Extract the rural_women partition."""

    df = pd.read_parquet(
        DATA_PATH,
        columns=["id", "text", "source"],
    )

    records = df[df["source"] == "rural_women"].copy()

    records["normalized_text"] = records["text"].map(
        normalize_text
    )

    return records


def fetch_batch(split, offset, length):
    """Retrieve a batch with bounded retry handling."""

    parameters = urllib.parse.urlencode({
        "dataset": DATASET,
        "config": CONFIG,
        "split": split,
        "offset": offset,
        "length": length,
    })

    url = f"{BASE_URL}?{parameters}"

    for attempt in range(MAX_RETRIES):

        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "DialectAlign-Research-Audit/1.0"
                },
            )

            with urllib.request.urlopen(
                request, timeout=TIMEOUT
            ) as response:
                return json.load(response)

        except urllib.error.HTTPError as error:

            if error.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == MAX_RETRIES - 1:
                raise

            delay = 2 ** (attempt + 1)

            retry_after = error.headers.get("Retry-After")

            if retry_after and retry_after.isdigit():
                delay = max(delay, int(retry_after))

            print(
                f"HTTP {error.code}. "
                f"Retrying after {delay} seconds."
            )

            time.sleep(delay)

        except (urllib.error.URLError, TimeoutError):

            if attempt == MAX_RETRIES - 1:
                raise

            time.sleep(2 ** (attempt + 1))


def compare_split(split, local_texts):
    """Compare local transcripts against an upstream split."""

    expected_total = EXPECTED_ROWS[split]

    matched_texts = set()
    matched_upstream_rows = 0

    retrieved_rows = 0
    missing_text = 0
    truncated_text = 0

    seen_indices = set()

    print("\n" + "=" * 70)
    print(f"SPLIT: {split}")
    print("=" * 70)

    for offset in range(0, expected_total, BATCH_SIZE):

        length = min(
            BATCH_SIZE,
            expected_total - offset
        )

        data = fetch_batch(split, offset, length)

        if data.get("partial") is not False:
            raise RuntimeError(
                f"Incomplete API coverage for {split}"
            )

        if data.get("num_rows_total") != expected_total:
            raise RuntimeError(
                f"Unexpected row count for {split}. "
                "Upstream dataset may have changed."
            )

        rows = data["rows"]

        if len(rows) != length:
            raise RuntimeError(
                f"Incomplete batch at offset {offset}"
            )

        for item in rows:

            row_index = item["row_idx"]

            if row_index in seen_indices:
                raise RuntimeError(
                    f"Repeated upstream row index: {row_index}"
                )

            seen_indices.add(row_index)
            retrieved_rows += 1

            if "text" in item.get("truncated_cells", []):
                truncated_text += 1
                continue

            text = normalize_text(
                item["row"].get("text")
            )

            if not text:
                missing_text += 1
                continue

            if text in local_texts:
                matched_texts.add(text)
                matched_upstream_rows += 1

        print(
            f"Retrieved: {retrieved_rows:,}/{expected_total:,}"
            f" | Unique matches: {len(matched_texts):,}",
            flush=True,
        )

        time.sleep(REQUEST_DELAY)

    complete = (
        retrieved_rows == expected_total
        and seen_indices == set(range(expected_total))
        and truncated_text == 0
    )

    print("\n--- SPLIT RESULTS ---")
    print(f"Expected rows: {expected_total:,}")
    print(f"Retrieved rows: {retrieved_rows:,}")
    print(f"Missing or empty transcripts: {missing_text:,}")
    print(f"Truncated transcripts: {truncated_text:,}")
    print(f"Matched upstream rows: {matched_upstream_rows:,}")
    print(f"Unique matched local texts: {len(matched_texts):,}")
    print(f"Complete retrieval: {complete}")

    return matched_texts, complete


def main():

    parser = argparse.ArgumentParser(
        description="Audit rural_women transcript provenance."
    )

    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Also compare the train_synthetic split.",
    )

    args = parser.parse_args()

    local_records = load_local_records()

    local_texts = {
        text
        for text in local_records["normalized_text"]
        if text
    }

    print("=" * 70)
    print("DIALECTALIGN - RURAL WOMEN PROVENANCE AUDIT")
    print("=" * 70)

    print(f"Local records: {len(local_records):,}")
    print(f"Unique normalized texts: {len(local_texts):,}")

    splits = ["benchmark", "train_real"]

    if args.include_synthetic:
        splits.append("train_synthetic")

    results = {}
    coverage = {}

    for split in splits:

        results[split], coverage[split] = compare_split(
            split,
            local_texts,
        )

    print("\n" + "=" * 70)
    print("CONSOLIDATED PROVENANCE RESULTS")
    print("=" * 70)

    all_matches = set().union(*results.values())

    for split, matches in results.items():

        matched_records = int(
            local_records["normalized_text"]
            .isin(matches)
            .sum()
        )

        print(
            f"{split}: {matched_records:,} local records matched"
            f" | Complete retrieval: {coverage[split]}"
        )

    multiple_split_matches = {
        text for text in local_texts
        if sum(
            text in matches
            for matches in results.values()
        ) > 1
    }

    matched_records = int(
        local_records["normalized_text"]
        .isin(all_matches)
        .sum()
    )

    multiple_split_records = int(
        local_records["normalized_text"]
        .isin(multiple_split_matches)
        .sum()
    )

    print(f"\nTotal matched local records: {matched_records:,}")

    print(
        f"Unmatched local records: "
        f"{len(local_records) - matched_records:,}"
    )

    print(
        f"Local records matching multiple splits: "
        f"{multiple_split_records:,}"
    )

    print(f"Splits examined: {', '.join(splits)}")

    print(
        "All upstream splits examined:",
        set(splits) == set(EXPECTED_ROWS),
    )

    print("All examined splits fully retrieved:", all(coverage.values()))

    print("\nAudit completed.")
    print("No audio recordings downloaded.")
    print("No transcripts or personal metadata exported.")
    print("Original corpus remains unchanged.")
    print("Source status: QUARANTINED")


if __name__ == "__main__":
    main()
