"""Dashboard module for BMI Calculator.

Displays BMI history records, statistics cards, charts, search,
and export functionality in a tabbed interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from charts import create_trend_chart, create_pie_chart, create_stats_bar_chart
from reports import export_to_csv, export_to_excel, export_to_pdf


class DashboardPage(tk.Frame):
    """BMI History Dashboard with records table, statistics, and charts."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg"])
        self.app = app
        self.theme = app.theme
        self.chart_canvases = []

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_stats_bar()
        self._build_notebook()

    def _build_header(self):
        header = tk.Frame(self, bg=self.theme["header_bg"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="BMI Dashboard",
            font=("Segoe UI", 20, "bold"), fg=self.theme["header_text"],
            bg=self.theme["header_bg"],
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # Search bar
        search_frame = tk.Frame(header, bg=self.theme["header_bg"])
        search_frame.pack(side=tk.RIGHT, padx=20)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=("Segoe UI", 11), width=20,
            bg=self.theme["input_bg"], fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.theme["input_border"],
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda e: self._on_search())

        self._header_button(search_frame, "Search",
                            self.theme["button_primary"],
                            self._on_search).pack(side=tk.LEFT, padx=(0, 5))
        self._header_button(search_frame, "Show All",
                            self.theme["button_secondary"],
                            self._load_all).pack(side=tk.LEFT)

    def _build_stats_bar(self):
        bar = tk.Frame(self, bg=self.theme["bg"])
        bar.pack(fill=tk.X, padx=20, pady=10)

        stats = db.get_statistics()
        self.stat_labels = {}
        cards = [
            ("Total Records", stats["count"], self.theme["info"]),
            ("Average BMI", stats["avg_bmi"], self.theme["warning"]),
            ("Highest BMI", stats["max_bmi"], self.theme["error"]),
            ("Lowest BMI", stats["min_bmi"], self.theme["success"]),
        ]

        for i, (title, value, color) in enumerate(cards):
            card = self._card(bar)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                      padx=(0 if i == 0 else 5, 5 if i < 3 else 0))

            tk.Label(
                card, text=title, font=("Segoe UI", 9),
                fg=self.theme["text_secondary"], bg=self.theme["card_bg"],
            ).pack(anchor=tk.W, padx=12, pady=(10, 2))

            val_label = tk.Label(
                card, text=str(value), font=("Segoe UI", 22, "bold"),
                fg=color, bg=self.theme["card_bg"],
            )
            val_label.pack(anchor=tk.W, padx=12, pady=(0, 10))
            self.stat_labels[title] = val_label

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=self.theme["bg"],
                        borderwidth=0)
        style.configure("TNotebook.Tab", background=self.theme["card_bg"],
                        foreground=self.theme["text"],
                        padding=[14, 6],
                        font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                   background=[("selected", self.theme["button_primary"])],
                   foreground=[("selected", self.theme["button_text"])])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Tab 1: Records
        records_tab = tk.Frame(self.notebook, bg=self.theme["card_bg"])
        self.notebook.add(records_tab, text="  Records  ")
        self._build_records_table(records_tab)

        # Tab 2: Charts
        charts_tab = tk.Frame(self.notebook, bg=self.theme["card_bg"])
        self.notebook.add(charts_tab, text="  Charts  ")
        self._build_charts_tab(charts_tab)

        # Tab 3: Export
        export_tab = tk.Frame(self.notebook, bg=self.theme["card_bg"])
        self.notebook.add(export_tab, text="  Export  ")
        self._build_export_tab(export_tab)

    # ── Records Table ───────────────────────────────────────────────────────

    def _build_records_table(self, parent):
        toolbar = tk.Frame(parent, bg=self.theme["card_bg"])
        toolbar.pack(fill=tk.X, padx=15, pady=10)

        self._toolbar_button(toolbar, "Delete Selected",
                             self.theme["button_danger"],
                             self._on_delete).pack(side=tk.LEFT, padx=(0, 8))
        self._toolbar_button(toolbar, "Delete All",
                             self.theme["button_danger"],
                             self._on_delete_all).pack(side=tk.LEFT, padx=(0, 8))
        self._toolbar_button(toolbar, "PDF Report",
                             self.theme["button_primary"],
                             self._on_pdf_selected).pack(side=tk.LEFT, padx=(0, 8))
        self._toolbar_button(toolbar, "Refresh",
                             self.theme["button_secondary"],
                             self._load_all).pack(side=tk.LEFT)

        tree_frame = tk.Frame(parent, bg=self.theme["card_bg"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        columns = ("id", "name", "age", "gender", "weight", "height",
                   "bmi", "category", "date_time")
        col_widths = {"id": 40, "name": 120, "age": 45, "gender": 70,
                      "weight": 70, "height": 70, "bmi": 60,
                      "category": 110, "date_time": 140}

        style = ttk.Style()
        style.configure("Treeview",
                        background=self.theme["card_bg"],
                        foreground=self.theme["text"],
                        fieldbackground=self.theme["card_bg"],
                        font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading",
                        background=self.theme["table_header_bg"],
                        foreground=self.theme["table_header_text"],
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", self.theme["sidebar_active"])],
                  foreground=[("selected", self.theme["button_text"])])

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=col_widths.get(col, 80),
                             anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self._load_all()

    # ── Charts Tab ───────────────────────────────────────────────────────────

    def _build_charts_tab(self, parent):
        self.charts_container = tk.Frame(parent, bg=self.theme["card_bg"])
        self.charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._render_charts()

    def _render_charts(self):
        for c in self.chart_canvases:
            try:
                c.get_tk_widget().destroy()
            except Exception:
                pass
        self.chart_canvases.clear()

        for widget in self.charts_container.winfo_children():
            widget.destroy()

        dark = self.app.dark_mode

        top = tk.Frame(self.charts_container, bg=self.theme["card_bg"])
        top.pack(fill=tk.BOTH, expand=True)

        trend_frame = tk.LabelFrame(
            top, text="  BMI Trend  ", font=("Segoe UI", 11, "bold"),
            fg=self.theme["text"], bg=self.theme["card_bg"],
            labelanchor=tk.N,
        )
        trend_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        c1 = create_trend_chart(trend_frame, dark_mode=dark)
        self.chart_canvases.append(c1)

        pie_frame = tk.LabelFrame(
            top, text="  Category Distribution  ",
            font=("Segoe UI", 11, "bold"),
            fg=self.theme["text"], bg=self.theme["card_bg"],
            labelanchor=tk.N,
        )
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        c2 = create_pie_chart(pie_frame, dark_mode=dark)
        self.chart_canvases.append(c2)

        bottom = tk.Frame(self.charts_container, bg=self.theme["card_bg"])
        bottom.pack(fill=tk.BOTH, expand=True)

        stats_frame = tk.LabelFrame(
            bottom, text="  BMI Statistics  ", font=("Segoe UI", 11, "bold"),
            fg=self.theme["text"], bg=self.theme["card_bg"],
            labelanchor=tk.N,
        )
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        c3 = create_stats_bar_chart(stats_frame, dark_mode=dark)
        self.chart_canvases.append(c3)

    # ── Export Tab ────────────────────────────────────────────────────────────

    def _build_export_tab(self, parent):
        center = tk.Frame(parent, bg=self.theme["card_bg"])
        center.pack(expand=True)

        tk.Label(
            center, text="Export Data",
            font=("Segoe UI", 16, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        ).pack(pady=(20, 10))

        tk.Label(
            center, text="Choose an export format below",
            font=("Segoe UI", 10), fg=self.theme["text_secondary"],
            bg=self.theme["card_bg"],
        ).pack(pady=(0, 20))

        self._export_button(center, "Export to CSV",
                            self.theme["button_success"],
                            self._on_export_csv).pack(fill=tk.X, padx=40, pady=5)
        self._export_button(center, "Export to Excel",
                            self.theme["button_primary"],
                            self._on_export_excel).pack(fill=tk.X, padx=40, pady=5)
        self._export_button(center, "Generate PDF Report",
                            self.theme["button_primary"],
                            self._on_export_pdf).pack(fill=tk.X, padx=40, pady=5)

        self.export_status = tk.Label(
            center, text="", font=("Segoe UI", 10),
            fg=self.theme["success"], bg=self.theme["card_bg"],
        )
        self.export_status.pack(pady=15)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _card(self, parent):
        return tk.Frame(
            parent, bg=self.theme["card_bg"],
            highlightbackground=self.theme["card_border"],
            highlightthickness=1, bd=0,
        )

    def _header_button(self, parent, text, bg_color, command):
        return tk.Button(
            parent, text=text, font=("Segoe UI", 9, "bold"),
            bg=bg_color, fg=self.theme["button_text"],
            activebackground=bg_color, activeforeground=self.theme["button_text"],
            relief=tk.FLAT, bd=0, padx=10, pady=4,
            cursor="hand2", command=command,
        )

    def _toolbar_button(self, parent, text, bg_color, command):
        return tk.Button(
            parent, text=text, font=("Segoe UI", 10, "bold"),
            bg=bg_color, fg=self.theme["button_text"],
            activebackground=bg_color, activeforeground=self.theme["button_text"],
            relief=tk.FLAT, bd=0, padx=12, pady=5,
            cursor="hand2", command=command,
        )

    def _export_button(self, parent, text, bg_color, command):
        return tk.Button(
            parent, text=text, font=("Segoe UI", 12, "bold"),
            bg=bg_color, fg=self.theme["button_text"],
            activebackground=bg_color, activeforeground=self.theme["button_text"],
            relief=tk.FLAT, bd=0, padx=20, pady=10,
            cursor="hand2", command=command, width=25,
        )

    # ── Data Loading ─────────────────────────────────────────────────────────

    def _load_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = db.get_all_records()
        for r in records:
            self.tree.insert("", tk.END, values=(
                r["id"], r["name"], r["age"], r["gender"],
                r["weight"], r["height"], r["bmi"],
                r["category"], r["date_time"],
            ))
        self._refresh_stats()

    def _refresh_stats(self):
        stats = db.get_statistics()
        self.stat_labels["Total Records"].config(text=str(stats["count"]))
        self.stat_labels["Average BMI"].config(text=str(stats["avg_bmi"]))
        self.stat_labels["Highest BMI"].config(text=str(stats["max_bmi"]))
        self.stat_labels["Lowest BMI"].config(text=str(stats["min_bmi"]))

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _on_search(self):
        query = self.search_var.get().strip()
        if not query:
            self._load_all()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        records = db.search_records(query)
        for r in records:
            self.tree.insert("", tk.END, values=(
                r["id"], r["name"], r["age"], r["gender"],
                r["weight"], r["height"], r["bmi"],
                r["category"], r["date_time"],
            ))

    def _on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return

        item = selected[0]
        record_id = self.tree.item(item, "values")[0]

        if messagebox.askyesno("Confirm Delete", f"Delete record {record_id}?"):
            if db.delete_record(int(record_id)):
                self.tree.delete(item)
                self._refresh_stats()
                messagebox.showinfo("Deleted", "Record deleted.")

    def _on_delete_all(self):
        if messagebox.askyesno("Confirm Delete All",
                               "Delete ALL records? This cannot be undone."):
            count = db.delete_all_records()
            self._load_all()
            messagebox.showinfo("Deleted", f"{count} records deleted.")

    def _on_pdf_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a record first.")
            return
        record_id = int(self.tree.item(selected[0], "values")[0])
        try:
            path = export_to_pdf(record_id)
            self.export_status.config(text=f"PDF saved: {path}")
            messagebox.showinfo("PDF Generated", f"Report saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _on_export_csv(self):
        try:
            path = export_to_csv()
            self.export_status.config(text=f"CSV saved: {path}")
            messagebox.showinfo("Exported", f"CSV saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _on_export_excel(self):
        try:
            path = export_to_excel()
            self.export_status.config(text=f"Excel saved: {path}")
            messagebox.showinfo("Exported", f"Excel saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _on_export_pdf(self):
        try:
            path = export_to_pdf()
            self.export_status.config(text=f"PDF saved: {path}")
            messagebox.showinfo("Exported", f"PDF saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Theme Refresh ────────────────────────────────────────────────────────

    def refresh_theme(self):
        self.theme = self.app.theme
        self.destroy()
        self.__init__(self.master, self.app)

    def refresh_charts(self):
        self._render_charts()
