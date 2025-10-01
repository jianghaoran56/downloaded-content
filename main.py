import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from conversion import UnitRegistry, Converter


def center_window(win, width=520, height=380):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


class UnitConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("单位换算器")
        center_window(self)

        # 引擎与注册表
        self.registry = UnitRegistry()
        self.converter = Converter(self.registry)

        # 变量
        self.category_var = tk.StringVar()
        self.from_unit_var = tk.StringVar()
        self.to_unit_var = tk.StringVar()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(root, text="通用单位换算", font=("Microsoft YaHei", 16, "bold")).pack(anchor=tk.W, pady=(0, 12))

        # 分类选择
        row1 = ttk.Frame(root)
        row1.pack(fill=tk.X, pady=6)
        ttk.Label(row1, text="类别：", width=8).pack(side=tk.LEFT)
        categories = self.registry.get_categories()
        self.category_cb = ttk.Combobox(row1, textvariable=self.category_var, values=categories, state="readonly")
        self.category_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if categories:
            self.category_var.set(categories[0])

        # 单位选择
        row2 = ttk.Frame(root)
        row2.pack(fill=tk.X, pady=6)
        ttk.Label(row2, text="从：", width=8).pack(side=tk.LEFT)
        self.from_cb = ttk.Combobox(row2, textvariable=self.from_unit_var, values=[], state="readonly")
        self.from_cb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        swap_btn = ttk.Button(row2, text="⇄ 交换", command=self._swap_units)
        swap_btn.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Label(row2, text="到：", width=8).pack(side=tk.LEFT)
        self.to_cb = ttk.Combobox(row2, textvariable=self.to_unit_var, values=[], state="readonly")
        self.to_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 输入/输出
        row3 = ttk.Frame(root)
        row3.pack(fill=tk.X, pady=6)
        ttk.Label(row3, text="数值：", width=8).pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(row3, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.insert(0, "1")

        row4 = ttk.Frame(root)
        row4.pack(fill=tk.X, pady=6)
        ttk.Label(row4, text="结果：", width=8).pack(side=tk.LEFT)
        self.output_entry = ttk.Entry(row4, textvariable=self.output_var, state="readonly")
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 操作按钮
        row5 = ttk.Frame(root)
        row5.pack(fill=tk.X, pady=14)
        convert_btn = ttk.Button(row5, text="开始换算", command=self._convert)
        convert_btn.pack(side=tk.LEFT)
        copy_btn = ttk.Button(row5, text="复制结果", command=self._copy_result)
        copy_btn.pack(side=tk.LEFT, padx=8)

        # 状态
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

        self._refresh_units()

    def _bind_events(self):
        self.category_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_units())
        self.bind("<Return>", lambda e: self._convert())

    def _refresh_units(self):
        category = self.category_var.get()
        units = self.registry.get_units(category)
        self.from_cb["values"] = units
        self.to_cb["values"] = units
        if units:
            self.from_unit_var.set(units[0])
            self.to_unit_var.set(units[1] if len(units) > 1 else units[0])
        self.status_var.set(f"已选择类别：{category}")

    def _swap_units(self):
        self.from_unit_var.set(self.to_unit_var.get())
        self.to_unit_var.set(self.from_cb.get())
        self.status_var.set("已交换单位")

    def _convert(self):
        try:
            value = float(self.input_var.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
            return

        category = self.category_var.get()
        from_unit = self.from_unit_var.get()
        to_unit = self.to_unit_var.get()
        try:
            result = self.converter.convert(category, value, from_unit, to_unit)
            self.output_var.set(self._format_number(result))
            self.status_var.set(f"已换算：{value} {from_unit} → {to_unit}")
        except Exception as e:
            messagebox.showerror("换算失败", str(e))
            self.status_var.set("换算失败")

    def _copy_result(self):
        text = self.output_var.get()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set("结果已复制到剪贴板")

    @staticmethod
    def _format_number(n):
        try:
            if abs(n) < 1e-6 or abs(n) > 1e6:
                return f"{n:.6g}"
            return f"{n:.6f}".rstrip("0").rstrip(".")
        except Exception:
            return str(n)


if __name__ == "__main__":
    app = UnitConverterApp()
    app.mainloop()