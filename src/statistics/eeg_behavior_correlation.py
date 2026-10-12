import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD EEG DATA
# ============================================================

eeg = pd.read_csv(
    "final_preprocessed/PSD_participant_condition_logratio.csv"
)

# Keep only 2-back and 4-back
eeg_24 = eeg[
    eeg["condition"].isin(["2-back", "4-back"])
].copy()

# Put 2-back and 4-back into separate columns
eeg_wide = eeg_24.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)

# Calculate alpha change:
# 4-back minus 2-back
eeg_wide["delta_alpha"] = (
    eeg_wide["4-back"] - eeg_wide["2-back"]
)


# ============================================================
# 2. LOAD BEHAVIORAL DATA
# ============================================================

behavior = pd.read_csv(
    "final_preprocessed/behavioral_audit_summary.csv"
)

# Keep only 2-back and 4-back
behavior_24 = behavior[
    behavior["condition"].isin(["2-back", "4-back"])
].copy()

# Put 2-back and 4-back into separate columns
#
# IMPORTANT:
# The behavioral file uses "accuracy_mean",
# not "accuracy".
behavior_wide = behavior_24.pivot(
    index="subject",
    columns="condition",
    values="accuracy_mean"
)

# Calculate behavioral change:
# 4-back minus 2-back
behavior_wide["delta_accuracy"] = (
    behavior_wide["4-back"] - behavior_wide["2-back"]
)


# ============================================================
# 3. COMBINE EEG + BEHAVIOR
# ============================================================

combined = eeg_wide[
    ["delta_alpha"]
].join(
    behavior_wide[
        ["delta_accuracy"]
    ],
    how="inner"
)

# Remove any missing values, just in case
combined = combined.dropna()


print()
print("=" * 70)
print("EEG-BEHAVIOR ASSOCIATION")
print("=" * 70)

print("\nParticipant-level data:")
print(combined)

print("\nNumber of participants:", len(combined))


# ============================================================
# 4. SPEARMAN CORRELATION
# ============================================================

rho, p_value = spearmanr(
    combined["delta_alpha"],
    combined["delta_accuracy"]
)

print()
print("=" * 70)
print("SPEARMAN CORRELATION")
print("=" * 70)

print(f"\nSpearman rho = {rho:.4f}")
print(f"p-value      = {p_value:.6f}")


# ============================================================
# 5. SAVE PARTICIPANT-LEVEL DATA
# ============================================================

combined.to_csv(
    "final_preprocessed/alpha_behavior_correlation.csv"
)

print()
print("Saved:")
print("  final_preprocessed/alpha_behavior_correlation.csv")


# ============================================================
# 6. CREATE SCATTER PLOT
# ============================================================

plt.figure(figsize=(7, 5))

plt.scatter(
    combined["delta_alpha"],
    combined["delta_accuracy"]
)

# Reference lines showing no change
plt.axhline(
    0,
    linestyle="--"
)

plt.axvline(
    0,
    linestyle="--"
)

plt.xlabel(
    "Alpha change (4-back − 2-back)"
)

plt.ylabel(
    "Accuracy change (4-back − 2-back)"
)

plt.title(
    f"Alpha change vs behavioral change\n"
    f"Spearman ρ = {rho:.2f}, p = {p_value:.4f}"
)

plt.tight_layout()

plt.savefig(
    "final_preprocessed/alpha_behavior_correlation.png",
    dpi=300
)

plt.show()

print(
    "  final_preprocessed/alpha_behavior_correlation.png"
)

print()
print("=" * 70)
print("DONE")
print("=" * 70)
