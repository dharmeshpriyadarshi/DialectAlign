
"""Targeted remediation of non-approved Rural Women Bhojpuri redactions."""

import tkinter as tk

from collections import Counter
from tkinter import messagebox, ttk

from scripts.redact_rural_women_privacy import (
    RedactionApp,
    hash_text,
)

from scripts.validate_rural_women_privacy import (
    prepare_validation_records,
    load_validations,
    save_validations,
    is_current,
)


REMEDIATION_DECISIONS = {
    "REDACTION_INCOMPLETE",
    "OVER_REDACTED",
    "UNCERTAIN",
}


class RemediationApp(RedactionApp):

    def __init__(self, root):

        validation_records = prepare_validation_records()

        self.validations = load_validations()

        self.remediation_targets = {}

        for record in validation_records:

            record_id = record["record_id"]

            previous = self.validations.get(
                record_id
            )

            if not is_current(record, previous):
                continue

            if previous["decision"] in REMEDIATION_DECISIONS:

                self.remediation_targets[record_id] = {
                    "decision": previous["decision"],
                    "redacted_sha256":
                        record["redacted_sha256"],
                }

        self.session_excluded = 0

        super().__init__(root)

    def is_completed(self, record):

        record_id = record["record_id"]

        target = self.remediation_targets.get(
            record_id
        )

        if target is None:
            return True

        validation = self.validations.get(
            record_id
        )

        redaction = self.redactions.get(
            record_id
        )

        if redaction is None:
            return False

        if (
            validation
            and validation["decision"] == "EXCLUDE"
            and validation["original_sha256"]
            == redaction["original_sha256"]
            and validation["redacted_sha256"]
            == redaction["redacted_sha256"]
        ):
            return True

        return (
            redaction["redacted_sha256"]
            != target["redacted_sha256"]
        )

    def build_interface(self):

        self.targets = list(self.queue)

        self.root.title(
            "DialectAlign - Targeted Privacy Remediation"
        )

        self.root.geometry("1250x740")
        self.root.minsize(950, 600)

        toolbar = tk.Frame(
            self.root,
            bg=self.BG,
            padx=20,
            pady=8,
        )

        toolbar.pack(fill="x")

        tk.Button(
            toolbar,
            text="View previous redaction",
            command=self.show_previous_redaction,
            padx=12,
            pady=5,
        ).pack(
            side="left",
            padx=4,
        )

        tk.Button(
            toolbar,
            text="Exclude record",
            command=self.exclude_record,
            bg="#991B1B",
            fg="white",
            padx=12,
            pady=5,
        ).pack(
            side="right",
            padx=4,
        )

        super().build_interface()

    def display_record(self):

        if self.finished:
            return

        if self.position >= len(self.queue):

            self.finish()
            return

        super().display_record()

        record = self.queue[self.position]

        record_id = record["record_id"]

        previous = self.remediation_targets[
            record_id
        ]

        self.progress_label.configure(
            text=(
                f"Remediated: "
                f"{self.completed_count()}/{len(self.targets)}"
                f"    |    Queue: "
                f"{self.position + 1}/{len(self.queue)}"
            )
        )

        self.metadata_label.configure(
            text=(
                f"Record ID: {record_id}"
                f"    |    Previous decision: "
                f"{previous['decision']}"
            )
        )

        self.status_label.configure(
            text=(
                "Reconstruct the redaction from the "
                "original transcript. "
                "Use View previous redaction for reference."
            )
        )

    def show_previous_redaction(self):

        if self.finished:
            return

        record = self.queue[self.position]

        previous = self.redactions[
            record["record_id"]
        ]

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Previous redaction - Reference"
        )

        window.geometry("900x450")
        window.configure(bg=self.BG)

        window.transient(self.root)

        container = tk.Frame(
            window,
            bg=self.BG,
            padx=15,
            pady=15,
        )

        container.pack(
            fill="both",
            expand=True,
        )

        self.label(
            container,
            "PREVIOUS REDACTED TRANSCRIPT",
            14,
        ).pack(
            fill="x",
            pady=8,
        )

        scrollbar = ttk.Scrollbar(
            container
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        text_widget = tk.Text(
            container,
            font=self.transcript_font,
            wrap="word",
            bg=self.PANEL,
            fg=self.FG,
            padx=12,
            pady=12,
            height=6,
            yscrollcommand=scrollbar.set,
        )

        text_widget.pack(
            fill="both",
            expand=True,
        )

        scrollbar.configure(
            command=text_widget.yview
        )

        text_widget.insert(
            "1.0",
            previous["redacted_text"],
        )

        text_widget.configure(
            state="disabled"
        )

        window.grab_set()

    def save_and_next(self):

        if self.finished:
            return

        record = self.queue[self.position]

        record_id = record["record_id"]

        previous_hash = self.redactions[
            record_id
        ]["redacted_sha256"]

        current_hash = hash_text(
            self.current_text()
        )

        if current_hash == previous_hash:

            messagebox.showwarning(
                "No correction detected",
                "The reconstructed redaction is identical "
                "to the previous version.\n\n"
                "Make the required correction, skip the "
                "record, or exclude it if the privacy "
                "risk cannot be resolved.",
            )

            return

        super().save_and_next()

    def exclude_record(self):

        if self.finished:
            return

        record = self.queue[self.position]

        record_id = record["record_id"]

        redaction = self.redactions[
            record_id
        ]

        confirmed = messagebox.askyesno(
            "Confirm exclusion",
            "Exclude this transcript from subsequent "
            "corpus preparation?\n\n"
            "Any unsaved replacements will be discarded. "
            "The original corpus and existing redaction "
            "will remain unchanged.",
        )

        if not confirmed:
            return

        updated = self.validations.copy()

        updated[record_id] = {
            "record_id": record_id,
            "original_sha256":
                redaction["original_sha256"],
            "redacted_sha256":
                redaction["redacted_sha256"],
            "decision": "EXCLUDE",
        }

        try:

            save_validations(updated)

        except Exception:

            messagebox.showerror(
                "Save failed",
                "The exclusion decision could not be saved.",
            )

            return

        self.validations = updated

        self.session_excluded += 1
        self.position += 1

        self.display_record()

    def finish(self):

        if self.finished:
            return

        if (
            self.position < len(self.queue)
            and self.replacement_count
        ):

            confirmed = messagebox.askyesno(
                "Exit remediation",
                "Discard unsaved replacements and exit?",
            )

            if not confirmed:
                return

        self.finished = True

        counts = Counter()

        for record in self.targets:

            record_id = record["record_id"]

            validation = self.validations.get(
                record_id
            )

            redaction = self.redactions[
                record_id
            ]

            if (
                validation
                and validation["decision"] == "EXCLUDE"
                and validation["original_sha256"]
                == redaction["original_sha256"]
                and validation["redacted_sha256"]
                == redaction["redacted_sha256"]
            ):

                counts["EXCLUDED"] += 1

            elif (
                redaction["redacted_sha256"]
                != self.remediation_targets[
                    record_id
                ]["redacted_sha256"]
            ):

                counts["CORRECTED"] += 1

            else:

                counts["PENDING"] += 1

        summary = "\n".join([
            f"Total remediation targets: {len(self.targets)}",
            f"Corrected records: {counts['CORRECTED']}",
            f"Excluded records: {counts['EXCLUDED']}",
            f"Pending remediation: {counts['PENDING']}",
            "",
            f"Session corrected: {self.session_completed}",
            f"Session excluded: {self.session_excluded}",
            f"Records skipped: {self.skipped}",
            "",
            "Corrected records require fresh validation.",
            "Original corpus remains unchanged.",
            "Source status: QUARANTINED",
        ])

        print("\n" + "=" * 70)
        print("TARGETED PRIVACY REMEDIATION SUMMARY")
        print("=" * 70)
        print(summary)

        messagebox.showinfo(
            "Remediation Summary",
            summary,
        )

        self.root.destroy()


def main():

    records = prepare_validation_records()
    validations = load_validations()

    pending = [
        record
        for record in records
        if is_current(
            record,
            validations.get(record["record_id"]),
        )
        and validations[
            record["record_id"]
        ]["decision"] in REMEDIATION_DECISIONS
    ]

    if not pending:

        print("No current remediation targets.")
        print("Run post-redaction validation next.")
        return

    root = tk.Tk()

    try:

        RemediationApp(root)

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
