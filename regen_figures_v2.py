"""
regen_figures_v2.py
Regenerates all 6 report diagrams with minimum 11pt font sizes and larger figure dimensions.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from pathlib import Path

NAVY  = "#0D2C54"
BLUE  = "#1A6BC4"
STEEL = "#3A5F8F"
LGRAY = "#F0F4F8"
MGRAY = "#BDC8D8"
WHITE = "#FFFFFF"

FIG_DIR = Path("Owner's Inbox/figures")
FIG_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Agentic AI Capability Loop
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 8), facecolor=WHITE)
ax.set_xlim(-1.65, 1.65); ax.set_ylim(-1.6, 1.7); ax.set_aspect("equal"); ax.axis("off")

steps = [
    ("1. GOAL\nReceived",   90,  "User or system\ndefines objective"),
    ("2. PLAN\nDevised",    18,  "Agent breaks goal\ninto steps"),
    ("3. TOOLS\nActivated", -54, "APIs, databases,\nbrowsers accessed"),
    ("4. ACTIONS\nExecuted",-126,"Tasks completed\nacross systems"),
    ("5. RESULTS\nObserved",-198,"Output reviewed;\nadapt if needed"),
]
r = 1.08
for (label, angle, sub) in steps:
    rad = np.radians(angle)
    x, y = r * np.cos(rad), r * np.sin(rad)
    circle = plt.Circle((x, y), 0.30, color=NAVY, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y + 0.06, label.split("\n")[0], ha="center", va="center",
            fontsize=11, fontweight="bold", color=WHITE, zorder=4)
    ax.text(x, y - 0.10, label.split("\n")[1], ha="center", va="center",
            fontsize=11, color=MGRAY, zorder=4)
    # sub-label outside circle
    ox, oy = (r + 0.44) * np.cos(rad), (r + 0.44) * np.sin(rad)
    ax.text(ox, oy, sub, ha="center", va="center",
            fontsize=10, color=STEEL, multialignment="center",
            bbox=dict(facecolor=LGRAY, edgecolor=MGRAY, boxstyle="round,pad=0.25", alpha=0.8))

# curved arrows
for i, (_, angle, _s) in enumerate(steps):
    next_angle = steps[(i + 1) % len(steps)][1]
    start_rad = np.radians(angle - 24)
    end_rad   = np.radians(next_angle + 24)
    sx, sy = (r + 0.02) * np.cos(start_rad), (r + 0.02) * np.sin(start_rad)
    ex, ey = (r + 0.02) * np.cos(end_rad),   (r + 0.02) * np.sin(end_rad)
    ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=2.2,
                                connectionstyle="arc3,rad=-0.28"))

# centre
centre = plt.Circle((0, 0), 0.34, color=BLUE, zorder=2)
ax.add_patch(centre)
ax.text(0, 0.07, "AGENTIC", ha="center", va="center",
        fontsize=12, fontweight="bold", color=WHITE, zorder=3)
ax.text(0, -0.12, "AI LOOP", ha="center", va="center",
        fontsize=11, fontweight="bold", color=WHITE, zorder=3)

ax.set_title(
    "Figure 1: The Agentic AI Capability Loop\n"
    "How an agent autonomously pursues a goal through continuous cycles of planning, action, and adaptation",
    fontsize=13, fontweight="bold", color=NAVY, pad=14,
)
plt.tight_layout(pad=1.2)
plt.savefig(FIG_DIR / "fig1_capability_loop.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 1 done")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — GenAI vs Agentic AI comparison table
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 9), facecolor=WHITE)
ax.axis("off")

rows = [
    ("Interaction Mode",  "Prompt → single response",           "Goal → multi-step execution"),
    ("Output",            "Text, code, images, summaries",      "Completed workflows and outcomes"),
    ("Human Role",        "Directs every step manually",        "Sets goal; reviews exceptions only"),
    ("Tool Access",       "Limited — text in, text out",        "APIs, databases, browsers, code runners"),
    ("Duration",          "Seconds per interaction",            "Minutes to days per goal"),
    ("Scale Effect",      "Boosts individual productivity",     "Transforms entire process economics"),
    ("Risk Profile",      "Output accuracy / hallucination",    "Compound error, auditability, control"),
    ("Banking Analogy",   "Expert advisor you consult",         "Delegated team member you brief"),
]

col_labels = ["Dimension", "Generative AI", "Agentic AI"]
col_x = [0.02, 0.30, 0.63]
col_w = [0.26, 0.31, 0.36]
header_h = 0.87
row_h    = 0.097

for j, (label, x, w) in enumerate(zip(col_labels, col_x, col_w)):
    colour = "#D0D8E4" if j == 0 else (STEEL if j == 1 else NAVY)
    rect = FancyBboxPatch((x, header_h), w - 0.01, row_h,
                          boxstyle="round,pad=0.005", facecolor=colour,
                          edgecolor="none", transform=ax.transAxes, clip_on=False)
    ax.add_patch(rect)
    ax.text(x + (w / 2) - 0.005, header_h + row_h / 2, label,
            ha="center", va="center", fontsize=12, fontweight="bold",
            color=WHITE if j > 0 else NAVY, transform=ax.transAxes)

for i, (dim, gen, agent) in enumerate(rows):
    y = header_h - (i + 1) * row_h
    bg = WHITE if i % 2 == 0 else "#EEF3F9"
    for j, (txt, x, w) in enumerate(zip([dim, gen, agent], col_x, col_w)):
        fc = "#E4EBF3" if j == 0 else bg
        rect = FancyBboxPatch((x, y), w - 0.01, row_h - 0.005,
                              boxstyle="round,pad=0.003", facecolor=fc,
                              edgecolor=MGRAY, linewidth=0.4,
                              transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)
        clr    = NAVY if j == 0 else ("#333333" if j == 1 else NAVY)
        weight = "bold" if j == 0 else "normal"
        ax.text(x + 0.012, y + row_h / 2 - 0.004, txt,
                ha="left", va="center", fontsize=11, color=clr,
                fontweight=weight, transform=ax.transAxes)

ax.set_title(
    "Figure 2: Generative AI vs Agentic AI — Eight Key Dimensions Compared",
    fontsize=13, fontweight="bold", color=NAVY, pad=14,
)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig2_genai_vs_agentic.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 2 done")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Autonomy Spectrum + Taxonomy
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(15, 9), facecolor=WHITE)
ax = fig.add_axes([0.03, 0.05, 0.94, 0.88])
ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis("off")

ax.text(7, 8.65, "Figure 3: The Agentic AI Spectrum and Architecture Taxonomy",
        ha="center", va="center", fontsize=14, fontweight="bold", color=NAVY)
ax.text(7, 8.22, "From human-led workflows to fully autonomous agents — and how they can be structured",
        ha="center", va="center", fontsize=11, color=STEEL)

# gradient bar
bar_y, bar_h = 6.0, 0.65
cmap = LinearSegmentedColormap.from_list("spec", [STEEL, NAVY])
gradient = np.linspace(0, 1, 256).reshape(1, -1)
ax.imshow(gradient, extent=[0.5, 13.5, bar_y, bar_y + bar_h], aspect="auto",
          cmap=cmap, zorder=1)
ax.text(0.2, bar_y + bar_h / 2, "HIGH\nHUMAN\nCONTROL",
        ha="center", va="center", fontsize=9.5, color=STEEL, fontweight="bold")
ax.text(13.8, bar_y + bar_h / 2, "HIGH\nAUTONOMY",
        ha="center", va="center", fontsize=9.5, color=NAVY, fontweight="bold")

types = [
    (1.8,  "Human-Led\nWorkflows",        "AI suggests;\nhuman decides\nand acts",            STEEL),
    (4.8,  "Agentic\nWorkflows",          "AI executes;\nhuman approves\nat checkpoints",      BLUE),
    (8.2,  "Semi-Autonomous\nAgents",     "AI acts within\npre-approved\nboundaries",          "#1050A0"),
    (11.8, "Fully Autonomous\nAgents",    "AI pursues goals\nwith minimal\nper-step oversight", NAVY),
]
for (x, label, desc, colour) in types:
    ax.plot([x, x], [bar_y, bar_y - 0.4], color=colour, lw=2.0, zorder=2)
    box = FancyBboxPatch((x - 1.1, bar_y - 2.45), 2.2, 2.0,
                         boxstyle="round,pad=0.07", facecolor=colour,
                         edgecolor="none", alpha=0.93, zorder=2)
    ax.add_patch(box)
    ax.text(x, bar_y - 1.25, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color=WHITE, zorder=3, multialignment="center")
    ax.text(x, bar_y - 2.1, desc, ha="center", va="center",
            fontsize=10, color=LGRAY, zorder=3, multialignment="center")

# architecture taxonomy
ax.text(7, 3.1, "MULTI-AGENT ARCHITECTURE PATTERNS",
        ha="center", va="center", fontsize=12, fontweight="bold", color=NAVY)

arch_types = [
    (2.4,  "Single\nAgent",          "One agent manages the\ncomplete task end-to-end.\nBest for simple, linear\nworkflows.",                  STEEL),
    (7.0,  "Multi-Agent\n(Parallel)", "Multiple specialist agents\nwork simultaneously on\ndifferent sub-tasks.\nResults consolidated.",           BLUE),
    (11.5, "Hierarchical\n(Orchestrated)", "A lead orchestrator agent\ndelegates to specialist\nagents. Most powerful\nfor complex tasks.",    NAVY),
]
for (x, label, desc, colour) in arch_types:
    box = FancyBboxPatch((x - 1.7, 0.4), 3.4, 2.45,
                         boxstyle="round,pad=0.10", facecolor=colour,
                         edgecolor="none", alpha=0.88, zorder=2)
    ax.add_patch(box)
    ax.text(x, 2.4, label, ha="center", va="center",
            fontsize=11, fontweight="bold", color=WHITE, zorder=3, multialignment="center")
    ax.text(x, 1.35, desc, ha="center", va="center",
            fontsize=10, color=LGRAY, zorder=3, multialignment="center")
    ax.plot([x, x], [3.25, 2.88], color=MGRAY, lw=1.4)

for x_div in [4.5, 9.5]:
    ax.plot([x_div, x_div], [0.3, 3.05], color=MGRAY, lw=0.8, ls="--", alpha=0.5)

plt.savefig(FIG_DIR / "fig3_autonomy_spectrum.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 3 done")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Tech Stack (layered architecture)
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(13, 9), facecolor=WHITE)
ax = fig.add_axes([0.04, 0.04, 0.92, 0.90])
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

ax.text(5, 9.6, "Figure 4: The Agentic AI Technology Stack",
        ha="center", va="center", fontsize=14, fontweight="bold", color=NAVY)
ax.text(5, 9.18, "Five layers that work together — explained without jargon",
        ha="center", va="center", fontsize=11, color=STEEL)

layers = [
    # (y_bottom, height, layer_label, sublabel, description, colour)
    (0.25, 1.25, "LAYER 1: DATA & TOOLS",              "The Hands",
     "All external systems the agent can access: transaction databases, regulatory\n"
     "filings, CRM platforms, trading APIs, email, calendar, and web browsers.",
     "#1A3A5C"),
    (1.65, 1.25, "LAYER 2: MEMORY",                    "The Filing Cabinet",
     "Short-term memory holds task context. Long-term memory stores learned facts,\n"
     "institutional knowledge, and past interaction history for reuse across tasks.",
     STEEL),
    (3.05, 1.25, "LAYER 3: REASONING ENGINE (LLM)",   "The Brain",
     "A Large Language Model (e.g. GPT-4, Claude, Gemini) reads the situation and\n"
     "decides what to do next. This is the core intelligence powering the agent.",
     BLUE),
    (4.45, 1.25, "LAYER 4: PLANNING & ORCHESTRATION", "The Project Manager",
     "Breaks goals into ordered steps, routes work to sub-agents or tools, monitors\n"
     "progress, and handles exceptions — acting as the operational nerve centre.",
     "#1050A0"),
    (5.85, 1.25, "LAYER 5: TASK INTERFACE",            "The Front Door",
     "How instructions arrive: a user chat, an automated trigger, a system event,\n"
     "a scheduled run, or another agent passing a delegated sub-task.",
     NAVY),
]

for (yb, h, label, sublabel, desc, colour) in layers:
    indent = (5.85 - yb) * 0.06
    box = FancyBboxPatch((0.25 + indent * 0.5, yb), 9.5 - indent, h - 0.1,
                         boxstyle="round,pad=0.05", facecolor=colour,
                         edgecolor="none", alpha=0.96, zorder=2)
    ax.add_patch(box)
    ax.text(0.60 + indent * 0.5, yb + h * 0.72, label,
            ha="left", va="center", fontsize=11, fontweight="bold", color=WHITE, zorder=3)
    ax.text(9.62 - indent * 0.5, yb + h * 0.72, f"({sublabel})",
            ha="right", va="center", fontsize=11, color=LGRAY, style="italic", zorder=3)
    ax.text(0.60 + indent * 0.5, yb + h * 0.28, desc,
            ha="left", va="center", fontsize=10, color=MGRAY, zorder=3)

# flow arrow
ax.annotate("", xy=(9.88, 5.95), xytext=(9.88, 1.55),
            arrowprops=dict(arrowstyle="<->", color=MGRAY, lw=1.8))
ax.text(9.96, 3.75, "Information\nFlow", ha="left", va="center",
        fontsize=9, color=MGRAY, rotation=90)

# analogy box
ax.text(5, 8.35,
        '"Think of it as a bank\'s operations centre: the Front Door receives the brief, the Project Manager\n'
        'allocates work, the Brain makes decisions, the Filing Cabinet holds context, and the Hands execute."',
        ha="center", va="center", fontsize=11, color=STEEL, style="italic",
        bbox=dict(facecolor=LGRAY, edgecolor=MGRAY, boxstyle="round,pad=0.45"))

plt.savefig(FIG_DIR / "fig4_tech_stack.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 4 done")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Risk Heat Map
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 9), facecolor=WHITE)
ax.set_facecolor(WHITE)

n = 5
colours = []
for i in range(n):
    row = []
    for j in range(n):
        score = (i + j) / (2 * (n - 1))
        if score < 0.35:   row.append("#C8E6C9")
        elif score < 0.60: row.append("#FFF9C4")
        elif score < 0.80: row.append("#FFCC80")
        else:               row.append("#EF9A9A")
    colours.append(row)

for i in range(n):
    for j in range(n):
        rect = FancyBboxPatch((j, i), 0.94, 0.94,
                              boxstyle="round,pad=0.04",
                              facecolor=colours[i][j], edgecolor=WHITE, linewidth=2)
        ax.add_patch(rect)

risks = [
    (0.5, 0.5, "Data Privacy\nBreach"),
    (0.5, 2.5, "Vendor\nLock-in"),
    (1.5, 1.5, "Model Bias\n& Fairness"),
    (2.5, 0.5, "Talent\nShortage"),
    (2.5, 2.5, "Operational\nDisruption"),
    (1.5, 3.5, "Regulatory\nNon-compliance"),
    (2.5, 4.5, "Auditability\nGap"),
    (3.5, 3.5, "Hallucination /\nError Propagation"),
    (4.5, 3.5, "Autonomous\nAction Risk"),
    (4.5, 4.5, "Systemic\nFailure"),
]
for (x, y, label) in risks:
    ax.text(x, y, label, ha="center", va="center", fontsize=10,
            fontweight="bold", color="#1A1A1A", multialignment="center")

ax.set_xlim(0, 5); ax.set_ylim(0, 5)
ax.set_xticks([0.47, 1.47, 2.47, 3.47, 4.47])
ax.set_xticklabels(["Very Low", "Low", "Medium", "High", "Very High"], fontsize=11)
ax.set_yticks([0.47, 1.47, 2.47, 3.47, 4.47])
ax.set_yticklabels(["Very Low", "Low", "Medium", "High", "Very High"], fontsize=11)
ax.set_xlabel("LIKELIHOOD OF OCCURRENCE", fontsize=12, fontweight="bold", color=NAVY, labelpad=10)
ax.set_ylabel("SEVERITY OF IMPACT", fontsize=12, fontweight="bold", color=NAVY, labelpad=10)
ax.tick_params(color=MGRAY, length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

legend_items = [
    mpatches.Patch(facecolor="#C8E6C9", edgecolor=MGRAY, label="Low Risk"),
    mpatches.Patch(facecolor="#FFF9C4", edgecolor=MGRAY, label="Medium Risk"),
    mpatches.Patch(facecolor="#FFCC80", edgecolor=MGRAY, label="High Risk"),
    mpatches.Patch(facecolor="#EF9A9A", edgecolor=MGRAY, label="Critical Risk"),
]
ax.legend(handles=legend_items, loc="lower right", fontsize=11,
          framealpha=0.9, edgecolor=MGRAY)

ax.set_title(
    "Figure 5: Agentic AI Risk Heat Map — Banking Sector\n"
    "Key risks plotted by likelihood of occurrence and severity of impact",
    fontsize=13, fontweight="bold", color=NAVY, pad=13,
)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig5_risk_heatmap.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 5 done")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Strategic Timeline (3 horizons)
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 9), facecolor=WHITE)
ax = fig.add_axes([0.02, 0.06, 0.96, 0.88])
ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")

ax.text(8, 9.6, "Figure 6: Agentic AI Strategic Timeline for Banking",
        ha="center", va="center", fontsize=14, fontweight="bold", color=NAVY)
ax.text(8, 9.15, "Three planning horizons for senior banking leaders",
        ha="center", va="center", fontsize=11, color=STEEL)

horizons = [
    (0.3, 4.7, "NOW — 2026\nFoundation & Pilots", STEEL, [
        "Agentic compliance\n& KYC workflows",
        "Human-in-the-loop\nloan pre-screening",
        "AI coding assistants\nin technology teams",
        "Model risk framework\ndevelopment",
        "Regulatory guidance\nbeing published",
        "Workforce upskilling\nprogrammes begin",
    ]),
    (5.7, 4.7, "2027 — 2028\nScale & Integration", BLUE, [
        "Autonomous trade\nmonitoring & alerts",
        "Multi-agent fraud\ndetection networks",
        "Agentic wealth advisory\n(mass-affluent segment)",
        "Industry governance\nstandards established",
        "Cross-bank agentic\ninteroperability trials",
        "Regulator sandbox\nprogrammes live",
    ]),
    (11.1, 4.7, "2029 — 2031\nTransformation", NAVY, [
        "Autonomous loan\norigination at scale",
        "AI-to-AI financial\nmarket interactions",
        "Agentic treasury\n& CFO functions",
        "New regulatory\nregimes in force",
        "Competitive landscape\nfundamentally reset",
        "Human roles shift to\nstrategic oversight",
    ]),
]

for (x, w, label, colour, items) in horizons:
    # header
    hdr = FancyBboxPatch((x, 7.5), w, 1.2,
                         boxstyle="round,pad=0.07", facecolor=colour, edgecolor="none", zorder=2)
    ax.add_patch(hdr)
    ax.text(x + w / 2, 8.12, label,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=WHITE, zorder=3, multialignment="center")
    # items
    for k, item in enumerate(items):
        ypos = 7.0 - k * 1.07
        dot = plt.Circle((x + 0.27, ypos + 0.14), 0.08, color=colour, zorder=3)
        ax.add_patch(dot)
        ax.text(x + 0.52, ypos + 0.14, item,
                ha="left", va="center", fontsize=10,
                color="#1A1A1A", zorder=3, multialignment="left")

# timeline bar
ax.plot([0.3, 15.7], [0.6, 0.6], color=MGRAY, lw=2.5, zorder=1)
for x_mark, label in [(0.3, "Today\n2026"), (5.8, "2027"), (11.2, "2029"), (15.7, "2031+")]:
    ax.plot(x_mark, 0.6, "o", color=NAVY, ms=10, zorder=2)
    ax.text(x_mark, 0.24, label,
            ha="center", va="center", fontsize=10,
            color=NAVY, fontweight="bold", multialignment="center")

for x_div in [5.55, 10.95]:
    ax.plot([x_div, x_div], [0.78, 9.0], color=MGRAY, lw=1.2, ls="--", alpha=0.55)

plt.savefig(FIG_DIR / "fig6_strategic_timeline.png", dpi=160, bbox_inches="tight", facecolor=WHITE)
plt.close()
print("Fig 6 done")
print("\nAll figures regenerated with minimum 11pt fonts.")
