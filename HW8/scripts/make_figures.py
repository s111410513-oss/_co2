# make_figures.py -- generate the figures used in README.md
# All numbers below are taken from the Yosys logs in ../log
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- figure 1
def box(ax, x, y, w, h, text, fc, ec="#37474f"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9.5, color="#102027")

def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                                 lw=1.4, color="#546e7a",
                                 connectionstyle="arc3,rad=0"))

def flow_figure():
    fig, ax = plt.subplots(figsize=(12.4, 5.6))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(-0.9, 5.3)
    ax.axis("off")

    done = "#a5d6a7"      # steps actually exercised in this report
    todo = "#e0e0e0"      # steps that need a PDK / commercial tool

    # front-end row
    y1 = 3.0
    boxes1 = [
        ("規格制定\nSpec", 0.15, done),
        ("RTL 設計\n(Verilog)", 2.05, done),
        ("功能驗證\n模擬 / 形式驗證", 3.95, done),
        ("邏輯合成\nSynthesis", 5.85, done),
        ("可測試性設計\nDFT / 掃描鏈", 7.75, todo),
    ]
    w, h = 1.75, 1.15
    for text, x, fc in boxes1:
        box(ax, x, y1, w, h, text, fc)
    for i in range(len(boxes1) - 1):
        x1 = boxes1[i][1] + w
        arrow(ax, x1 + 0.02, y1 + h / 2, boxes1[i + 1][1] - 0.02, y1 + h / 2)

    # back-end row
    y2 = 1.05
    boxes2 = [
        ("平面規劃\nFloorplan", 0.15, todo),
        ("佈局\nPlacement", 2.05, todo),
        ("時鐘樹\nCTS", 3.95, todo),
        ("繞線\nRouting", 5.85, todo),
        ("實體驗證\nDRC / LVS", 7.75, todo),
    ]
    for text, x, fc in boxes2:
        box(ax, x, y2, w, h, text, fc)
    for i in range(len(boxes2) - 1):
        x1 = boxes2[i][1] + w
        arrow(ax, x1 + 0.02, y2 + h / 2, boxes2[i + 1][1] - 0.02, y2 + h / 2)

    # DFT -> floorplan (routed connector: down, left, down)
    xs, ys = 8.625, 3.0
    xm, ym = 1.025, 2.62
    ax.plot([xs, xs, xm], [ys, ym, ym], color="#546e7a", lw=1.4, solid_capstyle="round", zorder=2)
    arrow(ax, xm, ym, xm, 2.22)

    # tape-out chain
    box(ax, 9.75, y2, 1.35, h, "時序簽核\nSTA", todo)
    arrow(ax, 7.75 + w + 0.02, y2 + h / 2, 9.73, y2 + h / 2)
    box(ax, 11.25, y2, 1.0, h, "GDSII\n光罩", "#fff59d")
    arrow(ax, 11.12, y2 + h / 2, 11.23, y2 + h / 2)

    # stage bands
    ax.add_patch(plt.Rectangle((0.05, 2.85), 12.3, 1.55, fc="#f1f8e9" if False else "#e8f5e9",
                               ec="none", zorder=0))
    ax.add_patch(plt.Rectangle((0.05, 0.9), 12.3, 1.55, fc="#eceff1", ec="none", zorder=0))
    for patch in ax.patches:
        patch.set_zorder(2)
    ax.text(0.12, 4.42, "前端設計 Front-end（本報告涵蓋）", fontsize=10, color="#2e7d32", weight="bold")
    ax.text(0.12, 2.55, "後端設計 Back-end（需要 PDK 與商業 EDA）", fontsize=10, color="#37474f", weight="bold")

    # legend
    ax.add_patch(FancyBboxPatch((0.15, -0.45), 0.32, 0.22, boxstyle="round,pad=0.01", fc=done, ec="#37474f"))
    ax.text(0.55, -0.34, "本報告以開源工具實際執行", fontsize=9, va="center")
    ax.add_patch(FancyBboxPatch((3.9, -0.45), 0.32, 0.22, boxstyle="round,pad=0.01", fc=todo, ec="#37474f"))
    ax.text(4.3, -0.34, "本次未執行（缺 PDK / 商業授權）", fontsize=9, va="center")

    ax.set_title("圖 1　IC 設計流程與 EDA 工具的分工", fontsize=12.5, pad=6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_flow.png"), dpi=200)
    plt.close(fig)

# ---------------------------------------------------------------- figure 2
def cells_figure():
    cats = ["$_AND_", "$_OR_", "$_XOR_", "$_NOT_", "$_MUX_", "DFF"]
    alu = [109, 86, 22, 21, 19, 0]
    cnt = [8, 19, 13, 8, 9, 8]
    colors = ["#42a5f5", "#66bb6a", "#ffa726", "#ef5350", "#ab47bc", "#8d6e63"]

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    x = [0, 1]
    bottom = [0, 0]
    for i, c in enumerate(cats):
        vals = [alu[i], cnt[i]]
        ax.bar(x, vals, 0.45, bottom=bottom, label=c, color=colors[i], edgecolor="white")
        for xi, v, b in zip(x, vals, bottom):
            if v >= 8:
                ax.text(xi, b + v / 2, str(v), ha="center", va="center", fontsize=9, color="white")
        bottom = [b + v for b, v in zip(bottom, vals)]

    for xi, tot in zip(x, bottom):
        ax.text(xi, tot + 4, f"總計 {tot} 個 cell", ha="center", fontsize=10.5, weight="bold")

    ax.set_xticks(x, ["alu（8-bit ALU，組合邏輯）", "counter（8-bit 計數器，序向邏輯）"])
    ax.set_ylabel("cell 數量")
    ax.set_ylim(0, 300)
    ax.set_title("圖 2　Yosys 泛用閘級合成結果（abc -g AND,OR,XOR,MUX）", fontsize=12)
    ax.legend(ncol=6, fontsize=8.5, loc="upper right", frameon=False)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_cells.png"), dpi=200)
    plt.close(fig)

# ---------------------------------------------------------------- figure 3
def fpga_figure():
    cats = ["SB_LUT4", "SB_CARRY", "SB_DFFER"]
    alu = [111, 14, 0]
    cnt = [31, 12, 8]
    colors = ["#29b6f6", "#ffca28", "#ec407a"]

    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    x = [0, 1]
    bottom = [0, 0]
    for i, c in enumerate(cats):
        vals = [alu[i], cnt[i]]
        ax.bar(x, vals, 0.42, bottom=bottom, label=c, color=colors[i], edgecolor="white")
        for xi, v, b in zip(x, vals, bottom):
            if v:
                ax.text(xi, b + v / 2, str(v), ha="center", va="center", fontsize=9, color="#263238")
        bottom = [b + v for b, v in zip(bottom, vals)]

    for xi, tot in zip(x, bottom):
        ax.text(xi, tot + 3, f"總計 {tot} 個資源", ha="center", fontsize=10.5, weight="bold")

    ax.set_xticks(x, ["alu → iCE40", "counter → iCE40"])
    ax.set_ylabel("資源數量")
    ax.set_ylim(0, 150)
    ax.set_title("圖 3　同一份 RTL 映射到 Lattice iCE40 FPGA（LUT4 / 進位鏈 / DFF）", fontsize=12)
    ax.legend(ncol=3, fontsize=9, loc="upper right", frameon=False)
    ax.grid(axis="y", ls=":", alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_fpga.png"), dpi=200)
    plt.close(fig)

# ---------------------------------------------------------------- figure 4
def depth_figure():
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    names = ["alu", "counter"]
    depth = [10, 36]
    bars = ax.barh(names, depth, color=["#5c6bc0", "#26a69a"], height=0.45)
    for b, v in zip(bars, depth):
        ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{v} 級邏輯", va="center", fontsize=10)
    ax.set_xlim(0, 44)
    ax.set_xlabel("最長拓撲路徑（logic levels）")
    ax.set_title("圖 4　合成後之路徑深度（Yosys ltp，未計入實際元件延遲）", fontsize=11.5)
    ax.grid(axis="x", ls=":", alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_depth.png"), dpi=200)
    plt.close(fig)

if __name__ == "__main__":
    flow_figure()
    cells_figure()
    fpga_figure()
    depth_figure()
    print("figures written to", OUT)
