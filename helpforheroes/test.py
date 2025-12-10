import matplotlib.pyplot as plt

# Labels inside the matrix (optional)
labels = [
    ["Pale Green", "Medium Green", "Strong Green"],  # High health
    ["Light Red",  "Yellow",       "Pale Green"],    # Medium health
    ["Strong Red", "Light Red",    "Yellow"]         # Low health
]

# Matching colors
colors = [
    ["#b6e6b6", "#66cc66", "#009900"],  # pale, medium, strong green
    ["#ff9999", "#ffff66", "#b6e6b6"],  # light red, yellow, pale green
    ["#cc0000", "#ff9999", "#ffff66"]   # strong red, light red, yellow
]

fig, ax = plt.subplots(figsize=(6, 6))

# Draw each cell
for i in range(3):
    for j in range(3):
        ax.add_patch(plt.Rectangle((j, i), 1, 1,
                                   facecolor=colors[2 - i][j],
                                   edgecolor="black"))
        ax.text(j + 0.5, i + 0.5, labels[2 - i][j],
                ha='center', va='center', fontsize=11)

# Axes
ax.set_xticks([0.5, 1.5, 2.5])
ax.set_xticklabels(["Low", "Medium", "High"])
ax.set_yticks([0.5, 1.5, 2.5])
ax.set_yticklabels(["Low", "Medium", "High"])

ax.set_xlabel("Carbon footprint")
ax.set_ylabel("Health effect")

ax.set_xlim(0, 3)
ax.set_ylim(0, 3)
ax.set_aspect("equal")

plt.tight_layout()
plt.show()
