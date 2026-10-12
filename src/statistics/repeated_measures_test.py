import pandas as pd
from scipy.stats import f_oneway
from statsmodels.stats.anova import AnovaRM


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

condition_order = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

df["condition"] = pd.Categorical(
    df["condition"],
    categories=condition_order,
    ordered=True
)


# ============================================================
# BANDS
# ============================================================

bands = {
    "theta": "theta_log_ratio",
    "alpha": "alpha_log_ratio",
    "beta": "beta_log_ratio"
}


# ============================================================
# RUN REPEATED-MEASURES ANOVA
# ============================================================

print("\n" + "=" * 80)
print("REPEATED-MEASURES ANOVA")
print("=" * 80)


results = []


for band_name, value_column in bands.items():

    print("\n")
    print("-" * 80)
    print(f"{band_name.upper()}")
    print("-" * 80)

    model = AnovaRM(
        data=df,
        depvar=value_column,
        subject="subject",
        within=["condition"]
    )

    result = model.fit()

    print(result)

    # Extract F and p
    table = result.anova_table

    f_value = table.loc["condition", "F Value"]
    p_value = table.loc["condition", "Pr > F"]

    results.append({
        "band": band_name,
        "F": f_value,
        "p": p_value
    })


# ============================================================
# SUMMARY TABLE
# ============================================================

results_df = pd.DataFrame(results)


print("\n" + "=" * 80)
print("ANOVA SUMMARY")
print("=" * 80)

print(
    results_df.to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "repeated_measures_anova_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)
