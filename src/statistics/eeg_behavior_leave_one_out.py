import pandas as pd
from scipy.stats import spearmanr


# ============================================================
# 1. LOAD PARTICIPANT-LEVEL EEG + BEHAVIOR DATA
# ============================================================

data = pd.read_csv(
    "final_preprocessed/alpha_behavior_correlation.csv"
)

# Make sure there are no missing values
data = data.dropna(
    subset=["delta_alpha", "delta_accuracy"]
).copy()

print()
print("=" * 70)
print("EEG-BEHAVIOR LEAVE-ONE-OUT SENSITIVITY ANALYSIS")
print("=" * 70)

print("\nTotal participants:", len(data))


# ============================================================
# 2. ORIGINAL CORRELATION
# ============================================================

rho_original, p_original = spearmanr(
    data["delta_alpha"],
    data["delta_accuracy"]
)

print()
print("Original correlation:")
print(f"rho = {rho_original:.4f}")
print(f"p   = {p_original:.6f}")


# ============================================================
# 3. LEAVE-ONE-OUT ANALYSIS
# ============================================================

results = []

subjects = data["subject"].tolist()

for subject in subjects:

    # Remove one participant
    subset = data[
        data["subject"] != subject
    ].copy()

    # Calculate Spearman correlation
    rho, p_value = spearmanr(
        subset["delta_alpha"],
        subset["delta_accuracy"]
    )

    results.append({
        "removed_subject": subject,
        "n_participants": len(subset),
        "spearman_rho": rho,
        "p_value": p_value
    })


# ============================================================
# 4. CREATE RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)

# Sort by correlation strength
results_df = results_df.sort_values(
    "spearman_rho"
)

print()
print("=" * 70)
print("LEAVE-ONE-OUT RESULTS")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 5. SUMMARY
# ============================================================

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(
    f"\nOriginal rho = {rho_original:.4f}"
)

print(
    f"Leave-one-out rho range: "
    f"{results_df['spearman_rho'].min():.4f} "
    f"to "
    f"{results_df['spearman_rho'].max():.4f}"
)

print(
    f"Leave-one-out p-value range: "
    f"{results_df['p_value'].min():.6f} "
    f"to "
    f"{results_df['p_value'].max():.6f}"
)

significant_count = (
    results_df["p_value"] < 0.05
).sum()

print(
    f"\nLeave-one-out analyses with p < .05: "
    f"{significant_count}/{len(results_df)}"
)


# ============================================================
# 6. SAVE RESULTS
# ============================================================

output_file = (
    "final_preprocessed/"
    "alpha_behavior_leave_one_out.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print()
print("Saved:")
print(f"  {output_file}")

print()
print("=" * 70)
print("DONE")
print("=" * 70)
