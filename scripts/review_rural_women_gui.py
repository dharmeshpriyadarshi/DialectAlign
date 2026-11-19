
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from collections import Counter

from scripts.review_rural_women_privacy import (
    DECISIONS,
    prepare_records,
    load_previous_reviews,
    save_decision,
)


class PrivacyReviewApp:

    BACKGROUND = "#1E1E1E"
    PANEL = "#252526"
    FOREGROUND = "#E5E7EB"
    SECONDARY = "#A1A1AA"

    def __init__(self, root, recheck=False):

        self.root = root
        self.recheck = recheck

        self.records = prepare_records()
        self.saved_reviews = load_previous_reviews()

        self.reviews = {
            record["record_id"]:
                self.saved_reviews[record["record_id"]]
            for record in self.records
            if record["record_id"] in self.saved_reviews
            and self.saved_reviews[
                record["record_id"]
            ]["text_sha256"] == record["text_sha256"]
        }

        self.queue = self.build_queue()

        self.position = 0
        self.session_reviewed = 0
        self.changed_decisions = 0
        self.skipped_records = 0

        self.font_size = 30
        self.finished = False

        self.root.title("DialectAlign - Privacy Review")
        self.root.geometry("1100x750")
        self.root.minsize(850, 620)
        self.root.configure(bg=self.BACKGROUND)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.finish_review,
        )

        self.configure_fonts()
        self.build_interface()
        self.bind_shortcuts()
        self.display_record()

    def build_queue(self):
        """Construct the appropriate review queue."""

        if self.recheck:

            return [
                record
                for record in self.records
                if record["record_id"] in self.reviews
                and self.reviews[
                    record["record_id"]
                ]["decision"] == "REDACTION_REQUIRED"
            ]

        return [
            record
            for record in self.records
            if record["record_id"] not in self.reviews
        ]

    def configure_fonts(self):

        available_fonts = set(
            tkfont.families(self.root)
        )

        preferred_fonts = [
            "Nirmala UI",
            "Mangal",
            "Arial Unicode MS",
        ]

        family = next(
            (
                name
                for name in preferred_fonts
                if name in available_fonts
            ),
            "Segoe UI",
        )

        self.transcript_font = tkfont.Font(
            family=family,
            size=self.font_size,
        )

    def create_label(
        self,
        parent,
        text="",
        size=12,
        color=None,
        bold=False,
    ):

        return tk.Label(
            parent,
            text=text,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal",
            ),
            bg=self.BACKGROUND,
            fg=color or self.FOREGROUND,
            anchor="w",
        )

    def build_interface(self):

        container = tk.Frame(
            self.root,
            bg=self.BACKGROUND,
            padx=28,
            pady=20,
        )

        container.pack(
            fill="both",
            expand=True,
        )

        self.create_label(
            container,
            "DialectAlign - Privacy Review",
            size=22,
            bold=True,
        ).pack(fill="x")

        mode = (
            "REVALIDATION MODE"
            if self.recheck
            else "STANDARD REVIEW MODE"
        )

        self.create_label(
            container,
            mode,
            color=self.SECONDARY,
        ).pack(fill="x", pady=(4, 12))

        self.progress_label = self.create_label(
            container,
            bold=True,
        )

        self.progress_label.pack(fill="x")

        self.progress_bar = ttk.Progressbar(
            container,
            maximum=max(len(self.queue), 1),
            mode="determinate",
        )

        self.progress_bar.pack(
            fill="x",
            pady=(8, 15),
        )

        self.metadata_label = self.create_label(
            container,
            size=11,
            color=self.SECONDARY,
        )

        self.metadata_label.pack(fill="x")

        self.previous_label = self.create_label(
            container,
            size=12,
            color="#FBBF24",
        )

        self.previous_label.pack(
            fill="x",
            pady=(5, 10),
        )

        transcript_header = tk.Frame(
            container,
            bg=self.BACKGROUND,
        )

        transcript_header.pack(fill="x")

        self.create_label(
            transcript_header,
            "LOCAL TRANSCRIPT",
            bold=True,
        ).pack(side="left")

        tk.Button(
            transcript_header,
            text="A+",
            command=lambda: self.change_font_size(2),
            width=5,
        ).pack(side="right", padx=3)

        tk.Button(
            transcript_header,
            text="A-",
            command=lambda: self.change_font_size(-2),
            width=5,
        ).pack(side="right", padx=3)

        transcript_panel = tk.Frame(
            container,
            bg=self.PANEL,
        )

        transcript_panel.pack(
            fill="both",
            expand=True,
            pady=(10, 15),
        )

        scrollbar = ttk.Scrollbar(
            transcript_panel
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.transcript = tk.Text(
            transcript_panel,
            font=self.transcript_font,
            bg=self.PANEL,
            fg=self.FOREGROUND,
            wrap="word",
            padx=20,
            pady=20,
            spacing1=5,
            spacing3=10,
            relief="flat",
            height=5,
            yscrollcommand=scrollbar.set,
            state="disabled",
        )

        self.transcript.pack(
            fill="both",
            expand=True,
        )

        scrollbar.configure(
            command=self.transcript.yview
        )

        button_panel = tk.Frame(
            container,
            bg=self.BACKGROUND,
        )

        button_panel.pack(fill="x")

        button_panel.columnconfigure(0, weight=1)
        button_panel.columnconfigure(1, weight=1)

        buttons = [
            ("1 - CLEAR", "CLEAR", "#166534"),
            (
                "2 - REDACTION REQUIRED",
                "REDACTION_REQUIRED",
                "#92400E",
            ),
            ("3 - EXCLUDE", "EXCLUDE", "#991B1B"),
            (
                "4 - UNCERTAIN",
                "UNCERTAIN",
                "#475569",
            ),
        ]

        self.decision_buttons = []

        for index, (label, decision, color) in enumerate(
            buttons
        ):

            button = tk.Button(
                button_panel,
                text=label,
                command=lambda d=decision:
                    self.process_decision(d),
                font=("Segoe UI", 12, "bold"),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                pady=12,
                cursor="hand2",
            )

            button.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=4,
                pady=4,
            )

            self.decision_buttons.append(button)

        actions = tk.Frame(
            container,
            bg=self.BACKGROUND,
        )

        actions.pack(
            fill="x",
            pady=(12, 0),
        )

        if self.recheck:

            keep_button = tk.Button(
                actions,
                text="K - Keep previous",
                command=lambda:
                    self.process_decision("KEEP"),
                padx=12,
                pady=7,
            )

            keep_button.pack(
                side="left",
                padx=4,
            )

            self.decision_buttons.append(
                keep_button
            )

        skip_button = tk.Button(
            actions,
            text="S - Skip",
            command=lambda:
                self.process_decision("SKIP"),
            padx=12,
            pady=7,
        )

        skip_button.pack(
            side="left",
            padx=4,
        )

        self.decision_buttons.append(
            skip_button
        )

        tk.Button(
            actions,
            text="Q - Save and exit",
            command=self.finish_review,
            padx=12,
            pady=7,
        ).pack(side="right")

        self.status_label = self.create_label(
            container,
            color=self.SECONDARY,
            size=10,
        )

        self.status_label.pack(
            fill="x",
            pady=(12, 0),
        )

    def bind_shortcuts(self):

        for key, decision in DECISIONS.items():

            self.root.bind(
                key,
                lambda event, d=decision:
                    self.process_decision(d),
            )

        if self.recheck:

            self.root.bind(
                "<KeyPress-k>",
                lambda event:
                    self.process_decision("KEEP"),
            )

        self.root.bind(
            "<KeyPress-s>",
            lambda event:
                self.process_decision("SKIP"),
        )

        self.root.bind(
            "<KeyPress-q>",
            lambda event:
                self.finish_review(),
        )

    def change_font_size(self, adjustment):

        self.font_size = max(
            18,
            min(
                60,
                self.font_size + adjustment,
            ),
        )

        self.transcript_font.configure(
            size=self.font_size
        )

    def display_record(self):

        self.progress_bar["value"] = self.position

        if self.position >= len(self.queue):

            self.finish_review()
            return

        record = self.queue[self.position]

        self.progress_label.configure(
            text=(
                f"Overall review: "
                f"{len(self.reviews)}/{len(self.records)}"
                f"    |    Queue: "
                f"{self.position + 1}/{len(self.queue)}"
            )
        )

        flags = ", ".join(
            sorted(record["flags"])
        )

        self.metadata_label.configure(
            text=(
                f"Record: {record['record_id']}"
                f"    |    Priority: {record['priority']}"
                f"\nFlags: {flags or 'None detected'}"
            )
        )

        previous = self.reviews.get(
            record["record_id"],
            {},
        ).get("decision", "Not reviewed")

        self.previous_label.configure(
            text=f"Previous decision: {previous}"
        )

        self.transcript.configure(
            state="normal"
        )

        self.transcript.delete("1.0", "end")

        self.transcript.insert(
            "1.0",
            record["text"],
        )

        self.transcript.configure(
            state="disabled"
        )

        self.transcript.yview_moveto(0)

    def process_decision(self, decision):

        if self.finished:
            return

        if self.position >= len(self.queue):
            return

        record = self.queue[self.position]
        record_id = record["record_id"]

        previous = self.reviews.get(
            record_id,
            {},
        ).get("decision")

        if decision == "SKIP":

            self.skipped_records += 1

            self.status_label.configure(
                text="Record skipped."
            )

        elif decision == "KEEP":

            if not self.recheck:
                return

            self.session_reviewed += 1

            self.status_label.configure(
                text="Previous decision retained."
            )

        else:

            try:

                save_decision(
                    record,
                    decision,
                    self.saved_reviews,
                )

            except Exception:

                messagebox.showerror(
                    "Save failed",
                    "The decision could not be saved. "
                    "The current record has been retained.",
                )

                return

            self.reviews[record_id] = (
                self.saved_reviews[record_id]
            )

            self.session_reviewed += 1

            if previous and previous != decision:

                self.changed_decisions += 1

            self.status_label.configure(
                text="Decision saved successfully."
            )

        self.position += 1

        self.display_record()

    def finish_review(self):

        if self.finished:
            return

        self.finished = True

        counts = Counter(
            review["decision"]
            for review in self.reviews.values()
        )

        lines = [
            f"Total records: {len(self.records)}",
            f"Reviewed records: {len(self.reviews)}",
            (
                f"Pending records: "
                f"{len(self.records) - len(self.reviews)}"
            ),
            "",
            f"Session reviewed: {self.session_reviewed}",
            f"Decisions changed: {self.changed_decisions}",
            f"Records skipped: {self.skipped_records}",
            "",
        ]

        for decision in DECISIONS.values():

            lines.append(
                f"{decision}: {counts[decision]}"
            )

        lines.extend([
            "",
            "Original corpus remains unchanged.",
            "Source status: QUARANTINED",
        ])

        summary = "\n".join(lines)

        print("\n" + "=" * 70)
        print("MANUAL PRIVACY REVIEW SUMMARY")
        print("=" * 70)
        print(summary)

        messagebox.showinfo(
            "Privacy Review Summary",
            summary,
        )

        self.root.destroy()


def main():

    parser = argparse.ArgumentParser(
        description="Graphical rural Bhojpuri privacy review."
    )

    parser.add_argument(
        "--recheck",
        action="store_true",
        help="Revalidate existing redaction decisions.",
    )

    args = parser.parse_args()

    root = tk.Tk()

    PrivacyReviewApp(
        root,
        recheck=args.recheck,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
