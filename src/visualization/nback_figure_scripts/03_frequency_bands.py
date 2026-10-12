import matplotlib.pyplot as plt

conditions = ["1-back", "2-back", "3-back", "4-back"]

values = {
    "Theta":  [0.0000, -0.0395, -0.0054,  0.0107],
    "Alpha":  [0.0000, -0.1124, -0.0642,  0.0362],
    "Beta":   [0.0000, -0.0454,  0.0188,  0.0513],
}

fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)

for ax, (band, y) in zip(axes, values.items()):
    ax.plot(conditions, y, marker="o", linewidth=2)
    ax.axhline(0, linewidth=0.8, linestyle="--")
    ax.set_title(f"{band} ({ {'Theta':'4–8 Hz','Alpha':'8–13 Hz','Beta':'13–30 Hz'}[band] })")
    ax.set_xlabel("N-back condition")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=20)

axes[0].set_ylabel("Mean log-ratio power")
fig.suptitle("EEG band-power changes across N-back conditions", fontsize=14)
plt.tight_layout()

plt.savefig("Figure_3_frequency_band_changes.png", dpi=300, bbox_inches="tight")
plt.show()
