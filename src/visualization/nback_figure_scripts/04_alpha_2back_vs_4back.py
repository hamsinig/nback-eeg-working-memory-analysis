import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# INPUT FILE
# ---------------------------------------------------------
# Create a CSV named participant_level_results.csv.
#
# Required columns:
# participant, alpha_2back, alpha_4back
#
# Optional columns that are not needed for this figure:
# accuracy_2back, accuracy_4back
# ---------------------------------------------------------

FILE = Path("participant_level_results.csv")

if not FILE.exists():
    raise FileNotFoundError(
        "participant_level_results.csv was not found. "
        "Put it in the same folder as this script."
    )

df = pd.read_csv(FILE)

required = {"participant", "alpha_2back", "alpha_4back"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

df = df.sort_values("participant").reset_index(drop=True)

fig, ax = plt.subplots(figsize=(7, 5))

for _, row in df.iterrows():
    ax.plot(
        ["2-back", "4-back"],
        [row["alpha_2back"], row["alpha_4back"]],
        marker="o",
        linewidth=1.2,
        alpha=0.65
    )

ax.axhline(0, linewidth=0.8, linestyle="--")
ax.set_ylabel("Alpha log-ratio power")
ax.set_title("Participant-level alpha change: 2-back vs 4-back")
ax.grid(axis="y", alpha=0.25)

ax.text(
    0.98, 0.03,
    "Wilcoxon: adjusted p = .0116\n16/18 participants increased",
    transform=ax.transAxes,
    ha="right", va="bottom", fontsize=9
)

plt.tight_layout()
plt.savefig("Figure_4_alpha_2back_vs_4back.png", dpi=300, bbox_inches="tight")
plt.show()
