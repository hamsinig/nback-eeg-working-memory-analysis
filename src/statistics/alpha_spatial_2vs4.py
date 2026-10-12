import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

FILE = "final_preprocessed/PSD_log_ratio_from_1back.csv"

df = pd.read_csv(FILE)

channels = sorted(df["channel"].unique())

results = []

for channel in channels:

    channel_df = df[df["channel"] == channel]

    wide = channel_df.pivot(
        index="subject",
        columns="condition",
        values="alpha_log_ratio"
    )

    # Keep only participants with both conditions
    wide = wide[["2-back", "4-back"]].dropna()

    stat, p = wilcoxon(
        wide["2-back"],
        wide["4-back"],
        alternative="two-sided"
    )

    mean_2 = wide["2-back"].mean()
    mean_4 = wide["4-back"].mean()

    results.append({
        "channel": channel,
        "n": len(wide),
        "wilcoxon_W": stat,
        "p_raw": p,
        "mean_2back": mean_2,
        "mean_4back": mean_4,
        "mean_difference_4minus2": mean_4 - mean_2
    })


results_df = pd.DataFrame(results)

# ---------------------------------------------------------
# FDR correction across 19 channels
# ---------------------------------------------------------

reject, p_fdr, _, _ = multipletests(
    results_df["p_raw"],
    alpha=0.05,
    method="fdr_bh"
)

results_df["p_fdr"] = p_fdr
results_df["significant_fdr"] = reject

# Sort by corrected p-value
results_df = results_df.sort_values("p_fdr")

print("=" * 75)
print("SPATIAL ALPHA ANALYSIS — 2-BACK VS 4-BACK")
print("=" * 75)

print()
print(results_df.to_string(index=False))

print()
print("=" * 75)
print("FDR-SIGNIFICANT CHANNELS")
print("=" * 75)

sig = results_df[results_df["significant_fdr"]]

if len(sig) == 0:
    print("No channels survived FDR correction.")
else:
    print(sig.to_string(index=False))

# Save
output = "final_preprocessed/alpha_spatial_2vs4_fdr.csv"

results_df.to_csv(output, index=False)

print()
print("Saved:")
print(output)
