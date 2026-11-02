"""Render a social-preview cover (1280x640) showing the RAG assistant's flow."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BG = "#0f1115"
PANEL = "#171a21"
LINE = "#262b36"
TXT = "#e6e8ec"
MUTED = "#8b93a1"
ACCENT = "#3a8bff"
GREEN = "#36c28b"
ORANGE = "#f5a623"

fig = plt.figure(figsize=(12.8, 6.4), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def node(cx, cy, w, h, label, sub=None, edge=ACCENT, fill=PANEL, tcol=TXT):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.6,rounding_size=2.2",
                 facecolor=fill, edgecolor=edge, lw=1.8, zorder=3))
    ax.text(cx, cy + (2.0 if sub else 0), label, color=tcol, fontsize=12.5,
            ha="center", va="center", fontweight="bold", zorder=4)
    if sub:
        ax.text(cx, cy - 5.0, sub, color=MUTED, fontsize=9, ha="center", va="center", zorder=4)


def arrow(x1, y1, x2, y2, col=MUTED, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                 connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                 mutation_scale=15, color=col, lw=1.6, zorder=2))


# Title
ax.text(6, 92, "RAG Assistant", color="white", fontsize=40, fontweight="bold", va="top")
ax.text(6, 80.5, "FastAPI + LangGraph  ·  source-cited answers  ·  multi-tenant",
        color=TXT, fontsize=15, va="top")
ax.text(6, 74, "Answers only from your documents, with citations, and hands off to a human when unsure.",
        color=MUTED, fontsize=11.5, va="top", style="italic")
ax.plot([6, 30], [69.5, 69.5], color=ACCENT, lw=3)

# Flow row
y = 46
node(12, y, 17, 13, "Question", "+ tenant", edge=LINE)
node(31, y, 15, 13, "Guard", "injection check", edge=ACCENT)
node(50, y, 16, 13, "Retrieve", "hybrid search", edge=ACCENT)
node(68, y, 14, 13, "Grade", "confident?", edge=ACCENT)
node(86, 64, 16, 13, "Answer", "grounded [1][2]", edge=GREEN, tcol=GREEN)
node(86, 28, 16, 13, "Escalate", "to a human", edge=ORANGE, tcol=ORANGE)

arrow(20.5, y, 23.5, y)
arrow(38.5, y, 42, y)
arrow(58, y, 61, y)
arrow(75, y + 3, 78, 60, col=GREEN, rad=0.25)
arrow(75, y - 3, 78, 32, col=ORANGE, rad=-0.25)

# small "sources" hint under the answer
ax.text(86, 55.5, "cites the exact source", color=MUTED, fontsize=8.5, ha="center", va="top")

# Footer
ax.text(94, 7, "Python  ·  pgvector / Qdrant  ·  A. Amini", color=MUTED, fontsize=11, ha="right")

out = Path(__file__).resolve().parents[1] / "docs/cover.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, facecolor=BG)
print(f"wrote {out}")
