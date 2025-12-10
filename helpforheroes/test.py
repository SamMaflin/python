import pandas as pd
import matplotlib.pyplot as plt

# Your DataFrame
df = pd.DataFrame(
    {
        "Low Activity": [
            '"Dormant Base"',
            '"At-Risk Decliners"',
            '"One-Off Premiums"'
        ],
        "Mid Activity": [
            '"Steady Low-Spend"',
            '"Developing Value"',
            '"Loyal Value"'
        ],
        "High Activity": [
            '"Engaged Low-Spend"',
            '"Premium Regulars"',
            '"Premium Loyalists"'
        ],
    },
    index=["Low", "Mid", "High"]
)

# Color matrix aligned so LOW–LOW is bottom-left
color_matrix = [
    ["#ff0011", "#ff9999", "#ffff66"],  
    ["#ff9999", "#ffff66", "#b6e6b6"],  
    ["#ffff66", "#b6e6b6", "#13DA48"],  
]

fig, ax = plt.subplots(figsize=(8, 6))

# Draw rectangles + labels (BOLD text)
for i, row in enumerate(df.index):
    for j, col in enumerate(df.columns):
        ax.add_patch(
            plt.Rectangle(
                (j, i), 1, 1,
                facecolor=color_matrix[i][j],
                edgecolor="black"
            )
        )
        ax.text(
            j + 0.5,
            i + 0.5,
            df.loc[row, col],
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            wrap=True
        )

# ---- TICKS: KEEP LABELS, REMOVE MARKS ----
ax.set_xticks([0.5, 1.5, 2.5])
ax.set_xticklabels(["Low", "Mid", "High"], fontsize=10, fontweight="bold")

ax.set_yticks([0.5, 1.5, 2.5])
ax.set_yticklabels(["Low", "Mid", "High"], rotation=90, va="center",
                   fontsize=10, fontweight="bold")

ax.tick_params(axis="both", length=0)
ax.tick_params(axis="x", pad=9)
ax.tick_params(axis="y", pad=9)

plt.gca().invert_yaxis()

ax.set_xlabel("Activity Score (Percentile Rank)", labelpad=20, fontsize=10, fontweight="bold")
ax.set_ylabel("Spend Score (Percentile Rank)", labelpad=30, fontsize=10, fontweight="bold")

ax.set_xlim(0, 3)
ax.set_ylim(0, 3)
ax.set_aspect("equal")

plt.tight_layout()

# ⭐ SAVE THE IMAGE HERE ⭐
plt.savefig("helpforheroes/matrix_plot.png", dpi=300, bbox_inches='tight')

plt.show()
