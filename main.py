import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from collections import defaultdict

DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


class KakeiboApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("家計簿アプリ")
        self.geometry("800x600")
        self.records = load_data()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_input = ttk.Frame(notebook)
        self.tab_summary = ttk.Frame(notebook)
        notebook.add(self.tab_input, text="入力・記録")
        notebook.add(self.tab_summary, text="月別集計")

        self._build_input_tab()
        self._build_summary_tab()

    def _build_input_tab(self):
        frame = self.tab_input

        form = ttk.LabelFrame(frame, text="新規入力", padding=10)
        form.pack(fill="x", padx=10, pady=10)

        labels = ["日付 (YYYY-MM-DD)", "種類", "カテゴリ", "金額", "メモ"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)

        self.entries["date"] = ttk.Entry(form, width=20)
        self.entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.entries["date"].grid(row=0, column=1, sticky="w", padx=5)

        self.entries["type"] = ttk.Combobox(form, values=["支出", "収入"], width=10, state="readonly")
        self.entries["type"].current(0)
        self.entries["type"].grid(row=1, column=1, sticky="w", padx=5)

        self.entries["category"] = ttk.Combobox(
            form,
            values=["食費", "交通費", "光熱費", "娯楽", "医療", "給料", "その他"],
            width=15,
        )
        self.entries["category"].grid(row=2, column=1, sticky="w", padx=5)

        self.entries["amount"] = ttk.Entry(form, width=15)
        self.entries["amount"].grid(row=3, column=1, sticky="w", padx=5)

        self.entries["memo"] = ttk.Entry(form, width=30)
        self.entries["memo"].grid(row=4, column=1, sticky="w", padx=5)

        ttk.Button(form, text="追加", command=self._add_record).grid(row=5, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(frame, text="記録一覧", padding=5)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("date", "type", "category", "amount", "memo")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        headers = {"date": "日付", "type": "種類", "category": "カテゴリ", "amount": "金額", "memo": "メモ"}
        widths = {"date": 100, "type": 60, "category": 100, "amount": 80, "memo": 200}
        for col in cols:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col])

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(frame, text="選択した記録を削除", command=self._delete_record).pack(pady=(0, 10))

    def _build_summary_tab(self):
        frame = self.tab_summary

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", padx=10, pady=10)

        ttk.Label(ctrl, text="対象月 (YYYY-MM):").pack(side="left")
        self.month_var = tk.StringVar(value=datetime.today().strftime("%Y-%m"))
        ttk.Entry(ctrl, textvariable=self.month_var, width=10).pack(side="left", padx=5)
        ttk.Button(ctrl, text="集計", command=self._show_summary).pack(side="left")

        self.summary_text = tk.Text(frame, height=20, state="disabled", font=("Consolas", 11))
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _add_record(self):
        date = self.entries["date"].get().strip()
        kind = self.entries["type"].get()
        category = self.entries["category"].get().strip()
        amount_str = self.entries["amount"].get().strip()
        memo = self.entries["memo"].get().strip()

        if not date or not category or not amount_str:
            messagebox.showwarning("入力エラー", "日付・カテゴリ・金額は必須です。")
            return

        try:
            amount = int(amount_str.replace(",", ""))
        except ValueError:
            messagebox.showwarning("入力エラー", "金額は数値で入力してください。")
            return

        record = {"date": date, "type": kind, "category": category, "amount": amount, "memo": memo}
        self.records.append(record)
        save_data(self.records)
        self._refresh_list()
        self.entries["amount"].delete(0, "end")
        self.entries["memo"].delete(0, "end")

    def _delete_record(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        del self.records[idx]
        save_data(self.records)
        self._refresh_list()

    def _refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in sorted(self.records, key=lambda x: x["date"], reverse=True):
            self.tree.insert("", "end", values=(r["date"], r["type"], r["category"], f"¥{r['amount']:,}", r["memo"]))

    def _show_summary(self):
        month = self.month_var.get().strip()
        filtered = [r for r in self.records if r["date"].startswith(month)]

        income = sum(r["amount"] for r in filtered if r["type"] == "収入")
        expense = sum(r["amount"] for r in filtered if r["type"] == "支出")

        by_category = defaultdict(int)
        for r in filtered:
            if r["type"] == "支出":
                by_category[r["category"]] += r["amount"]

        lines = [
            f"=== {month} の集計 ===\n",
            f"  収入合計:  ¥{income:>10,}",
            f"  支出合計:  ¥{expense:>10,}",
            f"  収支差額:  ¥{income - expense:>10,}",
            "\n--- カテゴリ別支出 ---",
        ]
        for cat, total in sorted(by_category.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat:<10} ¥{total:>10,}")

        if not filtered:
            lines.append("  (この月のデータがありません)")

        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "\n".join(lines))
        self.summary_text.configure(state="disabled")


if __name__ == "__main__":
    app = KakeiboApp()
    app.mainloop()
