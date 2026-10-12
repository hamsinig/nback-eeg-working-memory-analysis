import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


# ============================================================
# LOAD DATA
# ============================================================

FILE = (
    "final_preprocessed/"
    "PSD_participant_condition_logratio.csv"
)

df = pd.read_csv(FILE)


# ============================================================
# MAKE PARTICIPANT × CONDITION MATRIX
# ============================================================

wide = df.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)


conditions = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

wide = wide[conditions]


# ============================================================
# PAIRWISE COMPARISONS
# ============================================================

comparisons = [
    ("1-back", "2-back"),
    ("1-back", "3-back"),
    ("1-back", "4-back"),
    ("2-back", "3-back"),
    ("2-back", "4-back"),
    ("3-back", "4-back")
]


results = []


print("\n" + "=" * 80)
print("ALPHA POST-HOC WILCOXON TESTS")
print("=" * 80)


for condition_a, condition_b in comparisons:

    statistic, p_value = wilcoxon(
        wide[condition_a],
        wide[condition_b],
        alternative="two-sided"
    )

    results.append({
        "comparison": f"{condition_a} vs {condition_b}",
        "W": statistic,
        "p_raw": p_value
    })


# ============================================================
# MULTIPLE-COMPARISON CORRECTION
# ============================================================

p_values = [
    result["p_raw"]
    for result in results
]


reject, p_corrected, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method="bonferroni"
)


for i, result in enumerate(results):

    result["p_bonferroni"] = p_corrected[i]
    result["significant"] = reject[i]


# ============================================================
# DISPLAY
# ============================================================

results_df = pd.DataFrame(results)


print(
    results_df.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "alpha_posthoc_wilcoxon.csv"
)

results_df.to_csv(
    output_file,
    index=False
)


print("\nSaved:")
print(output_file)
