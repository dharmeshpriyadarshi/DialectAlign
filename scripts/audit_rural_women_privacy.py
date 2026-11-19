
import re
import unicodedata
from collections import Counter
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

PATTERNS = {
    "email_address": (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "mobile_number": (
        r"(?<!\d)(?:\+91[\s-]?)?"
        r"[6-9]\d{4}[\s-]?\d{5}(?!\d)"
    ),

    "aadhaar_like_number": (
        r"(?<!\d)[2-9]\d{3}[\s-]?"
        r"\d{4}[\s-]?\d{4}(?!\d)"
    ),

    "pan_like_identifier": (
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    ),

    "ifsc_code": (
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    ),

    "possible_long_numeric_identifier": (
        r"(?<!\d)\d{9,18}(?!\d)"
    ),
}

KEYWORD_GROUPS = {
    "identity_context": [
        "आधार",
        "पहचान पत्र",
        "पहिचान पत्र",
        "पैन कार्ड",
        "राशन कार्ड",
        "मतदाता पहचान",
        "जन्म तिथि",
        "जनम तारीख",
    ],

    "financial_context": [
        "बैंक",
        "खाता",
        "अकाउंट",
        "आईएफएससी",
        "एटीएम",
        "ओटीपी",
        "पासबुक",
        "यूपीआई",
        "पिन नंबर",
    ],

    "contact_context": [
        "मोबाइल नंबर",
        "फोन नंबर",
        "फोन नम्बर",
        "मोबाइल नम्बर",
        "ईमेल",
        "संपर्क नंबर",
    ],

    "personal_context": [
        "हमार नाम",
        "हमर नाम",
        "मेरा नाम",
        "हमार उमिर",
        "पति के नाम",
        "पिता के नाम",
        "बाबूजी के नाम",
    ],

    "address_context": [
        "हमार पता",
        "घर के पता",
        "मकान नंबर",
        "पिन कोड",
        "पोस्ट ऑफिस",
        "थाना",
        "पूरा पता",
    ],

    "health_context": [
        "बीमारी",
        "गर्भवती",
        "इलाज",
        "दवाई",
        "मरीज",
        "जांच रिपोर्ट",
        "अस्पताल",
    ],
}

NUMBER_WORDS = {
    "शून्य", "जीरो", "सून्य",
    "एक", "एगो",
    "दो", "दू", "दुइ",
    "तीन", "चार", "पांच", "पाँच",
    "छह", "छव", "सात",
    "आठ", "नौ", "दस",
}

IDENTIFIER_CONTEXT = [
    "नंबर",
    "नम्बर",
    "आधार",
    "खाता",
    "मोबाइल",
    "फोन",
    "ओटीपी",
    "पिन",
]

WORD_PATTERN = re.compile(
    r"[\u0900-\u097F]+"
)


def normalize_text(text):
    """Normalize Unicode and decimal digits for screening."""

    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFC", text)

    normalized_characters = []

    for character in text:

        if character.isdecimal():
            normalized_characters.append(
                str(unicodedata.decimal(character))
            )
        else:
            normalized_characters.append(character)

    return " ".join(
        "".join(normalized_characters).split()
    )


def load_records():
    """Load only the required local corpus partition."""

    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Corpus not found: {DATA_PATH}"
        )

    df = pd.read_parquet(
        DATA_PATH,
        columns=["id", "text", "source"],
    )

    return df[
        df["source"] == "rural_women"
    ].copy()


def detect_spoken_number_sequences(text):
    """Flag possible spoken identifiers using heuristics."""

    if not any(
        keyword in text
        for keyword in IDENTIFIER_CONTEXT
    ):
        return False

    words = WORD_PATTERN.findall(text)

    consecutive_numbers = 0

    for word in words:

        if word in NUMBER_WORDS:
            consecutive_numbers += 1

            if consecutive_numbers >= 4:
                return True

        else:
            consecutive_numbers = 0

    return False


def screen_record(text):
    """Return privacy indicators without exposing text."""

    text = normalize_text(text)

    flags = set()

    if not text:
        return flags

    for name, pattern in PATTERNS.items():

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            flags.add(name)

    for name, keywords in KEYWORD_GROUPS.items():

        if any(
            keyword in text
            for keyword in keywords
        ):
            flags.add(name)

    if detect_spoken_number_sequences(text):
        flags.add(
            "possible_spoken_numeric_identifier"
        )

    return flags


def main():
    """Execute aggregate privacy screening."""

    records = load_records()

    total_records = len(records)

    indicator_counts = Counter()

    records_with_flags = 0
    records_without_flags = 0
    records_with_numeric_flags = 0

    numeric_indicators = set(PATTERNS) | {
        "possible_spoken_numeric_identifier"
    }

    print("=" * 70)
    print("DIALECTALIGN - RURAL WOMEN PRIVACY AUDIT")
    print("=" * 70)

    print(f"Source: rural_women")
    print(f"Total records: {total_records:,}")

    for text in records["text"]:

        flags = screen_record(text)

        if flags:
            records_with_flags += 1
            indicator_counts.update(flags)

        else:
            records_without_flags += 1

        if flags.intersection(numeric_indicators):
            records_with_numeric_flags += 1

    all_indicators = (
        list(PATTERNS)
        + list(KEYWORD_GROUPS)
        + ["possible_spoken_numeric_identifier"]
    )

    print("\n--- PRIVACY INDICATOR DISTRIBUTION ---")

    for indicator in all_indicators:

        count = indicator_counts[indicator]

        percentage = (
            100 * count / total_records
            if total_records else 0
        )

        print(
            f"{indicator:<40}"
            f"{count:>5,} "
            f"({percentage:.2f}%)"
        )

    print("\n--- CONSOLIDATED RESULTS ---")

    print(
        f"Total records screened: "
        f"{total_records:,}"
    )

    print(
        f"Records with at least one indicator: "
        f"{records_with_flags:,}"
    )

    print(
        f"Records with no detected indicators: "
        f"{records_without_flags:,}"
    )

    print(
        f"Records with identifier-pattern indicators: "
        f"{records_with_numeric_flags:,}"
    )

    print("\n--- LIMITATIONS ---")

    print("Indicators are not confirmed PII.")
    print("Keyword matches may produce false positives.")
    print("Undetected PII may still exist.")
    print("Manual privacy review remains necessary.")

    print("\n--- DATA HANDLING ---")

    print("No transcript content printed.")
    print("No personal identifiers exported.")
    print("No records deleted or modified.")
    print("Original corpus remains unchanged.")
    print("Source status: QUARANTINED")

    print("\nPrivacy screening completed.")


if __name__ == "__main__":
    main()
