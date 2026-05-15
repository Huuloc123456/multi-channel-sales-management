""" ui/charts.py  Các widget biểu đồ thuần tkinter (Canvas) – không cần matplotlib. Bao gồm: BarChart, PieChart, LineChart, HBarChart (ngang). """

import tkinter as tk
import math
from ui import theme as T


# ─────────────────────────────────────────────────────────────────────────── #
#  HELPERS                                                                    #
# ─────────────────────────────────────────────────────────────────────────── #

def _lighten(hex_color: str, factor: float = 0.3) -> str:
    """ Làm sáng màu hex. """
    try:
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


PALETTE = [
    "#2196f3", "#e83e5a", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#3498db",
    "#1877f2", "#ee4d2d", "#fe2c55",
]


# ─────────────────────────────────────────────────────────────────────────── #
#  BAR CHART (dọc)                                                            #
# ─────────────────────────────────────────────────────────────────────────── #

class BarChart(tk.Canvas):
    """ Biểu đồ cột dọc. data: list of (label: str, value: float) """

    PAD_L = 60   # left padding (for y-axis labels)
    PAD_B = 40   # bottom padding (for x-axis labels)
    PAD_T = 20   # top padding
    PAD_R = 20   # right padding
    BAR_GAP = 0.3  # gap ratio between bars

    def __init__(self, parent, data: list[tuple], title: str = "",
                 color: str = "#2196f3", bg: str = T.CARD_BG, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=bg, **kwargs)
        self._data  = data
        self._title = title
        self._color = color
        self._bg    = bg
        self.bind("<Configure>", self._redraw)

    def update_data(self, data: list[tuple]):
        self._data = data
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        if not self._data:
            self._no_data()
            return

        W = self.winfo_width()
        H = self.winfo_height()
        if W < 10 or H < 10:
            return

        # Draw area
        ax_x0 = self.PAD_L
        ax_y0 = self.PAD_T
        ax_x1 = W - self.PAD_R
        ax_y1 = H - self.PAD_B

        values = [max(0, v) for _, v in self._data]
        max_v  = max(values) if values else 1
        if max_v == 0:
            max_v = 1

        # Y-axis grid lines + labels
        n_ticks = 5
        for i in range(n_ticks + 1):
            frac = i / n_ticks
            y    = ax_y1 - frac * (ax_y1 - ax_y0)
            val  = max_v * frac
            label = _fmt_val(val)
            self.create_line(ax_x0, y, ax_x1, y,
                             fill="#e8eaf0", width=1, dash=(3, 3))
            self.create_text(ax_x0 - 6, y, text=label,
                             anchor="e", font=(T.FONT_APP, 7), fill=T.TEXT_SECONDARY)

        # Bars
        n    = len(self._data)
        slot = (ax_x1 - ax_x0) / n
        bw   = slot * (1 - self.BAR_GAP)

        for i, (label, val) in enumerate(self._data):
            x0 = ax_x0 + i * slot + slot * self.BAR_GAP / 2
            x1 = x0 + bw
            bar_h = (val / max_v) * (ax_y1 - ax_y0)
            y0 = ax_y1 - bar_h
            y1 = ax_y1

            # Bar (with rounded top feel using two rects)
            color = PALETTE[i % len(PALETTE)] if self._color == "auto" else self._color
            self.create_rectangle(x0, y0, x1, y1,
                                  fill=color, outline="", width=0)
            # Value label above bar
            mid_x = (x0 + x1) / 2
            if bar_h > 14:
                self.create_text(mid_x, y0 - 4, text=_fmt_val(val),
                                 anchor="s", font=(T.FONT_APP, 7, "bold"),
                                 fill=T.TEXT_PRIMARY)

            # X-axis label
            short = label if len(label) <= 10 else label[:9] + "…"
            self.create_text(mid_x, ax_y1 + 6, text=short,
                             anchor="n", font=(T.FONT_APP, 7), fill=T.TEXT_SECONDARY)

        # Axes
        self.create_line(ax_x0, ax_y0, ax_x0, ax_y1, fill="#bbb", width=1)
        self.create_line(ax_x0, ax_y1, ax_x1, ax_y1, fill="#bbb", width=1)

        # Title
        if self._title:
            self.create_text(W / 2, 8, text=self._title,
                             anchor="n", font=(T.FONT_APP, 9, "bold"),
                             fill=T.TEXT_PRIMARY)

    def _no_data(self):
        W, H = self.winfo_width(), self.winfo_height()
        self.create_text(W/2, H/2, text="Chưa có dữ liệu",
                         font=(T.FONT_APP, 10), fill=T.TEXT_MUTED)


# ─────────────────────────────────────────────────────────────────────────── #
#  HORIZONTAL BAR CHART                                                       #
# ─────────────────────────────────────────────────────────────────────────── #

class HBarChart(tk.Canvas):
    """ Biểu đồ cột ngang – phù hợp hiển thị doanh thu theo kênh. """

    PAD_L = 90
    PAD_R = 80
    PAD_T = 16
    PAD_B = 12
    ROW_H = 30

    def __init__(self, parent, data: list[tuple],
                 bg: str = T.CARD_BG, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=bg, **kwargs)
        self._data = data
        self._bg   = bg
        self.bind("<Configure>", self._redraw)

    def update_data(self, data: list[tuple]):
        self._data = data
        h = max(80, self.PAD_T + self.PAD_B + len(data) * (self.ROW_H + 6))
        self.config(height=h)
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        if not self._data:
            return
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 10:
            return

        max_v = max(v for _, v in self._data) or 1
        ax_x0 = self.PAD_L
        ax_x1 = W - self.PAD_R

        for i, (label, val) in enumerate(self._data):
            y_mid = self.PAD_T + i * (self.ROW_H + 6) + self.ROW_H / 2
            y0    = y_mid - 10
            y1    = y_mid + 10

            # Label
            short = label if len(label) <= 12 else label[:11] + "…"
            self.create_text(ax_x0 - 6, y_mid, text=short,
                             anchor="e", font=(T.FONT_APP, 8), fill=T.TEXT_PRIMARY)

            # Track
            self.create_rectangle(ax_x0, y0, ax_x1, y1,
                                  fill="#f0f1f5", outline="", width=0)

            # Fill
            fill_w = int((val / max_v) * (ax_x1 - ax_x0))
            if fill_w > 0:
                color = PALETTE[i % len(PALETTE)]
                self.create_rectangle(ax_x0, y0, ax_x0 + fill_w, y1,
                                      fill=color, outline="", width=0)

            # Value
            pct = val / max_v * 100
            self.create_text(ax_x1 + 6, y_mid,
                             text=f"{_fmt_val(val)} ({pct:.0f}%)",
                             anchor="w", font=(T.FONT_APP, 7, "bold"),
                             fill=T.TEXT_PRIMARY)


# ─────────────────────────────────────────────────────────────────────────── #
#  PIE CHART                                                                  #
# ─────────────────────────────────────────────────────────────────────────── #

class PieChart(tk.Canvas):
    """ Biểu đồ tròn (Pie/Donut) với legend. """

    def __init__(self, parent, data: list[tuple],
                 donut: bool = True, bg: str = T.CARD_BG, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=bg, **kwargs)
        self._data  = data
        self._donut = donut
        self._bg    = bg
        self.bind("<Configure>", self._redraw)

    def update_data(self, data: list[tuple]):
        self._data = data
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        if not self._data:
            self._no_data()
            return

        W = self.winfo_width()
        H = self.winfo_height()
        if W < 10 or H < 10:
            return

        total = sum(max(0, v) for _, v in self._data) or 1
        LEGEND_W = 160
        chart_w  = W - LEGEND_W
        cx = chart_w / 2
        cy = H / 2
        r  = min(chart_w, H) / 2 - 16
        if r < 10:
            return
        r_inner = r * 0.55 if self._donut else 0

        start = -90.0  # start from top
        for i, (label, val) in enumerate(self._data):
            if val <= 0:
                continue
            extent = (val / total) * 360
            color  = PALETTE[i % len(PALETTE)]

            self.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=start, extent=extent,
                            fill=color, outline=T.CARD_BG, width=2)
            if self._donut and r_inner > 0:
                # Mask inner
                self.create_oval(cx - r_inner, cy - r_inner,
                                 cx + r_inner, cy + r_inner,
                                 fill=self._bg, outline=self._bg)
            start += extent

        # Center text (donut)
        if self._donut:
            self.create_text(cx, cy - 8, text="Doanh thu",
                             font=(T.FONT_APP, 7), fill=T.TEXT_SECONDARY, anchor="center")
            self.create_text(cx, cy + 8, text=f"{len(self._data)} kênh",
                             font=(T.FONT_APP, 8, "bold"), fill=T.TEXT_PRIMARY, anchor="center")

        # Legend
        lx = chart_w + 10
        ly = 16
        for i, (label, val) in enumerate(self._data):
            color = PALETTE[i % len(PALETTE)]
            pct   = val / total * 100
            self.create_rectangle(lx, ly + i * 22, lx + 12, ly + i * 22 + 12,
                                  fill=color, outline="")
            short = label if len(label) <= 14 else label[:13] + "…"
            self.create_text(lx + 16, ly + i * 22 + 6,
                             text=f"{short} {pct:.1f}%",
                             anchor="w", font=(T.FONT_APP, 7), fill=T.TEXT_PRIMARY)

    def _no_data(self):
        W, H = self.winfo_width(), self.winfo_height()
        self.create_text(W/2, H/2, text="Chưa có dữ liệu",
                         font=(T.FONT_APP, 10), fill=T.TEXT_MUTED)


# ─────────────────────────────────────────────────────────────────────────── #
#  LINE CHART                                                                 #
# ─────────────────────────────────────────────────────────────────────────── #

class LineChart(tk.Canvas):
    """ Biểu đồ đường – hiển thị xu hướng theo thời gian. series: list of (series_name, [(label, value), ...]) """

    PAD_L = 64
    PAD_B = 36
    PAD_T = 24
    PAD_R = 20

    def __init__(self, parent, series: list, title: str = "",
                 bg: str = T.CARD_BG, **kwargs):
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=bg, **kwargs)
        self._series = series
        self._title  = title
        self._bg     = bg
        self.bind("<Configure>", self._redraw)

    def update_series(self, series: list):
        self._series = series
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        if not self._series:
            self._no_data()
            return

        W = self.winfo_width()
        H = self.winfo_height()
        if W < 10 or H < 10:
            return

        ax_x0 = self.PAD_L
        ax_y0 = self.PAD_T
        ax_x1 = W - self.PAD_R
        ax_y1 = H - self.PAD_B

        # Collect all values
        all_vals = [v for _, pts in self._series for _, v in pts]
        max_v = max(all_vals) if all_vals else 1
        if max_v == 0:
            max_v = 1

        # Y-axis ticks
        for i in range(6):
            frac = i / 5
            y    = ax_y1 - frac * (ax_y1 - ax_y0)
            val  = max_v * frac
            self.create_line(ax_x0, y, ax_x1, y,
                             fill="#e8eaf0", width=1, dash=(3, 3))
            self.create_text(ax_x0 - 6, y, text=_fmt_val(val),
                             anchor="e", font=(T.FONT_APP, 7), fill=T.TEXT_SECONDARY)

        # Draw series
        # Use x-labels from first series
        if self._series:
            labels = [lbl for lbl, _ in self._series[0][1]]
            n      = len(labels)
            if n > 1:
                x_step = (ax_x1 - ax_x0) / (n - 1)
            else:
                x_step = (ax_x1 - ax_x0)

            # X-labels
            for i, lbl in enumerate(labels):
                x = ax_x0 + i * x_step if n > 1 else (ax_x0 + ax_x1) / 2
                self.create_text(x, ax_y1 + 6, text=lbl,
                                 anchor="n", font=(T.FONT_APP, 7),
                                 fill=T.TEXT_SECONDARY)

        for s_i, (s_name, points) in enumerate(self._series):
            color = PALETTE[s_i % len(PALETTE)]
            n = len(points)
            if n == 0:
                continue
            x_step = (ax_x1 - ax_x0) / max(n - 1, 1)
            coords = []
            for i, (_, val) in enumerate(points):
                x = ax_x0 + i * x_step
                y = ax_y1 - (val / max_v) * (ax_y1 - ax_y0)
                coords.append((x, y))

            # Area fill
            area_pts = [ax_x0, ax_y1] + [c for pt in coords for c in pt] + [coords[-1][0], ax_y1]
            self.create_polygon(*area_pts,
                                fill=_lighten(color, 0.7), outline="")

            # Line
            for i in range(len(coords) - 1):
                x0, y0_ = coords[i]
                x1_, y1_ = coords[i + 1]
                self.create_line(x0, y0_, x1_, y1_,
                                 fill=color, width=2, smooth=True)

            # Dots
            for x, y in coords:
                self.create_oval(x - 4, y - 4, x + 4, y + 4,
                                 fill=color, outline=T.CARD_BG, width=2)

            # Legend entry
            lx = ax_x1 - 100 + s_i * 110
            self.create_rectangle(ax_x0 + s_i * 100, 6,
                                  ax_x0 + s_i * 100 + 10, 14,
                                  fill=color, outline="")
            self.create_text(ax_x0 + s_i * 100 + 14, 10,
                             text=s_name, anchor="w",
                             font=(T.FONT_APP, 7), fill=T.TEXT_PRIMARY)

        # Axes
        self.create_line(ax_x0, ax_y0, ax_x0, ax_y1, fill="#bbb", width=1)
        self.create_line(ax_x0, ax_y1, ax_x1, ax_y1, fill="#bbb", width=1)

        if self._title:
            self.create_text(W / 2, 8, text=self._title,
                             anchor="n", font=(T.FONT_APP, 9, "bold"),
                             fill=T.TEXT_PRIMARY)

    def _no_data(self):
        W, H = self.winfo_width(), self.winfo_height()
        self.create_text(W/2, H/2, text="Chưa có dữ liệu",
                         font=(T.FONT_APP, 10), fill=T.TEXT_MUTED)


# ─────────────────────────────────────────────────────────────────────────── #
#  HELPER                                                                     #
# ─────────────────────────────────────────────────────────────────────────── #

def _fmt_val(v: float) -> str:
    """ Format số lớn thành dạng ngắn gọn. """
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return f"{int(v)}"
