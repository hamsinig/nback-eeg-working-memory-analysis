import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

FILE = "final_preprocessed/PSD_participant_condition_logratio.csv"

df = pd.read_csv(FILE)

# ---------------------------------------------------------
# 1. Kendall's W for Friedman tests
# ---------------------------------------------------------

n = df["subject"].nunique()
k = df["condition"].nunique()

friedman_stats = {
    "theta": 0.6000,
    "alpha": 17.6667,
    "beta": 8.6667
}

print("=" * 70)
print("FRIEDMAN EFFECT SIZES — KENDALL'S W")
print("=" * 70)

for band, chi2 in friedman_stats.items():

    W = chi2 / (n * (k - 1))

    print(f"{band.upper()}")
    print(f"Chi-square = {chi2:.4f}")
    print(f"Kendall's W = {W:.4f}")
    print()

# ---------------------------------------------------------
# 2. Alpha: 2-back vs 4-back paired effect
# ---------------------------------------------------------

wide = df.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)

x = wide["2-back"]
y = wide["4-back"]

difference = y - x

# Wilcoxon statistic
W_stat, p = wilcoxon(x, y)

# Rank-biserial correlation
# Based on absolute non-zero paired differences
nonzero = difference[difference != 0]

abs_diff = nonzero.abs()
ranks = abs_diff.rank()

positive_rank_sum = ranks[nonzero > 0].sum()
negative_rank_sum = ranks[nonzero < 0].sum()

rank_biserial = (
    positive_rank_sum - negative_rank_sum
) / (positive_rank_sum + negative_rank_sum)

print("=" * 70)
print("ALPHA — 2-BACK VS 4-BACK EFFECT SIZE")
print("=" * 70)

print(f"Participants = {n}")
print(f"Wilcoxon W = {W_stat:.1f}")
print(f"Raw p = {p:.6f}")
print(f"Rank-biserial correlation = {rank_biserial:.4f}")

print()
print("Descriptive statistics:")
print(f"2-back mean = {x.mean():.6f}")
print(f"4-back mean = {y.mean():.6f}")
print(f"Mean paired difference (4-back - 2-back) = {difference.mean():.6f}")
print(f"Median paired difference = {difference.median():.6f}")

# ---------------------------------------------------------
# 3. Save results
# ---------------------------------------------------------

results = []

for band, chi2 in friedman_stats.items():
    W = chi2 / (n * (k - 1))
    results.append({
        "band": band,
        "friedman_chi2": chi2,
        "kendalls_W": W
    })

effect_df = pd.DataFrame(results)

effect_df.to_csv(
    "final_preprocessed/friedman_effect_sizes.csv",
    index=False
)

pairwise = pd.DataFrame([{
    "band": "alpha",
    "comparison": "2-back vs 4-back",
    "wilcoxon_W": W_stat,
    "p_raw": p,
    "rank_biserial": rank_biserial,
    "mean_difference_4back_minus_2back": difference.mean(),
    "median_difference_4back_minus_2back": difference.median()
}])

pairwise.to_csv(
    "final_preprocessed/alpha_2back_vs_4back_effect_size.csv",
    index=False
)

print()
print("Saved:")
print("final_preprocessed/friedman_effect_sizes.csv")
print("final_preprocessed/alpha_2back_vs_4back_effect_size.csv")
