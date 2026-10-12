import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

steps = [
    "Raw continuous EEG\n19 scalp channels, 250 Hz",
    "Scaling correction\n+ 10–20 montage",
    "1–40 Hz band-pass filter",
    "ICA artifact correction",
    "Event selection\n+ tutorial exclusion",
    "Epoching\n−0.2 to 1.0 s",
    "Epoch-level artifact rejection\n7,177 retained epochs",
    "Welch PSD\n0–1 s post-stimulus",
    "Theta / Alpha / Beta\nband-power extraction",
    "Log-ratio normalization\nrelative to 1-back",
    "Participant-level\nstatistical analysis",
]

fig, ax = plt.subplots(figsize=(8, 14))
ax.set_xlim(0, 1)
ax.set_ylim(0, len(steps))
ax.axis("off")

for i, step in enumerate(steps):
    y = len(steps) - i - 0.8
    box = FancyBboxPatch(
        (0.18, y - 0.22), 0.64, 0.44,
        boxstyle="round,pad=0.02",
        linewidth=1.2,
        edgecolor="black",
        facecolor="white"
    )
    ax.add_patch(box)
    ax.text(0.5, y, step, ha="center", va="center", fontsize=11)
    if i < len(steps) - 1:
        ax.annotate(
            "", xy=(0.5, y - 0.36), xytext=(0.5, y - 0.52),
            arrowprops=dict(arrowstyle="->", lw=1.2)
        )

ax.set_title("EEG preprocessing and spectral analysis pipeline", fontsize=14, pad=18)
plt.tight_layout()
plt.savefig("Figure_1_EEG_analysis_pipeline.png", dpi=300, bbox_inches="tight")
plt.show()
