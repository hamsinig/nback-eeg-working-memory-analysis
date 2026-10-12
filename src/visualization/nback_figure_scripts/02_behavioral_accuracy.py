import matplotlib.pyplot as plt

conditions = ["1-back", "2-back", "3-back", "4-back"]
accuracy = [43.5, 61.7, 73.9, 69.6]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(conditions, accuracy, marker="o", linewidth=2)
ax.set_xlabel("N-back condition")
ax.set_ylabel("Mean accuracy (%)")
ax.set_title("Behavioral accuracy across N-back conditions")
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)

for x, y in zip(conditions, accuracy):
    ax.annotate(f"{y:.1f}%", (x, y), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=10)

plt.tight_layout()
plt.savefig("Figure_2_behavioral_accuracy.png", dpi=300, bbox_inches="tight")
plt.show()
