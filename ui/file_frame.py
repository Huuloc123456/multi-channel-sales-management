""" ui/file_frame.py  Frame Quản lý File – Xuất/Nhập dữ liệu. Hỗ trợ: JSON (chính), CSV, TXT, XML. """

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import csv
import xml.etree.ElementTree as ET
import logging
from pathlib import Path

from ui import theme as T
from ui.widgets import IconButton, build_page_header

logger = logging.getLogger(__name__)

PRODUCT_FILE  = Path("data/products.json")
CUSTOMER_FILE = Path("data/customers.json")
ORDER_FILE    = Path("data/orders.json")


def _load_json(path: Path) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_json(path: Path, data: list):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class FileFrame(tk.Frame):
    """ Frame quản lý xuất/nhập file dữ liệu. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._build()

    def _build(self):
        # Scrollable
        import tkinter.ttk as ttk
        canvas = tk.Canvas(self, bg=T.CONTENT_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=T.CONTENT_BG)
        wid = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        build_page_header(
            inner,
            title="Quản lý File",
            subtitle="Xuất/Nhập dữ liệu – Hỗ trợ JSON, CSV, TXT, XML",
            icon="📁",
        )

        sections = [
            {
                "title":    "Sản phẩm",
                "icon":     "🗃",
                "subtitle": f"Tệp: {PRODUCT_FILE} (chính)",
                "path":     PRODUCT_FILE,
                "prefix":   "products",
                "type":     "product",
            },
            {
                "title":    "Khách hàng",
                "icon":     "👥",
                "subtitle": f"Tệp: {CUSTOMER_FILE} (chính)",
                "path":     CUSTOMER_FILE,
                "prefix":   "customers",
                "type":     "customer",
            },
            {
                "title":    "Đơn hàng",
                "icon":     "📦",
                "subtitle": f"Tệp: {ORDER_FILE} (chính)",
                "path":     ORDER_FILE,
                "prefix":   "orders",
                "type":     "order",
            },
        ]

        for sec in sections:
            self._build_section(inner, **sec)

        # Convert format section
        conv_frame = tk.Frame(inner, bg=T.CARD_BG,
                              highlightbackground=T.CARD_BORDER, highlightthickness=1)
        conv_frame.pack(fill="x", padx=24, pady=(0, 16))
        header = tk.Frame(conv_frame, bg=T.CARD_BG)
        header.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(header, text="🔄  Chuyển đổi định dạng",
                 font=T.F_SECTION_TITLE, bg=T.CARD_BG,
                 fg=T.TEXT_PRIMARY).pack(side="left")
        sub = tk.Frame(conv_frame, bg=T.CARD_BG)
        sub.pack(fill="x", padx=16)
        tk.Label(sub, text="Chuyển đổi qua lại giữa JSON → CSV → TXT → XML",
                 font=T.F_PAGE_SUBTITLE, bg=T.CARD_BG,
                 fg=T.TEXT_SECONDARY).pack(side="left")
        btn_row = tk.Frame(conv_frame, bg=T.CARD_BG)
        btn_row.pack(fill="x", padx=16, pady=(10, 14))
        IconButton(btn_row, "🔄 Chuyển đổi file...",
                   bg=T.ACCENT_RED, command=self._convert_file
                   ).pack(side="left")

    def _build_section(self, parent, title, icon, subtitle, path, prefix, type, **_):
        frame = tk.Frame(parent, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="x", padx=24, pady=(0, 12))

        # Header
        hdr = tk.Frame(frame, bg=T.CARD_BG)
        hdr.pack(fill="x", padx=16, pady=(14, 2))
        tk.Label(hdr, text=f"{icon}  {title}",
                 font=T.F_SECTION_TITLE, bg=T.CARD_BG,
                 fg=T.TEXT_PRIMARY).pack(side="left")

        tk.Label(frame, text=subtitle,
                 font=T.F_PAGE_SUBTITLE, bg=T.CARD_BG,
                 fg=T.TEXT_SECONDARY, anchor="w").pack(fill="x", padx=16, pady=(0, 10))

        btn_row = tk.Frame(frame, bg=T.CARD_BG)
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        IconButton(btn_row, "📊 Xuất CSV", bg=T.BTN_PRIMARY_BG,
                   command=lambda p=path, pr=prefix: self._export_csv(p, pr)
                   ).pack(side="left", padx=(0, 8))
        IconButton(btn_row, "📄 Xuất TXT", bg=T.BTN_EXPORT_BG,
                   command=lambda p=path, pr=prefix: self._export_txt(p, pr)
                   ).pack(side="left", padx=(0, 8))
        IconButton(btn_row, "🗒 Xuất XML", bg=T.BTN_EXPORT_BG,
                   command=lambda p=path, pr=prefix: self._export_xml(p, pr)
                   ).pack(side="left", padx=(0, 40))
        IconButton(btn_row, "📂 Nhập từ file", bg=T.ACCENT_BLUE,
                   command=lambda p=path: self._import_file(p)
                   ).pack(side="right")

    # ------------------------------------------------------------------ #
    #  EXPORT METHODS                                                      #
    # ------------------------------------------------------------------ #

    def _export_csv(self, src_path: Path, prefix: str):
        data = _load_json(src_path)
        if not data:
            messagebox.showwarning("Không có dữ liệu", "File nguồn trống hoặc chưa có dữ liệu.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"{prefix}.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            messagebox.showinfo("Xuất CSV", f"Đã xuất {len(data)} bản ghi:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export_txt(self, src_path: Path, prefix: str):
        data = _load_json(src_path)
        if not data:
            messagebox.showwarning("Không có dữ liệu", "File nguồn trống hoặc chưa có dữ liệu.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=f"{prefix}.txt",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for item in data:
                    for k, v in item.items():
                        f.write(f"{k}: {v}\n")
                    f.write("-" * 40 + "\n")
            messagebox.showinfo("Xuất TXT", f"Đã xuất {len(data)} bản ghi:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export_xml(self, src_path: Path, prefix: str):
        data = _load_json(src_path)
        if not data:
            messagebox.showwarning("Không có dữ liệu", "File nguồn trống hoặc chưa có dữ liệu.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML Files", "*.xml")],
            initialfile=f"{prefix}.xml",
        )
        if not path:
            return
        try:
            root_el = ET.Element(prefix)
            for item in data:
                record = ET.SubElement(root_el, prefix.rstrip("s"))
                for k, v in item.items():
                    if isinstance(v, list):
                        sub = ET.SubElement(record, k)
                        for vi in v:
                            entry = ET.SubElement(sub, "item")
                            if isinstance(vi, dict):
                                for sk, sv in vi.items():
                                    c = ET.SubElement(entry, sk)
                                    c.text = str(sv)
                            else:
                                entry.text = str(vi)
                    else:
                        child = ET.SubElement(record, k)
                        child.text = str(v)
            tree = ET.ElementTree(root_el)
            ET.indent(tree, space="  ")
            tree.write(path, encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Xuất XML", f"Đã xuất {len(data)} bản ghi:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _import_file(self, dest_path: Path):
        path = filedialog.askopenfilename(
            filetypes=[
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*"),
            ]
        )
        if not path:
            return
        try:
            ext = Path(path).suffix.lower()
            if ext == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif ext == ".csv":
                with open(path, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
            else:
                messagebox.showwarning("Định dạng", "Chỉ hỗ trợ JSON và CSV khi nhập.")
                return

            if not messagebox.askyesno(
                "Xác nhận nhập",
                f"Nhập {len(data)} bản ghi vào:\n{dest_path}\n\n"
                "Dữ liệu hiện có sẽ bị ghi đè!",
            ):
                return
            _save_json(dest_path, data)
            messagebox.showinfo("Nhập file", f"Đã nhập {len(data)} bản ghi.")
        except Exception as e:
            messagebox.showerror("Lỗi nhập file", str(e))

    def _convert_file(self):
        """ Chuyển đổi file giữa các định dạng. """
        path = filedialog.askopenfilename(
            title="Chọn file nguồn",
            filetypes=[
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*"),
            ],
        )
        if not path:
            return
        ext = Path(path).suffix.lower()
        try:
            if ext == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif ext == ".csv":
                with open(path, "r", encoding="utf-8-sig") as f:
                    data = list(csv.DictReader(f))
            else:
                messagebox.showwarning("Định dạng", "Chỉ hỗ trợ JSON và CSV làm nguồn.")
                return

            # Choose target format
            target = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[
                    ("CSV Files", "*.csv"),
                    ("JSON Files", "*.json"),
                    ("XML Files", "*.xml"),
                    ("Text Files", "*.txt"),
                ],
            )
            if not target:
                return
            target_ext = Path(target).suffix.lower()

            if target_ext == ".csv":
                with open(target, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
                    writer.writeheader()
                    writer.writerows(data)
            elif target_ext == ".json":
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif target_ext == ".xml":
                root_el = ET.Element("data")
                for item in data:
                    rec = ET.SubElement(root_el, "record")
                    for k, v in item.items():
                        c = ET.SubElement(rec, str(k).replace(" ", "_"))
                        c.text = str(v)
                tree = ET.ElementTree(root_el)
                ET.indent(tree, space="  ")
                tree.write(target, encoding="utf-8", xml_declaration=True)
            elif target_ext == ".txt":
                with open(target, "w", encoding="utf-8") as f:
                    for item in data:
                        for k, v in item.items():
                            f.write(f"{k}: {v}\n")
                        f.write("-" * 40 + "\n")

            messagebox.showinfo("Chuyển đổi", f"Đã chuyển đổi thành công:\n{target}")
        except Exception as e:
            messagebox.showerror("Lỗi chuyển đổi", str(e))

    def refresh(self):
        pass
