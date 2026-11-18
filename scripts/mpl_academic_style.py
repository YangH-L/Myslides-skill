"""
Matplotlib High-Contrast Academic Plotting Toolkit (`mpl_academic_style.py`).

Enforces `Myslides-skill` Habits 3, 4, 5, 6:
  - Dual-font stack: `Times New Roman` for all Latin/digits/symbols + `SimHei` (黑体) for Chinese
  - High-contrast dark ink (`#111827`) for axes, ticks, labels, and legends (zero light gray)
  - Clean open academic frame (top & right spines hidden)
  - 7 distinct deep color palettes for cross-slide visual differentiation
  - Pre-save text assertion blocking in-chart `来源：`/`注：`, colloquial annotations, and AI buzzwords
"""
from __future__ import annotations

import re
from typing import Dict, List, Sequence, Union

import matplotlib as mpl
import matplotlib.pyplot as plt

INK_DARK = "#111827"
TITLE_NAVY = "#0B2E4F"
HIGHLIGHT_RED = "#C00000"
GRID_SUBTLE = "#CBD5E1"

PALETTES: Dict[str, Dict[str, str]] = {
    "deep_navy": {
        "primary": "#0F3D75",
        "secondary": "#2B5B84",
        "baseline": "#374151",
        "highlight": "#C00000",
    },
    "deep_teal": {
        "primary": "#0F5257",
        "secondary": "#0E7490",
        "baseline": "#334155",
        "highlight": "#C00000",
    },
    "deep_indigo": {
        "primary": "#1E3A8A",
        "secondary": "#2563EB",
        "baseline": "#374151",
        "highlight": "#C00000",
    },
    "deep_forest": {
        "primary": "#14532D",
        "secondary": "#166534",
        "baseline": "#334155",
        "highlight": "#C00000",
    },
    "deep_violet": {
        "primary": "#312E81",
        "secondary": "#4338CA",
        "baseline": "#374151",
        "highlight": "#C00000",
    },
    "prussian_amber": {
        "primary": "#0B2E4F",
        "secondary": "#9A3412",
        "baseline": "#334155",
        "highlight": "#C00000",
    },
    "deep_cobalt": {
        "primary": "#1E40AF",
        "secondary": "#3B5998",
        "baseline": "#334151",
        "highlight": "#C00000",
    },
}

PALETTE_ORDER: List[str] = list(PALETTES.keys())

FORBIDDEN_FIGURE_TEXT_PATTERNS = [
    r"来源[:：]",
    r"数据来源[:：]",
    r"^注[:：]",
    r"越高越好",
    r"越低越好",
    r"仅看可见行为",
    r"串入清零",
    r"零泄漏",
    r"零假阳性",
    r"噪声致误判",
    r"探针",
    r"金标准",
    r"金标",
    r"锁稿",
    r"全绿",
    r"架构翻转",
    r"跃升",
    r"倒挂",
    r"底座",
    r"排雷",
    r"闭环",
    r"同尺",
    r"论文矩阵",
    r"锚定",
    r"咬合",
    r"假世界",
]
FORBIDDEN_FIGURE_RE = re.compile("|".join(FORBIDDEN_FIGURE_TEXT_PATTERNS))


def apply_academic_style(dpi: int = 300) -> None:
    """Configure Matplotlib rcParams for large-screen high-contrast academic slides."""
    mpl.rcParams.update(
        {
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#FFFFFF",
            "font.family": ["Times New Roman", "SimHei", "DejaVu Sans"],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "text.color": INK_DARK,
            "axes.labelcolor": INK_DARK,
            "axes.edgecolor": INK_DARK,
            "axes.linewidth": 1.15,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": INK_DARK,
            "ytick.color": INK_DARK,
            "xtick.major.width": 1.05,
            "ytick.major.width": 1.05,
            "axes.titlesize": 13.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 11.5,
            "xtick.labelsize": 10.5,
            "ytick.labelsize": 10.5,
            "legend.fontsize": 10.5,
            "legend.frameon": False,
        }
    )


def get_palette(key_or_index: Union[str, int]) -> Dict[str, str]:
    """Return one of the 7 high-contrast palettes by name or 0-based page index."""
    if isinstance(key_or_index, int):
        key = PALETTE_ORDER[key_or_index % len(PALETTE_ORDER)]
        return dict(PALETTES[key])
    if key_or_index not in PALETTES:
        raise KeyError(f"Unknown palette {key_or_index!r}. Available: {PALETTE_ORDER}")
    return dict(PALETTES[key_or_index])


def style_axes(ax: plt.Axes, y_grid: bool = True) -> None:
    """Apply crisp high-contrast spine and subtle horizontal grid styling to an Axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(INK_DARK)
    ax.spines["bottom"].set_color(INK_DARK)
    ax.spines["left"].set_linewidth(1.15)
    ax.spines["bottom"].set_linewidth(1.15)
    ax.tick_params(axis="both", colors=INK_DARK, width=1.05)
    if y_grid:
        ax.yaxis.grid(True, linestyle="--", linewidth=0.7, color=GRID_SUBTLE, alpha=0.75)
        ax.set_axisbelow(True)


def assert_formal_figure_texts(fig: plt.Figure, extra_banned: Sequence[str] = ()) -> None:
    """
    Scan every matplotlib Text object in `fig` before saving.
    Raises AssertionError if in-chart provenance (`来源：`/`注：`), colloquial labels,
    or banned AI buzzwords are found.
    """
    extra_re = re.compile("|".join(extra_banned)) if extra_banned else None
    violations: List[str] = []
    for txt_obj in fig.findobj(mpl.text.Text):
        s = (txt_obj.get_text() or "").strip()
        if not s:
            continue
        m = FORBIDDEN_FIGURE_RE.search(s)
        if m:
            violations.append(f"Matched {m.group(0)!r} in figure text: {s!r}")
        if extra_re:
            m2 = extra_re.search(s)
            if m2:
                violations.append(f"Matched custom banned pattern {m2.group(0)!r} in: {s!r}")
    if violations:
        raise AssertionError("Figure failed Myslides-skill formal text audit:\n  - " + "\n  - ".join(violations))


if __name__ == "__main__":
    apply_academic_style()
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    pal = get_palette(0)
    ax.bar(["基线算法", "本文方法"], [52.4, 86.8], color=[pal["baseline"], pal["primary"]], width=0.45)
    ax.set_ylabel("查询吞吐率 (%)")
    ax.set_title("动态图流增量维护性能对比 (n = 300)", color=TITLE_NAVY, pad=10)
    style_axes(ax)
    assert_formal_figure_texts(fig)
    plt.close(fig)
    print("[OK] mpl_academic_style self-check passed.")
