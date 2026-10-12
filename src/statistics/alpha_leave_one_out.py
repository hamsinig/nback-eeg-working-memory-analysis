import pandas as pd
from scipy.stats import wilcoxon

FILE = "final_preprocessed/PSD_participant_condition_logratio.csv"

df = pd.read_csv(FILE)

wide = df.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)

wide = wide[["2-back", "4-back"]].dropna()

results = []

participants = wide.index.tolist()

for participant in participants:

    reduced = wide.drop(index=participant)

    stat, p = wilcoxon(
        reduced["2-back"],
        reduced["4-back"],
        alternative="two-sided"
    )

    difference = (
        reduced["4-back"] -
        reduced["2-back"]
    )

    results.append({
        "removed_participant": participant,
        "n": len(reduced),
        "wilcoxon_W": stat,
        "p_value": p,
        "mean_difference": difference.mean(),
        "median_difference": difference.median()
    })


results_df = pd.DataFrame(results)

results_df = results_df.sort_values("p_value")

print("=" * 80)
print("LEAVE-ONE-PARTICIPANT-OUT SENSITIVITY ANALYSIS")
print("=" * 80)

print()
print(results_df.to_string(index=False))

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    "Minimum p-value:",
    results_df["p_value"].min()
)

print(
    "Maximum p-value:",
    results_df["p_value"].max()
)

print(
    "Number of leave-one-out analyses with p < 0.05:",
    (results_df["p_value"] < 0.05).sum(),
    "/",
    len(results_df)
)

print()
print("Most influential participant:")
print(
    results_df.loc[
        results_df["p_value"].idxmax()
    ].to_string()
)

output = (
    "final_preprocessed/"
    "alpha_leave_one_out_sensitivity.csv"
)

results_df.to_csv(
    output,
    index=False
)

print()
print("Saved:")
print(output)
