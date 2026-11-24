
"""Regression tests for quarantined candidate corpus preparation."""

import csv
import json

from copy import deepcopy

import pytest

import scripts.prepare_rural_women_candidate as candidate


@pytest.fixture
def synthetic_inputs(tmp_path, monkeypatch):
    """Two fictional records; no real corpus data is accessed."""

    clear_id = "synthetic_clear_001"
    redact_id = "synthetic_redact_002"

    clear_text = "गाँव में पानी के समस्या बा"
    original_text = "हमार नाम DEMO_PERSON बा"
    redacted_text = "हमार नाम [NAME_REDACTED] बा"

    records = [
        {
            "record_id": clear_id,
            "text": clear_text,
            "text_sha256": candidate.hash_text(clear_text),
        },
        {
            "record_id": redact_id,
            "text": original_text,
            "text_sha256": candidate.hash_text(original_text),
        },
    ]

    reviews = {
        clear_id: {
            "record_id": clear_id,
            "text_sha256": candidate.hash_text(clear_text),
            "decision": "CLEAR",
        },
        redact_id: {
            "record_id": redact_id,
            "text_sha256": candidate.hash_text(original_text),
            "decision": "REDACTION_REQUIRED",
        },
    }

    redactions = {
        redact_id: {
            "record_id": redact_id,
            "original_sha256": candidate.hash_text(original_text),
            "redacted_text": redacted_text,
            "redacted_sha256": candidate.hash_text(redacted_text),
            "replacement_count": "1",
            "status": "REDACTED_PENDING_VALIDATION",
        },
    }

    validations = {
        redact_id: {
            "record_id": redact_id,
            "original_sha256": candidate.hash_text(original_text),
            "redacted_sha256": candidate.hash_text(redacted_text),
            "decision": "APPROVED",
        },
    }

    monkeypatch.setattr(
        candidate, "prepare_records", lambda: records
    )
    monkeypatch.setattr(
        candidate, "load_previous_reviews", lambda: reviews
    )
    monkeypatch.setattr(
        candidate, "load_redactions", lambda: redactions
    )
    monkeypatch.setattr(
        candidate, "load_validations", lambda: validations
    )

    input_files = {}

    for label in candidate.INPUT_FILES:
        path = tmp_path / f"{label}.test"
        path.write_text(
            f"Fictional test input: {label}",
            encoding="utf-8",
        )
        input_files[label] = path

    monkeypatch.setattr(candidate, "INPUT_FILES", input_files)

    output_csv = tmp_path / "candidate.csv"
    output_manifest = tmp_path / "candidate_manifest.json"

    monkeypatch.setattr(candidate, "OUTPUT_CSV", output_csv)
    monkeypatch.setattr(
        candidate, "OUTPUT_MANIFEST", output_manifest
    )

    return {
        "records": records,
        "reviews": reviews,
        "redactions": redactions,
        "validations": validations,
        "input_files": input_files,
        "output_csv": output_csv,
        "output_manifest": output_manifest,
        "clear_id": clear_id,
        "redact_id": redact_id,
        "clear_text": clear_text,
        "redacted_text": redacted_text,
    }


def test_valid_candidate_generation(synthetic_inputs):
    data = synthetic_inputs

    candidate.build_candidate()

    with data["output_csv"].open(
        "r", encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    manifest = json.loads(
        data["output_manifest"].read_text(encoding="utf-8")
    )

    assert len(rows) == 2

    by_id = {row["record_id"]: row for row in rows}
    assert len(by_id) == 2

    clear = by_id[data["clear_id"]]
    redacted = by_id[data["redact_id"]]

    assert clear["text"] == data["clear_text"]
    assert clear["privacy_status"] == "REVIEWER_CLEARED"
    assert clear["replacement_count"] == "0"

    assert redacted["text"] == data["redacted_text"]
    assert redacted["privacy_status"] == "REDACTED_REVIEWER_APPROVED"
    assert redacted["replacement_count"] == "1"

    for row in rows:
        assert row["text_sha256"] == candidate.hash_text(row["text"])
        assert row["research_use_status"] == "QUARANTINED"
        assert row["language"] == "Bhojpuri"

    assert manifest["counts"]["candidate_records"] == 2
    assert manifest["counts"]["reviewer_cleared"] == 1
    assert manifest["counts"]["redacted_reviewer_approved"] == 1
    assert manifest["counts"]["redaction_replacements"] == 1

    assert manifest["training_approved"] is False
    assert manifest["redistribution_approved"] is False
    assert manifest["research_use_status"] == "QUARANTINED"

    assert manifest["candidate_sha256"] == candidate.sha256_file(
        data["output_csv"]
    )

    for label, path in data["input_files"].items():
        assert manifest["inputs_sha256"][label] == (
            candidate.sha256_file(path)
        )


@pytest.mark.parametrize(
    "scenario, expected_error",
    [
        ("missing_review", "Manual review coverage mismatch"),
        ("missing_redaction", "Redaction target coverage mismatch"),
        ("stale_validation", "Stale validation decision"),
        ("unapproved_validation", "Unresolved validation"),
        ("changed_original", "Original fingerprint mismatch"),
        ("incorrect_replacement_count", "Replacement count mismatch"),
    ],
)
def test_invalid_input_rejected(
    synthetic_inputs, scenario, expected_error
):
    data = synthetic_inputs

    if scenario == "missing_review":
        data["reviews"].pop(data["clear_id"])

    elif scenario == "missing_redaction":
        data["redactions"].pop(data["redact_id"])

    elif scenario == "stale_validation":
        data["validations"][data["redact_id"]][
            "redacted_sha256"
        ] = "0" * 64

    elif scenario == "unapproved_validation":
        data["validations"][data["redact_id"]][
            "decision"
        ] = "UNCERTAIN"

    elif scenario == "changed_original":
        data["records"][0]["text"] += " altered"

    elif scenario == "incorrect_replacement_count":
        data["redactions"][data["redact_id"]][
            "replacement_count"
        ] = "9"

    with pytest.raises(ValueError, match=expected_error):
        candidate.build_candidate()

    assert not data["output_csv"].exists()
    assert not data["output_manifest"].exists()


def test_atomic_write_preserves_old_file_on_replace_failure(
    tmp_path, monkeypatch
):
    target = tmp_path / "existing_candidate.csv"
    target.write_bytes(b"previous valid content")

    def simulate_replace_failure(source, destination):
        raise OSError("Simulated replacement failure")

    monkeypatch.setattr(
        candidate.os,
        "replace",
        simulate_replace_failure,
    )

    with pytest.raises(
        OSError, match="Simulated replacement failure"
    ):
        candidate.atomic_write(
            target, b"new candidate content"
        )

    assert target.read_bytes() == b"previous valid content"

    assert not list(
        tmp_path.glob("existing_candidate.csv.*.tmp")
    )
