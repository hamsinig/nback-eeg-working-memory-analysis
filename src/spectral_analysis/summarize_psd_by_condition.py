import pandas as pd


# ============================================================
# LOAD PSD DATA
# ============================================================

FILE = "final_preprocessed/ALL_SUBJECTS_psd_band_power.csv"

df = pd.read_csv(FILE)


# ============================================================
# AVERAGE ACROSS CHANNELS AND EPOCHS
# ============================================================

summary = (
    df.groupby(
        ["subject", "condition"]
    )[
        [
            "theta_power_uv2",
            "alpha_power_uv2",
            "beta_power_uv2"
        ]
    ]
    .mean()
    .reset_index()
)


# ============================================================
# ORDER CONDITIONS
# ============================================================

condition_order = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

summary["condition"] = pd.Categorical(
    summary["condition"],
    categories=condition_order,
    ordered=True
)

summary = summary.sort_values(
    ["subject", "condition"]
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 80)
print("PARTICIPANT × CONDITION PSD SUMMARY")
print("=" * 80)

print(summary.to_string(index=False))


# ============================================================
# GROUP-LEVEL SUMMARY
# ============================================================

group_summary = (
    summary
    .groupby("condition", observed=True)
    [
        [
            "theta_power_uv2",
            "alpha_power_uv2",
            "beta_power_uv2"
        ]
    ]
    .agg(["mean", "std"])
)


print("\n" + "=" * 80)
print("GROUP-LEVEL SUMMARY")
print("=" * 80)

print(group_summary)


# ============================================================
# SAVE
# ============================================================

summary.to_csv(
    "final_preprocessed/PSD_participant_condition_summary.csv",
    index=False
)

print("\nSaved:")
print(
    "final_preprocessed/PSD_participant_condition_summary.csv"
)
