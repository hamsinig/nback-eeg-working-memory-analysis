import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from pathlib import Path

# ---------------------------------------------------------
# INPUT FILE
# ---------------------------------------------------------
# Uses the same participant_level_results.csv as Figure 4.
#
# Required columns:
# participant, alpha_2back, alpha_4back,
# accuracy_2back, accuracy_4back
# ---------------------------------------------------------

FILE = Path("participant_level_results.csv")

if not FILE.exists():
    raise FileNotFoundError(
        "participant_level_results.csv was not found. "
        "Put it in the same folder as this script."
    )

df = pd.read_csv(FILE)

required = {
    "participant",
    "alpha_2back",
    "alpha_4back",
    "accuracy_2back",
    "accuracy_4back",
}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

df["alpha_change"] = df["alpha_4back"] - df["alpha_2back"]
df["accuracy_change"] = df["accuracy_4back"] - df["accuracy_2back"]

rho, p = spearmanr(df["alpha_change"], df["accuracy_change"])

fig, ax = plt.subplots(figsize=(6.5, 5))

ax.scatter(
    df["alpha_change"],
    df["accuracy_change"],
    s=55,
    alpha=0.8
)

# Label individual participants.
for _, row in df.iterrows():
    ax.annotate(
        str(row["participant"]),
        (row["alpha_change"], row["accuracy_change"]),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8
    )

ax.axhline(0, linewidth=0.8, linestyle="--")
ax.axvline(0, linewidth=0.8, linestyle="--")

ax.set_xlabel("Alpha change (4-back − 2-back)")
ax.set_ylabel("Accuracy change (4-back − 2-back)")
ax.set_title("Alpha change vs behavioral change")
ax.grid(alpha=0.2)

ax.text(
    0.03, 0.97,
    f"Spearman ρ = {rho:.4f}\np = {p:.3f}",
    transform=ax.transAxes,
    ha="left", va="top", fontsize=10
)

plt.tight_layout()
plt.savefig("Figure_6_alpha_behavior_scatter.png", dpi=300, bbox_inches="tight")
plt.show()
