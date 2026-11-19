
"""Manual post-redaction privacy validation for Rural Women Bhojpuri."""

import csv
import os
import tkinter as tk

from collections import Counter
from tkinter import ttk, messagebox
from tkinter import font as tkfont

from scripts.review_rural_women_privacy import (
    prepare_records,
    load_previous_reviews,
)

from scripts.redact_rural_women_privacy import (
    OUTPUT_PATH,
    PLACEHOLDERS,
    hash_text,
    load_redactions,
)


VALIDATION_PATH = (
    OUTPUT_PATH.parent
    / "rural_women_validation.csv"
)

DECISIONS = {
    "APPROVED": "#166534",
    "REDACTION_INCOMPLETE": "#92400E",
    "OVER_REDACTED": "#854D0E",
    "EXCLUDE": "#991B1B",
    "UNCERTAIN": "#374151",
}

FIELDNAMES = [
    "record_id",
    "original_sha256",
    "redacted_sha256",
    "decision",
]


def prepare_validation_records():

    originals = prepare_records()
    reviews = load_previous_reviews()
    redactions = load_redactions()

    original_ids = {
        record["record_id"]
        for record in originals
    }

    if len(original_ids) != len(originals):
        raise ValueError(
            "Duplicate original record IDs."
        )

    if original_ids != set(reviews):
        raise ValueError(
            "Original review coverage mismatch."
        )

    for record in originals:

        record_id = record["record_id"]

        if hash_text(record["text"]) != (
            reviews[record_id]["text_sha256"]
        ):
            raise ValueError(
                "Original review fingerprint mismatch."
            )

    target_ids = {
        record_id
        for record_id, review in reviews.items()
        if review["decision"] == "REDACTION_REQUIRED"
    }

    if target_ids != set(redactions):
        raise ValueError(
            "Redaction target coverage mismatch."
        )

    records = []

    for original in originals:

        record_id = original["record_id"]

        if record_id not in target_ids:
            continue

        redaction = redactions[record_id]

        original_hash = hash_text(
            original["text"]
        )

        redacted_hash = hash_text(
            redaction["redacted_text"]
        )

        if original_hash != redaction["original_sha256"]:
            raise ValueError(
                "Original fingerprint mismatch."
            )

        if redacted_hash != redaction["redacted_sha256"]:
            raise ValueError(
                "Redacted fingerprint mismatch."
            )

        if original_hash == redacted_hash:
            raise ValueError(
                "Redacted transcript is unchanged."
            )

        if not any(
            placeholder in redaction["redacted_text"]
            for placeholder in PLACEHOLDERS.values()
        ):
            raise ValueError(
                "Approved redaction placeholder missing."
            )

        records.append({
            "record_id": record_id,
            "original_text": original["text"],
            "redacted_text": redaction["redacted_text"],
            "original_sha256": original_hash,
            "redacted_sha256": redacted_hash,
        })

    return records


def load_validations():

    if not VALIDATION_PATH.exists():
        return {}

    results = {}

    with VALIDATION_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDNAMES:
            raise ValueError(
                "Invalid validation file schema."
            )

        for row in reader:

            record_id = row["record_id"]

            if record_id in results:
                raise ValueError(
                    "Duplicate validation record."
                )

            if any(
                not row.get(field)
                for field in FIELDNAMES
            ):
                raise ValueError(
                    "Missing validation field."
                )

            if row["decision"] not in DECISIONS:
                raise ValueError(
                    "Unknown validation decision."
                )

            results[record_id] = row

    return results


def save_validations(results):

    VALIDATION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = VALIDATION_PATH.with_suffix(
        ".tmp"
    )

    with temp_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()
        writer.writerows(results.values())

        file.flush()
        os.fsync(file.fileno())

    temp_path.replace(VALIDATION_PATH)


def is_current(record, saved):

    if saved is None:
        return False

    return (
        saved["original_sha256"]
        == record["original_sha256"]
        and saved["redacted_sha256"]
        == record["redacted_sha256"]
    )


class ValidationApp:

    BG = "#1E1E1E"
    PANEL = "#252526"
    FG = "#E5E7EB"

    def __init__(self, root):

        self.root = root

        self.records = prepare_validation_records()
        self.validations = load_validations()

        self.queue = [
            record
            for record in self.records
            if not is_current(
                record,
                self.validations.get(
                    record["record_id"]
                ),
            )
        ]

        self.position = 0
        self.session_validated = 0
        self.skipped = 0
        self.finished = False
        self.font_size = 26

        root.title(
            "DialectAlign - Post-Redaction Privacy Validation"
        )

        root.geometry("1250x740")
        root.minsize(950, 600)
        root.configure(bg=self.BG)

        root.protocol(
            "WM_DELETE_WINDOW",
            self.finish,
        )

        available_fonts = set(
            tkfont.families(root)
        )

        family = next(
            (
                name
                for name in [
                    "Nirmala UI",
                    "Mangal",
                    "Arial Unicode MS",
                ]
                if name in available_fonts
            ),
            "Segoe UI",
        )

        self.transcript_font = tkfont.Font(
            family=family,
            size=self.font_size,
        )

        self.build_interface()

        root.after(
            0,
            self.display_record,
        )

    def label(self, parent, text="", size=12):

        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size),
            bg=self.BG,
            fg=self.FG,
            anchor="w",
        )

    def build_interface(self):

        container = tk.Frame(
            self.root,
            bg=self.BG,
            padx=20,
            pady=15,
        )

        container.pack(
            fill="both",
            expand=True,
        )

        self.label(
            container,
            "DialectAlign - Post-Redaction Privacy Validation",
            21,
        ).pack(fill="x")

        self.progress_label = self.label(
            container
        )

        self.progress_label.pack(
            fill="x",
            pady=8,
        )

        self.progress_bar = ttk.Progressbar(
            container,
            maximum=max(
                len(self.records),
                1,
            ),
        )

        self.progress_bar.pack(
            fill="x",
            pady=(0, 10),
        )

        header = tk.Frame(
            container,
            bg=self.BG,
        )

        header.pack(fill="x")

        self.metadata_label = self.label(
            header,
            size=11,
        )

        self.metadata_label.pack(
            side="left"
        )

        tk.Button(
            header,
            text="A+",
            command=lambda: self.change_font(2),
        ).pack(
            side="right",
            padx=3,
        )

        tk.Button(
            header,
            text="A-",
            command=lambda: self.change_font(-2),
        ).pack(
            side="right",
            padx=3,
        )

        panels = tk.Frame(
            container,
            bg=self.BG,
        )

        panels.pack(
            fill="both",
            expand=True,
            pady=10,
        )

        panels.columnconfigure(0, weight=1)
        panels.columnconfigure(1, weight=1)
        panels.rowconfigure(1, weight=1)

        self.label(
            panels,
            "ORIGINAL TRANSCRIPT",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.label(
            panels,
            "REDACTED TRANSCRIPT",
        ).grid(
            row=0,
            column=1,
            sticky="w",
        )

        self.original = self.create_text_panel(
            panels,
            0,
        )

        self.redacted = self.create_text_panel(
            panels,
            1,
        )

        instructions = (
            "Check for remaining identifiers, "
            "correct placeholder categories, "
            "and preservation of linguistic meaning."
        )

        self.label(
            container,
            instructions,
            11,
        ).pack(
            fill="x",
            pady=8,
        )

        buttons = tk.Frame(
            container,
            bg=self.BG,
        )

        buttons.pack(fill="x")

        for index, (decision, color) in enumerate(
            DECISIONS.items()
        ):

            buttons.columnconfigure(
                index,
                weight=1,
            )

            tk.Button(
                buttons,
                text=(
                    f"{index + 1} - "
                    f"{decision}"
                ),
                command=lambda d=decision:
                    self.save_decision(d),
                font=("Segoe UI", 10),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                wraplength=190,
                pady=12,
            ).grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=3,
                pady=3,
            )

        actions = tk.Frame(
            container,
            bg=self.BG,
        )

        actions.pack(
            fill="x",
            pady=10,
        )

        tk.Button(
            actions,
            text="Skip",
            command=self.skip,
            padx=15,
        ).pack(
            side="left",
            padx=4,
        )

        tk.Button(
            actions,
            text="Exit",
            command=self.finish,
            padx=15,
        ).pack(
            side="right",
            padx=4,
        )

        self.status_label = self.label(
            container,
            size=10,
        )

        self.status_label.pack(fill="x")

        for index, decision in enumerate(
            DECISIONS,
            start=1,
        ):

            self.root.bind(
                str(index),
                lambda event, d=decision:
                    self.save_decision(d),
            )

    def create_text_panel(self, parent, column):

        frame = tk.Frame(
            parent,
            bg=self.PANEL,
        )

        frame.grid(
            row=1,
            column=column,
            sticky="nsew",
            padx=5,
            pady=5,
        )

        scrollbar = ttk.Scrollbar(frame)

        scrollbar.pack(
            side="right",
            fill="y",
        )

        widget = tk.Text(
            frame,
            height=6,
            font=self.transcript_font,
            wrap="word",
            bg=self.PANEL,
            fg=self.FG,
            padx=12,
            pady=12,
            relief="flat",
            state="disabled",
            exportselection=False,
            yscrollcommand=scrollbar.set,
        )

        widget.pack(
            fill="both",
            expand=True,
        )

        scrollbar.configure(
            command=widget.yview
        )

        widget.tag_configure(
            "placeholder",
            foreground="#86EFAC",
            background="#14532D",
        )

        return widget

    def set_text(
        self,
        widget,
        text,
        highlight=False,
    ):

        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

        if highlight:

            for placeholder in PLACEHOLDERS.values():

                start = "1.0"

                while True:

                    position = widget.search(
                        placeholder,
                        start,
                        stopindex="end",
                        exact=True,
                    )

                    if not position:
                        break

                    end = widget.index(
                        f"{position}+"
                        f"{len(placeholder)}c"
                    )

                    widget.tag_add(
                        "placeholder",
                        position,
                        end,
                    )

                    start = end

        widget.configure(
            state="disabled"
        )

        widget.yview_moveto(0)

    def change_font(self, adjustment):

        self.font_size = max(
            16,
            min(
                54,
                self.font_size + adjustment,
            ),
        )

        self.transcript_font.configure(
            size=self.font_size
        )

    def current_validations(self):

        return {
            record["record_id"]:
                self.validations[record["record_id"]]

            for record in self.records

            if is_current(
                record,
                self.validations.get(
                    record["record_id"]
                ),
            )
        }

    def display_record(self):

        if self.finished:
            return

        completed = len(
            self.current_validations()
        )

        self.progress_bar["value"] = completed

        if self.position >= len(self.queue):

            self.finish()
            return

        record = self.queue[self.position]

        self.progress_label.configure(
            text=(
                f"Validated: "
                f"{completed}/{len(self.records)}"
                f"    |    Queue: "
                f"{self.position + 1}/{len(self.queue)}"
            )
        )

        self.metadata_label.configure(
            text=(
                f"Record ID: "
                f"{record['record_id']}"
            )
        )

        self.set_text(
            self.original,
            record["original_text"],
        )

        self.set_text(
            self.redacted,
            record["redacted_text"],
            highlight=True,
        )

        self.status_label.configure(
            text=(
                "Validation decision pending."
            )
        )

    def save_decision(self, decision):

        if self.finished:
            return

        record = self.queue[self.position]

        if decision == "APPROVED":

            confirmed = messagebox.askyesno(
                "Confirm privacy validation",
                "Have you checked the entire transcript "
                "for residual personal information, "
                "correct placeholder categories and "
                "unnecessary removal of linguistic content?",
            )

            if not confirmed:
                return

        updated = self.validations.copy()

        updated[record["record_id"]] = {
            "record_id": record["record_id"],
            "original_sha256":
                record["original_sha256"],
            "redacted_sha256":
                record["redacted_sha256"],
            "decision": decision,
        }

        try:

            save_validations(updated)

        except Exception:

            messagebox.showerror(
                "Save failed",
                "The validation decision "
                "could not be saved.",
            )

            return

        self.validations = updated
        self.session_validated += 1
        self.position += 1

        self.display_record()

    def skip(self):

        if self.finished:
            return

        self.skipped += 1
        self.position += 1

        self.display_record()

    def finish(self):

        if self.finished:
            return

        self.finished = True

        current = self.current_validations()

        counts = Counter(
            row["decision"]
            for row in current.values()
        )

        total = len(self.records)
        completed = len(current)
        pending = total - completed

        stale = sum(
            record["record_id"] in self.validations
            and record["record_id"] not in current
            for record in self.records
        )

        if pending:

            validation_status = "INCOMPLETE"

        elif counts["APPROVED"] == total and total:

            validation_status = (
                "ALL_REDACTIONS_APPROVED_BY_REVIEWER"
            )

        else:

            validation_status = (
                "FOLLOW_UP_REQUIRED"
            )

        summary = [
            f"Total validation targets: {total}",
            f"Validated records: {completed}",
            f"Pending validations: {pending}",
            f"Stale validations: {stale}",
            "",
            f"Session validated: {self.session_validated}",
            f"Records skipped: {self.skipped}",
            "",
        ]

        summary.extend(
            f"{decision}: {counts[decision]}"
            for decision in DECISIONS
        )

        summary.extend([
            "",
            f"Validation status: {validation_status}",
            "Original corpus remains unchanged.",
            "Redaction data remains unchanged.",
            "Source status: QUARANTINED",
        ])

        output = "\n".join(summary)

        print("\n" + "=" * 70)
        print("POST-REDACTION PRIVACY VALIDATION SUMMARY")
        print("=" * 70)
        print(output)

        messagebox.showinfo(
            "Validation Summary",
            output,
        )

        self.root.destroy()


def main():

    root = tk.Tk()

    try:

        ValidationApp(root)

    except Exception as error:

        messagebox.showerror(
            "Initialization failed",
            str(error),
        )

        root.destroy()
        raise

    root.mainloop()


if __name__ == "__main__":
    main()
