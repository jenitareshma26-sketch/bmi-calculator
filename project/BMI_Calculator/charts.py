"""Charts module for BMI Calculator.

Generates BMI trend line chart, category distribution pie chart,
and BMI statistics bar chart using Matplotlib.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import tkinter as tk

from database import get_bmi_trend, get_category_distribution, get_statistics
from utils import BMI_CATEGORIES


# ── Color Mapping ───────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "Underweight": "#3498db",
    "Normal Weight": "#27ae60",
    "Overweight": "#f39c12",
    "Obese Class I": "#e67e22",
    "Obese Class II": "#e74c3c",
    "Obese Class III": "#c0392b",
}

DARK_PLOT_STYLE = {
    "figure_facecolor": "#1a1a2e",
    "axes_facecolor": "#16213e",
    "axes_edgecolor": "#0f3460",
    "axes_labelcolor": "#e0e0e0",
    "text_color": "#e0e0e0",
    "grid_color": "#0f3460",
    "tick_colors": "#a0a0a0",
}

LIGHT_PLOT_STYLE = {
    "figure_facecolor": "#f5f7fa",
    "axes_facecolor": "#ffffff",
    "axes_edgecolor": "#e0e4e8",
    "axes_labelcolor": "#2c3e50",
    "text_color": "#2c3e50",
    "grid_color": "#ecf0f1",
    "tick_colors": "#7f8c8d",
}


def _apply_style(style_dict):
    """Apply a plot style dictionary to matplotlib rcParams."""
    plt.rcParams.update({
        "figure.facecolor": style_dict["figure_facecolor"],
        "axes.facecolor": style_dict["axes_facecolor"],
        "axes.edgecolor": style_dict["axes_edgecolor"],
        "axes.labelcolor": style_dict["axes_labelcolor"],
        "text.color": style_dict["text_color"],
        "xtick.color": style_dict["tick_colors"],
        "ytick.color": style_dict["tick_colors"],
        "grid.color": style_dict["grid_color"],
        "grid.alpha": 0.5,
    })


# ── BMI Trend Line Chart ────────────────────────────────────────────────────

def create_trend_chart(parent: tk.Widget, dark_mode: bool = False):
    """Create and embed the BMI trend chart into *parent*."""
    style = DARK_PLOT_STYLE if dark_mode else LIGHT_PLOT_STYLE
    _apply_style(style)

    data = get_bmi_trend()
    if not data:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                fontsize=14, color=style["text_color"])
        ax.set_axis_off()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas

    dates = [datetime.strptime(d["date"], "%Y-%m-%d %H:%M:%S") for d in data]
    bmis = [d["bmi"] for d in data]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(dates, bmis, marker="o", color="#3498db", linewidth=2,
            markersize=6, markerfacecolor="#2980b9")

    # BMI category zones
    ax.axhspan(0, 18.5, alpha=0.08, color="#3498db")
    ax.axhspan(18.5, 25, alpha=0.08, color="#27ae60")
    ax.axhspan(25, 30, alpha=0.08, color="#f39c12")
    ax.axhspan(30, 40, alpha=0.08, color="#e74c3c")

    ax.set_title("BMI Trend Over Time", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("BMI", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas


# ── Category Distribution Pie Chart ─────────────────────────────────────────

def create_pie_chart(parent: tk.Widget, dark_mode: bool = False):
    """Create and embed the category distribution pie chart."""
    style = DARK_PLOT_STYLE if dark_mode else LIGHT_PLOT_STYLE
    _apply_style(style)

    dist = get_category_distribution()
    if not dist:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                fontsize=14, color=style["text_color"])
        ax.set_axis_off()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas

    labels = list(dist.keys())
    sizes = list(dist.values())
    colors = [CATEGORY_COLORS.get(lbl, "#95a5a6") for lbl in labels]

    fig, ax = plt.subplots(figsize=(4, 3))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.8,
        textprops={"fontsize": 9, "color": style["text_color"]},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("#ffffff")

    ax.set_title("Health Category Distribution", fontsize=12,
                 fontweight="bold", pad=10)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas


# ── BMI Statistics Bar Chart ────────────────────────────────────────────────

def create_stats_bar_chart(parent: tk.Widget, dark_mode: bool = False):
    """Create and embed the BMI statistics bar chart."""
    style = DARK_PLOT_STYLE if dark_mode else LIGHT_PLOT_STYLE
    _apply_style(style)

    stats = get_statistics()
    if stats["count"] == 0:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                fontsize=14, color=style["text_color"])
        ax.set_axis_off()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas

    labels = ["Average", "Highest", "Lowest"]
    values = [stats["avg_bmi"], stats["max_bmi"], stats["min_bmi"]]
    bar_colors = []
    for v in values:
        for low, high, _, color in BMI_CATEGORIES:
            if low <= v < high:
                bar_colors.append(color)
                break
        else:
            bar_colors.append("#c0392b")

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(labels, values, color=bar_colors, width=0.5, edgecolor="none")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=style["text_color"])

    ax.set_title("BMI Statistics", fontsize=12, fontweight="bold", pad=10)
    ax.set_ylabel("BMI", fontsize=10)
    ax.set_ylim(0, max(values) * 1.25)
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas
