"""Main application entry point for BMI Calculator.

Initializes the root window, sidebar navigation, and manages
page switching, theme toggling, keyboard shortcuts, and about/help dialogs.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(__file__))

import database as db
from utils import LIGHT_THEME, DARK_THEME, HEALTH_TIPS
from bmi_calculator import BMICalculatorPage
from dashboard import DashboardPage


class BMIApp(tk.Tk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()

        self.dark_mode = False
        self.theme = LIGHT_THEME

        db.init_db()

        self.title("BMI Health Calculator")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=self.theme["bg"])

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._build_sidebar()
        self._build_content_area()

        self.pages = {}
        self._show_page("calculator")

        # Keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self._show_page("calculator"))
        self.bind_all("<Control-d>", lambda e: self._show_page("dashboard"))
        self.bind_all("<Control-t>", lambda e: self.toggle_theme())
        self.bind_all("<Control-h>", lambda e: self._show_help())
        self.bind_all("<F1>", lambda e: self._show_help())
        self.bind_all("<Control-a>", lambda e: self._show_about())
        self.bind_all("<Escape>", lambda e: self._on_reset())

    # ── Sidebar ──────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=self.theme["sidebar_bg"], width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="BMI Calc",
            font=("Segoe UI", 18, "bold"),
            fg=self.theme["sidebar_text"], bg=self.theme["sidebar_bg"],
        ).pack(pady=(25, 5))

        tk.Label(
            self.sidebar, text="Health Tracker",
            font=("Segoe UI", 10),
            fg=self.theme["text_secondary"], bg=self.theme["sidebar_bg"],
        ).pack(pady=(0, 20))

        self._sidebar_separator()

        self.nav_buttons = {}
        for key, label, icon in [
            ("calculator", "Calculator", "\u2295"),
            ("dashboard", "Dashboard", "\u2630"),
            ("help", "Help", "?"),
            ("about", "About", "i"),
        ]:
            btn = tk.Button(
                self.sidebar, text=f"  {icon}  {label}",
                font=("Segoe UI", 11), anchor=tk.W,
                bg=self.theme["sidebar_bg"],
                fg=self.theme["sidebar_text"],
                activebackground=self.theme["sidebar_active"],
                activeforeground=self.theme["button_text"],
                relief=tk.FLAT, bd=0, padx=20, pady=8,
                cursor="hand2",
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill=tk.X, padx=8, pady=2)
            self.nav_buttons[key] = btn

        self._sidebar_separator()

        self.theme_btn = tk.Button(
            self.sidebar, text="  \u263E  Dark Mode",
            font=("Segoe UI", 11), anchor=tk.W,
            bg=self.theme["sidebar_bg"],
            fg=self.theme["sidebar_text"],
            activebackground=self.theme["sidebar_active"],
            activeforeground=self.theme["button_text"],
            relief=tk.FLAT, bd=0, padx=20, pady=8,
            cursor="hand2", command=self.toggle_theme,
        )
        self.theme_btn.pack(fill=tk.X, padx=8, pady=2, side=tk.BOTTOM)

    def _sidebar_separator(self):
        tk.Frame(
            self.sidebar, bg=self.theme["card_border"], height=1,
        ).pack(fill=tk.X, padx=15, pady=8)

    # ── Content Area ─────────────────────────────────────────────────────────

    def _build_content_area(self):
        self.content = tk.Frame(self, bg=self.theme["bg"])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # ── Page Navigation ──────────────────────────────────────────────────────

    def _show_page(self, page_key):
        for widget in self.content.winfo_children():
            widget.destroy()

        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.config(bg=self.theme["sidebar_active"],
                           fg=self.theme["button_text"])
            else:
                btn.config(bg=self.theme["sidebar_bg"],
                           fg=self.theme["sidebar_text"])

        if page_key == "calculator":
            page = BMICalculatorPage(self.content, self)
            page.pack(fill=tk.BOTH, expand=True)
            self.pages["calculator"] = page

        elif page_key == "dashboard":
            page = DashboardPage(self.content, self)
            page.pack(fill=tk.BOTH, expand=True)
            self.pages["dashboard"] = page

        elif page_key == "help":
            self._build_help_page()

        elif page_key == "about":
            self._build_about_page()

    # ── Help Page ────────────────────────────────────────────────────────────

    def _build_help_page(self):
        frame = tk.Frame(self.content, bg=self.theme["bg"])
        frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(frame, bg=self.theme["header_bg"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header, text="Help",
            font=("Segoe UI", 20, "bold"),
            fg=self.theme["header_text"], bg=self.theme["header_bg"],
        ).pack(side=tk.LEFT, padx=20, pady=10)

        card = self._card(frame)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        help_text = (
            "Keyboard Shortcuts:\n"
            "  Ctrl+N      Open Calculator\n"
            "  Ctrl+D      Open Dashboard\n"
            "  Ctrl+T      Toggle Dark/Light Mode\n"
            "  Ctrl+H      Open Help\n"
            "  F1          Open Help\n"
            "  Ctrl+A      Open About\n"
            "  Escape      Reset Form\n"
            "\n"
            "How to Use:\n"
            "  1. Enter your details in the Calculator page.\n"
            "  2. Click \"Calculate BMI\" to see your result.\n"
            "  3. Click \"Save Record\" to store your data.\n"
            "  4. Use the Dashboard to view history, statistics, and charts.\n"
            "  5. Export your data to CSV, Excel, or PDF.\n"
            "\n"
            "BMI Categories:\n"
            "  Underweight       BMI < 18.5\n"
            "  Normal Weight     BMI 18.5 - 24.9\n"
            "  Overweight        BMI 25.0 - 29.9\n"
            "  Obese Class I     BMI 30.0 - 34.9\n"
            "  Obese Class II    BMI 35.0 - 39.9\n"
            "  Obese Class III   BMI 40.0+\n"
            "\n"
            "Disclaimer:\n"
            "  This calculator is for informational purposes only and should\n"
            "  not replace professional medical advice. Always consult a\n"
            "  healthcare provider for medical guidance."
        )

        text_widget = tk.Text(
            card, font=("Consolas", 11), wrap=tk.WORD,
            bg=self.theme["card_bg"], fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief=tk.FLAT, padx=20, pady=15,
        )
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    # ── About Page ───────────────────────────────────────────────────────────

    def _build_about_page(self):
        frame = tk.Frame(self.content, bg=self.theme["bg"])
        frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(frame, bg=self.theme["header_bg"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header, text="About",
            font=("Segoe UI", 20, "bold"),
            fg=self.theme["header_text"], bg=self.theme["header_bg"],
        ).pack(side=tk.LEFT, padx=20, pady=10)

        card = self._card(frame)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        center = tk.Frame(card, bg=self.theme["card_bg"])
        center.pack(expand=True)

        tk.Label(
            center, text="BMI Health Calculator",
            font=("Segoe UI", 24, "bold"), fg=self.theme["text"],
            bg=self.theme["card_bg"],
        ).pack(pady=(20, 5))

        tk.Label(
            center, text="Version 1.0.0",
            font=("Segoe UI", 12), fg=self.theme["text_secondary"],
            bg=self.theme["card_bg"],
        ).pack(pady=(0, 15))

        tk.Frame(center, bg=self.theme["separator"], height=1).pack(
            fill=tk.X, padx=40, pady=5)

        tk.Label(
            center, text=(
                "A comprehensive Body Mass Index calculator with\n"
                "health tracking, data visualization, and report generation.\n\n"
                "Built with Python and Tkinter."
            ),
            font=("Segoe UI", 11), fg=self.theme["text_secondary"],
            bg=self.theme["card_bg"], justify=tk.CENTER,
        ).pack(pady=15)

        tk.Label(
            center, text=(
                "For informational purposes only.\n"
                "Consult a healthcare professional for medical advice."
            ),
            font=("Segoe UI", 9, "italic"), fg=self.theme["warning"],
            bg=self.theme["card_bg"], justify=tk.CENTER,
        ).pack(pady=(0, 20))

    # ── Theme Toggle ─────────────────────────────────────────────────────────

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.configure(bg=self.theme["bg"])

        self.sidebar.destroy()
        for w in self.content.winfo_children():
            w.destroy()

        self._build_sidebar()
        if self.dark_mode:
            self.theme_btn.config(text="  \u2600  Light Mode")

        self._show_page("calculator")

    # ── Reset handler ────────────────────────────────────────────────────────

    def _on_reset(self):
        if "calculator" in self.pages and self.pages["calculator"].winfo_exists():
            self.pages["calculator"]._on_reset()

    # ── Help / About shortcuts ───────────────────────────────────────────────

    def _show_help(self):
        self._show_page("help")

    def _show_about(self):
        self._show_page("about")

    # ── Card helper ──────────────────────────────────────────────────────────

    def _card(self, parent):
        return tk.Frame(
            parent, bg=self.theme["card_bg"],
            highlightbackground=self.theme["card_border"],
            highlightthickness=1, bd=0,
        )


# ── Entry Point ─────────────────────────────────────────────────────────────

def main():
    app = BMIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
