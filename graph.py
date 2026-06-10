import tkinter as tk
from tkinter import ttk
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def show_graph_window(parent, records, month):
    """指定月のカテゴリ別支出を円グラフ・棒グラフで表示する"""
    if not MATPLOTLIB_AVAILABLE:
        tk.messagebox.showinfo(
            "グラフ機能",
            "グラフ表示には matplotlib が必要です。\n\npip install matplotlib\n\nを実行してください。",
        )
        return

    filtered = [r for r in records if r["date"].startswith(month) and r["type"] == "支出"]
    if not filtered:
        tk.messagebox.showinfo("グラフ", f"{month} の支出データがありません。")
        return

    by_category = defaultdict(int)
    for r in filtered:
        by_category[r["category"]] += r["amount"]

    categories = list(by_category.keys())
    amounts = [by_category[c] for c in categories]

    win = tk.Toplevel(parent)
    win.title(f"グラフ表示 — {month}")
    win.geometry("900x450")

    fig = Figure(figsize=(9, 4))

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
    ax1.set_title(f"{month} カテゴリ別支出（円グラフ）")

    ax2 = fig.add_subplot(1, 2, 2)
    bars = ax2.bar(categories, amounts, color="steelblue")
    ax2.set_title(f"{month} カテゴリ別支出（棒グラフ）")
    ax2.set_ylabel("金額 (円)")
    ax2.tick_params(axis="x", rotation=30)
    for bar, amount in zip(bars, amounts):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"¥{amount:,}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
