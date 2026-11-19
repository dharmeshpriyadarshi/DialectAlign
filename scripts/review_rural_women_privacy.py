
import argparse
import csv
import hashlib
import os
from collections import Counter
from pathlib import Path

from scripts.audit_rural_women_privacy import (
    PATTERNS,
    load_records,
    screen_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REVIEW_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "privacy"
    / "rural_women_review.csv"
)

DECISIONS = {
    "1": "CLEAR",
    "2": "REDACTION_REQUIRED",
    "3": "EXCLUDE",
    "4": "UNCERTAIN",
}

FIELDNAMES = [
    "record_id",
    "text_sha256",
    "priority",
    "flags",
    "decision",
]

IDENTIFIER_FLAGS = set(PATTERNS) | {
    "possible_spoken_numeric_identifier"
}


def hash_text(text):
    """Generate a fingerprint for the original transcript."""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def determine_priority(flags):
    """Assign manual review priority."""

    if flags.intersection(IDENTIFIER_FLAGS):
        return 1

    if flags:
        return 2

    return 3


def prepare_records():
    """Prepare and prioritize records for manual review."""

    df = load_records()

    if df["id"].isna().any():
        raise ValueError("Missing record IDs detected.")

    if df["id"].duplicated().any():
        raise ValueError("Duplicate record IDs detected.")

    records = []

    for _, row in df.iterrows():

        text = row["text"]

        if not isinstance(text, str):
            raise ValueError("Invalid transcript detected.")

        flags = screen_record(text)

        records.append({
            "record_id": str(row["id"]),
            "text": text,
            "text_sha256": hash_text(text),
            "flags": flags,
            "priority": determine_priority(flags),
        })

    return sorted(
        records,
        key=lambda record: (
            record["priority"],
            record["record_id"],
        ),
    )


def load_previous_reviews():
    """Load previously saved review decisions."""

    if not REVIEW_PATH.exists():
        return {}

    reviews = {}

    with REVIEW_PATH.open(
        "r", encoding="utf-8", newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDNAMES:
            raise ValueError("Invalid review file schema.")

        for row in reader:

            if row["decision"] not in DECISIONS.values():
                raise ValueError("Invalid saved decision.")

            record_id = row["record_id"]

            if record_id in reviews:
                raise ValueError(
                    f"Duplicate review entry: {record_id}"
                )

            reviews[record_id] = row

    return reviews


def save_reviews(reviews):
    """Atomically persist all review decisions."""

    REVIEW_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = REVIEW_PATH.with_suffix(".tmp")

    with temp_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()

        for review in reviews.values():
            writer.writerow(review)

        file.flush()
        os.fsync(file.fileno())

    temp_path.replace(REVIEW_PATH)


def save_decision(record, decision, saved_reviews):
    """Insert or update a decision without duplicate rows."""

    updated_reviews = saved_reviews.copy()

    updated_reviews[record["record_id"]] = {
        "record_id": record["record_id"],
        "text_sha256": record["text_sha256"],
        "priority": record["priority"],
        "flags": "|".join(sorted(record["flags"])),
        "decision": decision,
    }

    save_reviews(updated_reviews)

    saved_reviews.update(updated_reviews)


def get_decision(recheck=False):
    """Collect a valid manual review decision."""

    print("\n--- REVIEW OPTIONS ---")
    print("1. CLEAR")
    print("2. REDACTION_REQUIRED")
    print("3. EXCLUDE")
    print("4. UNCERTAIN")

    if recheck:
        print("K. Keep previous decision")

    print("S. Skip for now")
    print("Q. Save progress and quit")

    while True:

        choice = input("\nDecision: ").strip().upper()

        if choice in DECISIONS:
            return DECISIONS[choice]

        if recheck and choice == "K":
            return choice

        if choice in {"S", "Q"}:
            return choice

        print("Invalid option. Please try again.")


def print_summary(records, reviews):
    """Display aggregate review progress."""

    counts = Counter(
        review["decision"]
        for review in reviews.values()
    )

    print("\n" + "=" * 70)
    print("MANUAL PRIVACY REVIEW SUMMARY")
    print("=" * 70)

    print(f"Total records: {len(records)}")
    print(f"Reviewed records: {len(reviews)}")
    print(f"Pending records: {len(records) - len(reviews)}")

    for decision in DECISIONS.values():
        print(f"{decision}: {counts[decision]}")

    print(f"\nReview file: {REVIEW_PATH}")
    print("Original corpus remains unchanged.")
    print("Source status: QUARANTINED")


def main():

    parser = argparse.ArgumentParser(
        description="Manual rural Bhojpuri privacy review."
    )

    parser.add_argument(
        "--recheck",
        action="store_true",
        help="Revalidate records marked REDACTION_REQUIRED.",
    )

    args = parser.parse_args()

    records = prepare_records()
    saved_reviews = load_previous_reviews()

    reviews = {
        record["record_id"]: saved_reviews[record["record_id"]]
        for record in records
        if record["record_id"] in saved_reviews
        and saved_reviews[record["record_id"]]["text_sha256"]
        == record["text_sha256"]
    }

    priority_counts = Counter(
        record["priority"]
        for record in records
    )

    if args.recheck:

        queue = [
            record
            for record in records
            if record["record_id"] in reviews
            and reviews[record["record_id"]]["decision"]
            == "REDACTION_REQUIRED"
        ]

    else:

        queue = [
            record
            for record in records
            if record["record_id"] not in reviews
        ]

    changed_decisions = 0
    rechecked_records = 0
    skipped_records = 0

    print("=" * 70)
    print("DIALECTALIGN - MANUAL PRIVACY REVIEW")
    print("=" * 70)

    mode = "REVALIDATION" if args.recheck else "STANDARD"

    print(f"Review mode: {mode}")
    print(f"Total records: {len(records)}")
    print(f"Previously reviewed: {len(reviews)}")
    print(f"Records in current queue: {len(queue)}")

    print("\n--- REVIEW QUEUE ---")
    print(f"Priority 1: {priority_counts[1]}")
    print(f"Priority 2: {priority_counts[2]}")
    print(f"Priority 3: {priority_counts[3]}")

    print("\nReview transcripts privately.")
    print("Do not copy sensitive information.")
    print("Decisions are saved individually.")

    try:

        for position, record in enumerate(queue, start=1):

            record_id = record["record_id"]
            previous_review = reviews.get(record_id)

            previous_decision = (
                previous_review["decision"]
                if previous_review else None
            )

            print("\n" + "=" * 70)

            print(
                f"Review progress: "
                f"{len(reviews)}/{len(records)}"
            )

            print(
                f"Queue position: {position}/{len(queue)}"
            )

            print(f"Record ID: {record_id}")
            print(f"Priority: {record['priority']}")

            flags = ", ".join(sorted(record["flags"]))

            print(f"Flags: {flags or 'None detected'}")

            if previous_decision:

                print(
                    f"Previous decision: {previous_decision}"
                )

            print("\n--- LOCAL TRANSCRIPT ---")
            print(record["text"])

            decision = get_decision(
                recheck=args.recheck
            )

            if decision == "Q":
                break

            if decision == "S":
                skipped_records += 1
                continue

            if decision == "K":

                rechecked_records += 1

                print("Previous decision retained.")

                continue

            save_decision(
                record,
                decision,
                saved_reviews,
            )

            reviews[record_id] = saved_reviews[record_id]

            if args.recheck:

                rechecked_records += 1

                if decision != previous_decision:
                    changed_decisions += 1

            print("Decision saved.")

    except (KeyboardInterrupt, EOFError):

        print("\nReview interrupted. Saved progress retained.")

    if args.recheck:

        print("\n--- REVALIDATION RESULTS ---")
        print(f"Records revalidated: {rechecked_records}")
        print(f"Decisions changed: {changed_decisions}")
        print(f"Records skipped: {skipped_records}")

    print_summary(records, reviews)


if __name__ == "__main__":
    main()
