import pandas as pd


# ============================================================
# LOAD PSD DATA
# ============================================================

FILE = "final_preprocessed/ALL_SUBJECTS_psd_band_power.csv"

df = pd.read_csv(FILE)


# ============================================================
# BAND COLUMNS
# ============================================================

bands = [
    "theta_power_uv2",
    "alpha_power_uv2",
    "beta_power_uv2"
]


# ============================================================
# FIRST AVERAGE EPOCHS
#
# One row becomes:
# participant × channel × condition
# ============================================================

participant_channel = (
    df.groupby(
        ["subject", "channel", "condition"]
    )[bands]
    .mean()
    .reset_index()
)


# ============================================================
# EXTRACT 1-BACK BASELINE
# ============================================================

baseline = participant_channel[
    participant_channel["condition"] == "1-back"
].copy()


baseline = baseline[
    ["subject", "channel"] + bands
]


# Rename baseline columns
baseline = baseline.rename(
    columns={
        "theta_power_uv2": "theta_baseline",
        "alpha_power_uv2": "alpha_baseline",
        "beta_power_uv2": "beta_baseline"
    }
)


# ============================================================
# MERGE BASELINE BACK
# ============================================================

relative = participant_channel.merge(
    baseline,
    on=["subject", "channel"],
    how="left"
)


# ============================================================
# CALCULATE RELATIVE CHANGE
# ============================================================

for band in ["theta", "alpha", "beta"]:

    power_column = f"{band}_power_uv2"
    baseline_column = f"{band}_baseline"

    relative[f"{band}_relative_change_pct"] = (
        (
            relative[power_column]
            - relative[baseline_column]
        )
        / relative[baseline_column]
        * 100
    )


# ============================================================
# REMOVE 1-BACK
#
# Relative change is defined relative to 1-back,
# so the useful workload comparisons are 2/3/4-back.
# ============================================================

relative = relative[
    relative["condition"].isin(
        ["2-back", "3-back", "4-back"]
    )
].copy()


# ============================================================
# SELECT FINAL COLUMNS
# ============================================================

output_columns = [
    "subject",
    "channel",
    "condition",
    "theta_relative_change_pct",
    "alpha_relative_change_pct",
    "beta_relative_change_pct"
]

relative = relative[output_columns]


# ============================================================
# SORT
# ============================================================

condition_order = [
    "2-back",
    "3-back",
    "4-back"
]

relative["condition"] = pd.Categorical(
    relative["condition"],
    categories=condition_order,
    ordered=True
)

relative = relative.sort_values(
    ["subject", "channel", "condition"]
)


# ============================================================
# BASIC CHECKS
# ============================================================

print("\n" + "=" * 80)
print("RELATIVE-CHANGE DATASET")
print("=" * 80)

print("Shape:", relative.shape)

print("\nColumns:")
print(relative.columns.tolist())

print("\nRows per condition:")
print(relative["condition"].value_counts().sort_index())

print("\nParticipants:")
print(relative["subject"].nunique())

print("\nChannels:")
print(relative["channel"].nunique())


# ============================================================
# SHOW FIRST ROWS
# ============================================================

print("\nFirst 30 rows:")
print(
    relative.head(30).to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "PSD_relative_change_from_1back.csv"
)

relative.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)
