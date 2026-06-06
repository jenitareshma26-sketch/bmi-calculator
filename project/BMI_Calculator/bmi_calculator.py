"""BMI Calculator GUI module.

Contains the main calculator page with input form, result display,
health tips, ideal weight calculator, and record management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import (
    calculate_bmi, get_category, ideal_weight_range, validate_all,
    bmi_to_progress, HEALTH_TIPS, BMI_CATEGORIES, RECOMMENDATIONS,
)


class BMICalculatorPage(tk.Frame):
    """Main BMI Calculator page."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg"])
        self.app = app
        self.theme = app.theme
        self.current_record_id = None

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_content_area()

    def _build_header(self):
        header = tk.Frame(self, bg=self.theme["header_bg"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="BMI Health Calculator",
            font=("Segoe UI", 20, "bold"), fg=self.theme["header_text"],
            bg=self.theme["header_bg"],
        ).pack(side=tk.LEFT, padx=20, pady=10)

        self.theme_btn = tk.Button(
            header, text="Dark Mode", font=("Segoe UI", 10),
            bg=self.theme["header_bg"], fg=self.theme["header_text"],
            activebackground=self.theme["header_bg"],
            activeforeground=self.theme["header_text"],
            bd=0, cursor="hand2", command=self.app.toggle_theme,
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=20, pady=10)

    def _build_content_area(self):
        container = tk.Frame(self, bg=self.theme["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left: form card
        left_card = self._card(container)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self._build_form(left_card)

        # Right: results + extras
        right = tk.Frame(container, bg=self.theme["bg"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        result_card = self._card(right)
        result_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self._build_result_panel(result_card)

        tips_card = self._card(right)
        tips_card.pack(fill=tk.BOTH, expand=True)
        self._build_tips_panel(tips_card)

    # ── Card helper ──────────────────────────────────────────────────────────

    def _card(self, parent):
        frame = tk.Frame(
            parent, bg=self.theme["card_bg"],
            highlightbackground=self.theme["card_border"],
            highlightthickness=1, bd=0,
        )
        return frame

    # ── Form ─────────────────────────────────────────────────────────────────

    def _build_form(self, parent):
        tk.Label(
            parent, text="Enter Your Details",
            font=("Segoe UI", 14, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))

        form = tk.Frame(parent, bg=self.theme["card_bg"])
        form.pack(fill=tk.X, padx=15, pady=5)

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()

        self._add_field(form, 0, "Full Name", self.name_var)
        self._add_field(form, 1, "Age", self.age_var)
        self._add_field(form, 2, "Gender", self.gender_var, widget="combobox",
                        values=["Male", "Female", "Other"])
        self._add_field(form, 3, "Weight (kg)", self.weight_var)
        self._add_field(form, 4, "Height (cm)", self.height_var)

        # Buttons
        btn_frame = tk.Frame(parent, bg=self.theme["card_bg"])
        btn_frame.pack(fill=tk.X, padx=15, pady=(15, 15))

        self._button(btn_frame, "Calculate BMI", self.theme["button_primary"],
                     self._on_calculate).pack(side=tk.LEFT, padx=(0, 8))

        self._button(btn_frame, "Save Record", self.theme["button_success"],
                     self._on_save).pack(side=tk.LEFT, padx=(0, 8))

        self._button(btn_frame, "Update Record", self.theme["button_primary"],
                     self._on_update).pack(side=tk.LEFT, padx=(0, 8))

        self._button(btn_frame, "Reset", self.theme["button_secondary"],
                     self._on_reset).pack(side=tk.LEFT, padx=(0, 8))

        self._build_ideal_weight(parent)

    def _add_field(self, parent, row, label, var, widget="entry", values=None):
        tk.Label(
            parent, text=label, font=("Segoe UI", 10),
            fg=self.theme["text_secondary"], bg=self.theme["card_bg"],
        ).grid(row=row, column=0, sticky=tk.W, pady=6)

        if widget == "entry":
            entry = tk.Entry(
                parent, textvariable=var, font=("Segoe UI", 11),
                bg=self.theme["input_bg"], fg=self.theme["text"],
                insertbackground=self.theme["text"],
                relief=tk.FLAT, bd=0,
                highlightthickness=1,
                highlightcolor=self.theme["input_focus"],
                highlightbackground=self.theme["input_border"],
            )
            entry.grid(row=row, column=1, sticky=tk.EW, pady=6, padx=(10, 0))
            entry.bind("<Enter>", lambda e: entry.config(
                highlightbackground=self.theme["input_focus"]))
            entry.bind("<Leave>", lambda e: entry.config(
                highlightbackground=self.theme["input_border"]))
        elif widget == "combobox":
            cb = ttk.Combobox(
                parent, textvariable=var, values=values,
                state="readonly", font=("Segoe UI", 11),
            )
            cb.grid(row=row, column=1, sticky=tk.EW, pady=6, padx=(10, 0))

        parent.columnconfigure(1, weight=1)

    def _build_ideal_weight(self, parent):
        sep = tk.Frame(parent, bg=self.theme["separator"], height=1)
        sep.pack(fill=tk.X, padx=15, pady=(10, 5))

        tk.Label(
            parent, text="Ideal Weight Calculator",
            font=("Segoe UI", 12, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        ).pack(anchor=tk.W, padx=15, pady=(5, 5))

        iw_frame = tk.Frame(parent, bg=self.theme["card_bg"])
        iw_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(
            iw_frame, text="Height (cm):", font=("Segoe UI", 10),
            fg=self.theme["text_secondary"], bg=self.theme["card_bg"],
        ).pack(side=tk.LEFT)

        self.iw_height_var = tk.StringVar()
        tk.Entry(
            iw_frame, textvariable=self.iw_height_var,
            font=("Segoe UI", 11), width=8,
            bg=self.theme["input_bg"], fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.theme["input_border"],
        ).pack(side=tk.LEFT, padx=8)

        self._button(iw_frame, "Calculate", self.theme["button_primary"],
                     self._on_ideal_weight).pack(side=tk.LEFT, padx=5)

        self.iw_result = tk.Label(
            iw_frame, text="", font=("Segoe UI", 10),
            fg=self.theme["info"], bg=self.theme["card_bg"],
        )
        self.iw_result.pack(side=tk.LEFT, padx=10)

    # ── Result Panel ─────────────────────────────────────────────────────────

    def _build_result_panel(self, parent):
        self.result_label = tk.Label(
            parent, text="Your BMI Result",
            font=("Segoe UI", 14, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        )
        self.result_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

        self.bmi_value_label = tk.Label(
            parent, text="--",
            font=("Segoe UI", 36, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        )
        self.bmi_value_label.pack(pady=(5, 0))

        self.category_label = tk.Label(
            parent, text="Enter your details and click Calculate",
            font=("Segoe UI", 13), fg=self.theme["text_secondary"],
            bg=self.theme["card_bg"],
        )
        self.category_label.pack(pady=(0, 5))

        # Progress bar
        self.progress_canvas = tk.Canvas(
            parent, height=30, bg=self.theme["card_bg"],
            highlightthickness=0,
        )
        self.progress_canvas.pack(fill=tk.X, padx=15, pady=5)
        self.progress_canvas.bind("<Configure>",
                                  lambda e: self._draw_progress_bar(None))

        # Recommendation
        self.rec_label = tk.Label(
            parent, text="", font=("Segoe UI", 10),
            fg=self.theme["text_secondary"], bg=self.theme["card_bg"],
            wraplength=350, justify=tk.LEFT,
        )
        self.rec_label.pack(anchor=tk.W, padx=15, pady=(5, 15))

    def _draw_progress_bar(self, bmi=None, color=None):
        c = self.progress_canvas
        c.delete("all")
        w = c.winfo_width() or 350
        h = 30
        margin = 5

        # Background bar
        c.create_rectangle(margin, 8, w - margin, 22,
                           fill=self.theme["progress_bg"], outline="")

        # Category color segments (subtle)
        segments = [
            (0.0, 0.2125, "#3498db"),
            (0.2125, 0.375, "#27ae60"),
            (0.375, 0.5, "#f39c12"),
            (0.5, 0.75, "#e74c3c"),
        ]
        bar_w = w - 2 * margin
        for start_f, end_f, seg_col in segments:
            x0 = margin + start_f * bar_w
            x1 = margin + end_f * bar_w
            c.create_rectangle(x0, 8, x1, 22, fill=seg_col, outline="",
                               stipple="gray25")

        if bmi is not None and color is not None:
            frac = bmi_to_progress(bmi)
            indicator_x = margin + frac * bar_w
            c.create_polygon(
                indicator_x, 5, indicator_x - 5, 0, indicator_x + 5, 0,
                fill=color, outline="",
            )
            c.create_line(indicator_x, 8, indicator_x, 22,
                          fill=color, width=3)

        # Labels
        for val, frac in [(18.5, 0.2125), (25, 0.375), (30, 0.5)]:
            x = margin + frac * bar_w
            c.create_line(x, 22, x, 28, fill=self.theme["text_secondary"],
                          width=1)
            c.create_text(x, 28, text=str(val), font=("Segoe UI", 7),
                          fill=self.theme["text_secondary"], anchor=tk.N)

    # ── Tips Panel ───────────────────────────────────────────────────────────

    def _build_tips_panel(self, parent):
        tk.Label(
            parent, text="Health Tips",
            font=("Segoe UI", 12, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        import random
        tips = random.sample(HEALTH_TIPS, min(4, len(HEALTH_TIPS)))

        for tip in tips:
            f = tk.Frame(parent, bg=self.theme["card_bg"])
            f.pack(fill=tk.X, padx=15, pady=1)
            tk.Label(
                f, text="\u2022", font=("Segoe UI", 10),
                fg=self.theme["info"], bg=self.theme["card_bg"],
            ).pack(side=tk.LEFT)
            tk.Label(
                f, text=tip, font=("Segoe UI", 9),
                fg=self.theme["text_secondary"], bg=self.theme["card_bg"],
                wraplength=320, justify=tk.LEFT,
            ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Frame(parent, bg=self.theme["card_bg"], height=10).pack()

    # ── Button Helper ────────────────────────────────────────────────────────

    def _button(self, parent, text, bg_color, command):
        btn = tk.Button(
            parent, text=text, font=("Segoe UI", 10, "bold"),
            bg=bg_color, fg=self.theme["button_text"],
            activebackground=bg_color, activeforeground=self.theme["button_text"],
            relief=tk.FLAT, bd=0, padx=14, pady=6,
            cursor="hand2", command=command,
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(
            bg=self._lighten(bg_color)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        return btn

    @staticmethod
    def _lighten(hex_color, amount=30):
        hex_color = hex_color.lstrip("#")
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _on_calculate(self):
        name = self.name_var.get().strip()
        age = self.age_var.get().strip()
        gender = self.gender_var.get().strip()
        weight = self.weight_var.get().strip()
        height = self.height_var.get().strip()

        ok, msg = validate_all(name, age, gender, weight, height)
        if not ok:
            messagebox.showwarning("Validation Error", msg)
            return

        bmi = calculate_bmi(float(weight), float(height))
        category, color, recommendation = get_category(bmi)

        self.bmi_value_label.config(text=f"{bmi:.2f}", fg=color)
        self.category_label.config(text=category, fg=color)
        self.rec_label.config(text=recommendation)
        self._draw_progress_bar(bmi, color)

        self._last_calc = {
            "name": name, "age": int(age), "gender": gender,
            "weight": float(weight), "height": float(height),
            "bmi": bmi, "category": category,
        }

    def _on_save(self):
        if not hasattr(self, "_last_calc"):
            messagebox.showwarning("No Data", "Please calculate BMI first.")
            return

        d = self._last_calc
        try:
            rid = db.save_record(
                d["name"], d["age"], d["gender"],
                d["weight"], d["height"], d["bmi"], d["category"],
            )
            messagebox.showinfo("Saved", f"Record saved (ID: {rid}).")
            self.current_record_id = rid
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save: {e}")

    def _on_update(self):
        if not hasattr(self, "_last_calc"):
            messagebox.showwarning("No Data", "Please calculate BMI first.")
            return
        if self.current_record_id is None:
            messagebox.showwarning("No Record",
                                   "No record selected to update. Save first.")
            return

        d = self._last_calc
        try:
            ok = db.update_record(
                self.current_record_id, d["name"], d["age"], d["gender"],
                d["weight"], d["height"], d["bmi"], d["category"],
            )
            if ok:
                messagebox.showinfo("Updated",
                                    f"Record {self.current_record_id} updated.")
            else:
                messagebox.showwarning("Not Found", "Record not found.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update: {e}")

    def _on_reset(self):
        self.name_var.set("")
        self.age_var.set("")
        self.gender_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.iw_height_var.set("")
        self.iw_result.config(text="")
        self.bmi_value_label.config(text="--", fg=self.theme["text"])
        self.category_label.config(
            text="Enter your details and click Calculate",
            fg=self.theme["text_secondary"])
        self.rec_label.config(text="")
        self._draw_progress_bar(None)
        self.current_record_id = None
        if hasattr(self, "_last_calc"):
            del self._last_calc

    def _on_ideal_weight(self):
        h = self.iw_height_var.get().strip()
        try:
            h_val = float(h)
            if h_val <= 0 or h_val > 300:
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showwarning("Invalid Input",
                                   "Enter a valid height (1-300 cm).")
            return

        lo, hi = ideal_weight_range(h_val)
        self.iw_result.config(text=f"Ideal weight: {lo} - {hi} kg")

    # ── Theme Refresh ────────────────────────────────────────────────────────

    def refresh_theme(self):
        self.theme = self.app.theme
        self.destroy()
        self.__init__(self.master, self.app)
