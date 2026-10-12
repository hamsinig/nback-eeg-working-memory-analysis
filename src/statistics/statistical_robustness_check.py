import pandas as pd
from scipy.stats import friedmanchisquare


# ============================================================
# LOAD PARTICIPANT-LEVEL DATA
# ============================================================

FILE = (
    "final_preprocessed/"
    "PSD_participant_condition_logratio.csv"
)

df = pd.read_csv(FILE)


# ============================================================
# CONDITION ORDER
# ============================================================

conditions = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]


# ============================================================
# BANDS
# ============================================================

bands = {
    "theta": "theta_log_ratio",
    "alpha": "alpha_log_ratio",
    "beta": "beta_log_ratio"
}


# ============================================================
# FRIEDMAN TEST
# ============================================================

print("\n" + "=" * 80)
print("FRIEDMAN REPEATED-MEASURES TEST")
print("=" * 80)


results = []


for band_name, column in bands.items():

    # Convert to participant × condition matrix
    wide = df.pivot(
        index="subject",
        columns="condition",
        values=column
    )

    # Make sure conditions are in the correct order
    wide = wide[conditions]

    statistic, p_value = friedmanchisquare(
        wide["1-back"],
        wide["2-back"],
        wide["3-back"],
        wide["4-back"]
    )

    results.append({
        "band": band_name,
        "chi_square": statistic,
        "p": p_value
    })

    print("\n" + "-" * 60)
    print(band_name.upper())
    print("-" * 60)

    print(f"Friedman statistic = {statistic:.4f}")
    print(f"p-value = {p_value:.6f}")


# ============================================================
# SUMMARY
# ============================================================

results_df = pd.DataFrame(results)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    results_df.to_string(index=False)
)


# ============================================================
# MULTIPLE-COMPARISON CORRECTION
# ============================================================

print("\n" + "=" * 80)
print("MULTIPLE-TEST THRESHOLD")
print("=" * 80)

print("Number of frequency bands tested: 3")
print("Bonferroni alpha = 0.05 / 3")
print("Bonferroni alpha =", 0.05 / 3)


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "friedman_test_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)
