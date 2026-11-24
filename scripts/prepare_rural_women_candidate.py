
"""Build a quarantined, privacy-processed Rural Women Bhojpuri candidate.

Not approved for model training, public redistribution, or deployment.
"""

import csv
import hashlib
import io
import json
import os
import re
import tempfile

from collections import Counter
from pathlib import Path

from scripts.review_rural_women_privacy import (
    prepare_records,
    load_previous_reviews,
)
from scripts.redact_rural_women_privacy import (
    PLACEHOLDERS,
    hash_text,
    load_redactions,
)
from scripts.validate_rural_women_privacy import load_validations


ROOT = Path(__file__).resolve().parents[1]

SOURCE_PATH = (
    ROOT / "data" / "external"
    / "bhojpuri_corpus" / "BhojpuriCorpus.parquet"
)

PRIVACY_DIR = ROOT / "data" / "processed" / "privacy"

OUTPUT_CSV = PRIVACY_DIR / "rural_women_candidate.csv"
OUTPUT_MANIFEST = (
    PRIVACY_DIR / "rural_women_candidate_manifest.json"
)

INPUT_FILES = {
    "source_parquet": SOURCE_PATH,
    "manual_reviews": PRIVACY_DIR / "rural_women_review.csv",
    "redactions": PRIVACY_DIR / "rural_women_redactions.csv",
    "validations": PRIVACY_DIR / "rural_women_validation.csv",
}

FIELDS = [
    "record_id",
    "text",
    "language",
    "source_partition",
    "privacy_status",
    "replacement_count",
    "text_sha256",
    "research_use_status",
]

APPROVED_PLACEHOLDERS = set(PLACEHOLDERS.values())
PLACEHOLDER_PATTERN = re.compile(r"\[[A-Z_]+_REDACTED\]")


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def atomic_write(path, content):
    """Write bytes through a same-directory temporary file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary, path)

    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def validate_input_files():
    for label, path in INPUT_FILES.items():
        if not path.is_file():
            raise FileNotFoundError(
                f"Required {label} file is missing: {path}"
            )


def build_candidate():
    validate_input_files()

    records = prepare_records()
    reviews = load_previous_reviews()
    redactions = load_redactions()
    validations = load_validations()

    original_ids = [record["record_id"] for record in records]

    if len(set(original_ids)) != len(original_ids):
        raise ValueError("Duplicate original record IDs detected.")

    original_id_set = set(original_ids)

    if original_id_set != set(reviews):
        raise ValueError("Manual review coverage mismatch.")

    redaction_target_ids = {
        record_id
        for record_id, review in reviews.items()
        if review["decision"] == "REDACTION_REQUIRED"
    }

    if set(redactions) != redaction_target_ids:
        raise ValueError("Redaction target coverage mismatch.")

    if set(validations) != redaction_target_ids:
        raise ValueError("Validation target coverage mismatch.")

    rows = []
    counts = Counter()
    replacement_total = 0

    for record in sorted(records, key=lambda item: item["record_id"]):
        record_id = record["record_id"]
        original = record["text"]
        original_hash = hash_text(original)
        review = reviews[record_id]

        if original_hash != record["text_sha256"]:
            raise ValueError(
                f"Original fingerprint mismatch: {record_id}"
            )

        if original_hash != review["text_sha256"]:
            raise ValueError(
                f"Review fingerprint mismatch: {record_id}"
            )

        decision = review["decision"]

        if decision == "CLEAR":
            processed_text = original
            privacy_status = "REVIEWER_CLEARED"
            replacements = 0

        elif decision == "EXCLUDE":
            counts["excluded_at_initial_review"] += 1
            continue

        elif decision == "REDACTION_REQUIRED":
            redaction = redactions[record_id]
            validation = validations[record_id]

            processed_text = redaction["redacted_text"]
            processed_hash = hash_text(processed_text)

            if redaction["original_sha256"] != original_hash:
                raise ValueError(
                    f"Redaction origin mismatch: {record_id}"
                )

            if redaction["redacted_sha256"] != processed_hash:
                raise ValueError(
                    f"Redacted fingerprint mismatch: {record_id}"
                )

            if processed_text == original:
                raise ValueError(
                    f"Unchanged redaction target: {record_id}"
                )

            if (
                validation["original_sha256"] != original_hash
                or validation["redacted_sha256"] != processed_hash
            ):
                raise ValueError(
                    f"Stale validation decision: {record_id}"
                )

            placeholders = PLACEHOLDER_PATTERN.findall(processed_text)

            if not placeholders or any(
                placeholder not in APPROVED_PLACEHOLDERS
                for placeholder in placeholders
            ):
                raise ValueError(
                    f"Invalid redaction placeholders: {record_id}"
                )

            replacements = int(redaction["replacement_count"])

            if len(placeholders) != replacements:
                raise ValueError(
                    f"Replacement count mismatch: {record_id}"
                )

            if validation["decision"] == "EXCLUDE":
                counts["excluded_after_validation"] += 1
                continue

            if validation["decision"] != "APPROVED":
                raise ValueError(
                    f"Unresolved validation: {record_id}"
                )

            privacy_status = "REDACTED_REVIEWER_APPROVED"
            replacement_total += replacements

        else:
            raise ValueError(
                f"Unresolved privacy decision: {record_id}"
            )

        rows.append({
            "record_id": record_id,
            "text": processed_text,
            "language": "Bhojpuri",
            "source_partition": "rural_women",
            "privacy_status": privacy_status,
            "replacement_count": replacements,
            "text_sha256": hash_text(processed_text),
            "research_use_status": "QUARANTINED",
        })

        counts[privacy_status] += 1

    if len(rows) + sum(
        counts[key]
        for key in (
            "excluded_at_initial_review",
            "excluded_after_validation",
        )
    ) != len(records):
        raise ValueError("Candidate record accounting mismatch.")

    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=FIELDS,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    candidate_bytes = output.getvalue().encode("utf-8")
    candidate_hash = hashlib.sha256(candidate_bytes).hexdigest()

    manifest = {
        "schema_version": 1,
        "dataset": "rural_women_bhojpuri_candidate",
        "research_use_status": "QUARANTINED",
        "training_approved": False,
        "redistribution_approved": False,
        "privacy_assurance": (
            "Single-reviewer assessment; independent verification "
            "and contextual re-identification assessment unresolved."
        ),
        "domain_suitability": (
            "Authentic linguistic material; civic grievance labels "
            "and grievance-domain suitability not established."
        ),
        "source": {
            "aggregate_partition": "rural_women",
            "upstream": "ai4bharat/Rural_Women_Bhojpuri",
            "upstream_text_overlap": (
                "Prior normalized-text investigation matched 211 "
                "local records to upstream train_real records; "
                "exclusive origin and speaker independence unverified."
            ),
            "aggregate_license_declaration": "CC-BY",
            "upstream_license_declaration": "CC-BY-SA-4.0",
            "license_reconciliation": "UNRESOLVED",
            "secondary_use_permission": "UNRESOLVED",
        },
        "counts": {
            "original_records": len(records),
            "candidate_records": len(rows),
            "reviewer_cleared": counts["REVIEWER_CLEARED"],
            "redacted_reviewer_approved": (
                counts["REDACTED_REVIEWER_APPROVED"]
            ),
            "excluded_at_initial_review": (
                counts["excluded_at_initial_review"]
            ),
            "excluded_after_validation": (
                counts["excluded_after_validation"]
            ),
            "redaction_replacements": replacement_total,
        },
        "inputs_sha256": {
            label: sha256_file(path)
            for label, path in INPUT_FILES.items()
        },
        "candidate_sha256": candidate_hash,
        "candidate_file": OUTPUT_CSV.name,
        "preparation_script_sha256": sha256_file(
            Path(__file__).resolve()
        ),
    }

    manifest_bytes = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    # Both files remain under the Git-ignored privacy directory.
    atomic_write(OUTPUT_CSV, candidate_bytes)
    atomic_write(OUTPUT_MANIFEST, manifest_bytes)

    print("QUARANTINED CANDIDATE CORPUS")
    print("=" * 60)
    print("Original records:", len(records))
    print("Candidate records:", len(rows))
    print("Reviewer-cleared records:", counts["REVIEWER_CLEARED"])
    print(
        "Approved redacted records:",
        counts["REDACTED_REVIEWER_APPROVED"],
    )
    print("Total replacements:", replacement_total)
    print(
        "Excluded records:",
        counts["excluded_at_initial_review"]
        + counts["excluded_after_validation"],
    )
    print("Candidate SHA-256:", candidate_hash)
    print("Research-use status: QUARANTINED")
    print("Training approved: NO")
    print("Candidate file:", OUTPUT_CSV)
    print("Manifest file:", OUTPUT_MANIFEST)


if __name__ == "__main__":
    build_candidate()
