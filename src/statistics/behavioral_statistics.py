import pandas as pd
from scipy.stats import friedmanchisquare
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

FILE = "final_preprocessed/behavioral_audit_summary.csv"

df = pd.read_csv(FILE)

# ---------------------------------------------------------
# Participant × condition accuracy matrix
# ---------------------------------------------------------

wide = df.pivot(
    index="subject",
    columns="condition",
    values="accuracy_mean"
)

conditions = ["1-back", "2-back", "3-back", "4-back"]

wide = wide[conditions].dropna()

print("=" * 75)
print("BEHAVIORAL ACCURACY ANALYSIS")
print("=" * 75)

print()
print("Participants:", len(wide))

print()
print("Mean accuracy by condition:")
print(wide.mean().to_string())

print()
print("Median accuracy by condition:")
print(wide.median().to_string())

# ---------------------------------------------------------
# Friedman test
# ---------------------------------------------------------

stat, p = friedmanchisquare(
    wide["1-back"],
    wide["2-back"],
    wide["3-back"],
    wide["4-back"]
)

print()
print("=" * 75)
print("FRIEDMAN TEST")
print("=" * 75)

print(f"Friedman statistic = {stat:.4f}")
print(f"p-value = {p:.6f}")

# ---------------------------------------------------------
# Kendall's W
# ---------------------------------------------------------

n = len(wide)
k = len(conditions)

kendalls_w = stat / (n * (k - 1))

print(f"Kendall's W = {kendalls_w:.4f}")

# ---------------------------------------------------------
# Post-hoc tests
# ---------------------------------------------------------

comparisons = [
    ("1-back", "2-back"),
    ("1-back", "3-back"),
    ("1-back", "4-back"),
    ("2-back", "3-back"),
    ("2-back", "4-back"),
    ("3-back", "4-back")
]

results = []

for a, b in comparisons:

    W, p_raw = wilcoxon(
        wide[a],
        wide[b],
        alternative="two-sided"
    )

    results.append({
        "comparison": f"{a} vs {b}",
        "W": W,
        "p_raw": p_raw
    })

results_df = pd.DataFrame(results)

# Bonferroni correction
reject, p_corrected, _, _ = multipletests(
    results_df["p_raw"],
    alpha=0.05,
    method="bonferroni"
)

results_df["p_bonferroni"] = p_corrected
results_df["significant"] = reject

print()
print("=" * 75)
print("POST-HOC WILCOXON TESTS")
print("=" * 75)

print(results_df.to_string(index=False))

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

output = (
    "final_preprocessed/"
    "behavioral_statistics.csv"
)

results_df.to_csv(output, index=False)

print()
print("Saved:")
print(output)
