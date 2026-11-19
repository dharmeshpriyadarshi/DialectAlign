
import csv
import hashlib
import os
import tkinter as tk

from collections import Counter
from pathlib import Path
from tkinter import ttk, messagebox
from tkinter import font as tkfont

from scripts.review_rural_women_privacy import (
    prepare_records,
    load_previous_reviews,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "privacy"
    / "rural_women_redactions.csv"
)

PLACEHOLDERS = {
    "Account number": "[ACCOUNT_REDACTED]",
    "Card number": "[CARD_REDACTED]",
    "Aadhaar number": "[AADHAAR_REDACTED]",
    "Phone number": "[PHONE_REDACTED]",
    "Personal name": "[NAME_REDACTED]",
    "Residential address": "[ADDRESS_REDACTED]",
    "UPI identifier": "[UPI_REDACTED]",
    "Email address": "[EMAIL_REDACTED]",
    "Other identifier": "[ID_REDACTED]",
    "Sensitive details": "[DETAILS_REDACTED]",
}

FIELDNAMES = [
    "record_id",
    "original_sha256",
    "redacted_text",
    "redacted_sha256",
    "replacement_count",
    "status",
]


def hash_text(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def load_redactions():

    if not OUTPUT_PATH.exists():
        return {}

    results = {}

    with OUTPUT_PATH.open(
        "r", encoding="utf-8", newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDNAMES:
            raise ValueError(
                "Invalid redaction file schema."
            )

        for row in reader:

            record_id = row["record_id"]

            if record_id in results:
                raise ValueError(
                    f"Duplicate redaction: {record_id}"
                )

            if hash_text(row["redacted_text"]) != (
                row["redacted_sha256"]
            ):
                raise ValueError(
                    f"Redaction integrity error: {record_id}"
                )

            results[record_id] = row

    return results


def save_redactions(results):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = OUTPUT_PATH.with_suffix(".tmp")

    with temp_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()
        writer.writerows(results.values())

        file.flush()
        os.fsync(file.fileno())

    temp_path.replace(OUTPUT_PATH)


class RedactionApp:

    BG = "#1E1E1E"
    PANEL = "#252526"
    FG = "#E5E7EB"

    def __init__(self, root):

        self.root = root

        self.records = prepare_records()
        self.reviews = load_previous_reviews()
        self.redactions = load_redactions()

        self.validate_reviews()

        self.targets = [
            record
            for record in self.records
            if self.reviews[
                record["record_id"]
            ]["decision"] == "REDACTION_REQUIRED"
        ]

        self.queue = [
            record
            for record in self.targets
            if not self.is_completed(record)
        ]

        self.position = 0
        self.session_completed = 0
        self.skipped = 0

        self.history = []
        self.replacement_count = 0

        self.font_size = 26
        self.finished = False

        root.title(
            "DialectAlign - Targeted Privacy Redaction"
        )

        root.geometry("1250x850")
        root.minsize(900, 700)
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
        self.display_record()

    def validate_reviews(self):

        record_ids = {
            record["record_id"]
            for record in self.records
        }

        if set(self.reviews) != record_ids:

            raise ValueError(
                "Manual review coverage is incomplete "
                "or contains unknown records."
            )

        for record in self.records:

            review = self.reviews[
                record["record_id"]
            ]

            if review["text_sha256"] != (
                record["text_sha256"]
            ):

                raise ValueError(
                    "Original transcript has changed: "
                    f"{record['record_id']}"
                )

    def is_completed(self, record):

        result = self.redactions.get(
            record["record_id"]
        )

        return (
            result is not None
            and result["original_sha256"]
            == record["text_sha256"]
            and result["status"]
            == "REDACTED_PENDING_VALIDATION"
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
            "DialectAlign - Targeted Privacy Redaction",
            22,
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
            maximum=max(len(self.targets), 1),
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
        ).pack(side="right", padx=3)

        tk.Button(
            header,
            text="A-",
            command=lambda: self.change_font(-2),
        ).pack(side="right", padx=3)

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
            "REDACTED TRANSCRIPT - SELECT TEXT HERE",
        ).grid(
            row=0,
            column=1,
            sticky="w",
        )

        self.original = self.create_text_panel(
            panels, 0
        )

        self.redacted = self.create_text_panel(
            panels, 1
        )

        self.label(
            container,
            "Select sensitive text in the right panel,"
            " then click its replacement category.",
        ).pack(fill="x", pady=5)

        buttons = tk.Frame(
            container,
            bg=self.BG,
        )

        buttons.pack(fill="x")

        for column in range(5):

            buttons.columnconfigure(
                column,
                weight=1,
            )

        for index, (name, placeholder) in enumerate(
            PLACEHOLDERS.items()
        ):

            tk.Button(
                buttons,
                text=name,
                command=lambda p=placeholder:
                    self.replace_selection(p),
                font=("Segoe UI", 11),
                bg="#374151",
                fg="white",
                activebackground="#4B5563",
                activeforeground="white",
                pady=8,
            ).grid(
                row=index // 5,
                column=index % 5,
                sticky="ew",
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
            text="Undo",
            command=self.undo,
            padx=10,
        ).pack(side="left", padx=4)

        tk.Button(
            actions,
            text="Reset transcript",
            command=self.reset,
            padx=10,
        ).pack(side="left", padx=4)

        tk.Button(
            actions,
            text="Skip",
            command=self.skip,
            padx=10,
        ).pack(side="left", padx=4)

        tk.Button(
            actions,
            text="Save and next",
            command=self.save_and_next,
            bg="#166534",
            fg="white",
            padx=18,
            pady=8,
        ).pack(side="right", padx=4)

        tk.Button(
            actions,
            text="Exit",
            command=self.finish,
            padx=10,
        ).pack(side="right", padx=4)

        self.status_label = self.label(
            container,
            size=10,
        )

        self.status_label.pack(fill="x")

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
            font=self.transcript_font,
            wrap="word",
            bg=self.PANEL,
            fg=self.FG,
            selectbackground="#92400E",
            selectforeground="white",
            exportselection=False,
            padx=12,
            pady=12,
            height=6,
            relief="flat",
            state="disabled",
            yscrollcommand=scrollbar.set,
        )

        widget.pack(
            fill="both",
            expand=True,
        )

        scrollbar.configure(
            command=widget.yview
        )

        return widget

    def set_text(self, widget, text):

        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")
        widget.yview_moveto(0)

    def current_text(self):

        return self.redacted.get(
            "1.0",
            "end-1c",
        )

    def change_font(self, adjustment):

        self.font_size = max(
            16,
            min(54, self.font_size + adjustment),
        )

        self.transcript_font.configure(
            size=self.font_size
        )

    def completed_count(self):

        return sum(
            self.is_completed(record)
            for record in self.targets
        )

    def display_record(self):

        completed = self.completed_count()

        self.progress_bar["value"] = completed

        if self.position >= len(self.queue):

            self.finish()
            return

        record = self.queue[self.position]

        self.history = []
        self.replacement_count = 0

        self.progress_label.configure(
            text=(
                f"Redacted: {completed}/{len(self.targets)}"
                f"    |    Queue: "
                f"{self.position + 1}/{len(self.queue)}"
            )
        )

        self.metadata_label.configure(
            text=f"Record ID: {record['record_id']}"
        )

        self.set_text(
            self.original,
            record["text"],
        )

        self.set_text(
            self.redacted,
            record["text"],
        )

        self.status_label.configure(
            text="Replacements: 0"
        )

    def replace_selection(self, placeholder):

        if self.finished:
            return

        try:

            start = self.redacted.index("sel.first")
            end = self.redacted.index("sel.last")

        except tk.TclError:

            messagebox.showwarning(
                "No selection",
                "Select sensitive text in the "
                "right transcript panel first.",
            )

            return

        selected = self.redacted.get(start, end)

        if not selected.strip():
            return

        if "[" in selected or "]" in selected:

            messagebox.showwarning(
                "Invalid selection",
                "Do not select existing placeholders.",
            )

            return

        self.history.append(
            (
                self.current_text(),
                self.replacement_count,
            )
        )

        self.redacted.configure(
            state="normal"
        )

        self.redacted.delete(start, end)
        self.redacted.insert(start, placeholder)

        self.redacted.configure(
            state="disabled"
        )

        self.replacement_count += 1

        self.status_label.configure(
            text=(
                f"Replacements: {self.replacement_count}"
            )
        )

    def undo(self):

        if not self.history:
            return

        text, count = self.history.pop()

        self.set_text(
            self.redacted,
            text,
        )

        self.replacement_count = count

        self.status_label.configure(
            text=f"Replacements: {count}"
        )

    def reset(self):

        if self.finished:
            return

        record = self.queue[self.position]

        self.set_text(
            self.redacted,
            record["text"],
        )

        self.history = []
        self.replacement_count = 0

        self.status_label.configure(
            text="Transcript reset."
        )

    def save_and_next(self):

        if self.finished:
            return

        record = self.queue[self.position]
        text = self.current_text()

        if (
            self.replacement_count == 0
            or text == record["text"]
            or not text.strip()
        ):

            messagebox.showwarning(
                "Redaction required",
                "Apply at least one valid replacement "
                "before saving.",
            )

            return

        confirmed = messagebox.askyesno(
            "Confirm redaction",
            "Have you checked the entire redacted "
            "transcript for remaining sensitive "
            "information?",
        )

        if not confirmed:
            return

        updated = self.redactions.copy()

        updated[record["record_id"]] = {
            "record_id": record["record_id"],
            "original_sha256": record["text_sha256"],
            "redacted_text": text,
            "redacted_sha256": hash_text(text),
            "replacement_count": self.replacement_count,
            "status": "REDACTED_PENDING_VALIDATION",
        }

        try:

            save_redactions(updated)

        except Exception:

            messagebox.showerror(
                "Save failed",
                "The redaction could not be saved. "
                "The current transcript has been retained.",
            )

            return

        self.redactions = updated
        self.session_completed += 1
        self.position += 1

        self.display_record()

    def skip(self):

        if self.finished:
            return

        if self.replacement_count:

            confirmed = messagebox.askyesno(
                "Discard unsaved replacements?",
                "The current replacements have not "
                "been saved. Skip this record?",
            )

            if not confirmed:
                return

        self.skipped += 1
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
                "Exit redaction",
                "Discard unsaved replacements for "
                "the current transcript and exit?",
            )

            if not confirmed:
                return

        self.finished = True

        completed = self.completed_count()

        summary = "\n".join([
            f"Total redaction targets: {len(self.targets)}",
            f"Completed redactions: {completed}",
            f"Pending redactions: {len(self.targets) - completed}",
            "",
            f"Session completed: {self.session_completed}",
            f"Records skipped: {self.skipped}",
            "",
            "Original corpus remains unchanged.",
            "Post-redaction validation: PENDING",
            "Source status: QUARANTINED",
        ])

        print("\n" + "=" * 70)
        print("TARGETED PRIVACY REDACTION SUMMARY")
        print("=" * 70)
        print(summary)

        messagebox.showinfo(
            "Redaction Summary",
            summary,
        )

        self.root.destroy()


def main():

    root = tk.Tk()

    try:

        RedactionApp(root)

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
