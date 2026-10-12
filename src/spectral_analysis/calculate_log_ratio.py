import pandas as pd
import numpy as np


# ============================================================
# LOAD PSD DATA
# ============================================================

FILE = "final_preprocessed/ALL_SUBJECTS_psd_band_power.csv"

df = pd.read_csv(FILE)


# ============================================================
# BAND COLUMNS
# ============================================================

bands = {
    "theta": "theta_power_uv2",
    "alpha": "alpha_power_uv2",
    "beta": "beta_power_uv2"
}


# ============================================================
# AVERAGE EPOCHS
#
# One row becomes:
# participant × channel × condition
# ============================================================

participant_channel = (
    df.groupby(
        ["subject", "channel", "condition"]
    )[list(bands.values())]
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
    ["subject", "channel"] + list(bands.values())
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
# MERGE BASELINE WITH ALL CONDITIONS
# ============================================================

log_ratio = participant_channel.merge(
    baseline,
    on=["subject", "channel"],
    how="left"
)


# ============================================================
# CALCULATE LOG RATIOS
# ============================================================

for band in bands:

    power_column = bands[band]
    baseline_column = f"{band}_baseline"

    log_ratio[f"{band}_log_ratio"] = np.log(
        log_ratio[power_column] /
        log_ratio[baseline_column]
    )


# ============================================================
# KEEP ALL FOUR CONDITIONS
#
# 1-back should be approximately 0 because it is
# the reference condition.
# ============================================================

output_columns = [
    "subject",
    "channel",
    "condition",
    "theta_log_ratio",
    "alpha_log_ratio",
    "beta_log_ratio"
]

log_ratio = log_ratio[output_columns]


# ============================================================
# CONDITION ORDER
# ============================================================

condition_order = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

log_ratio["condition"] = pd.Categorical(
    log_ratio["condition"],
    categories=condition_order,
    ordered=True
)


# ============================================================
# SORT
# ============================================================

log_ratio = log_ratio.sort_values(
    ["subject", "channel", "condition"]
)


# ============================================================
# CHECK RESULTS
# ============================================================

print("\n" + "=" * 80)
print("LOG-RATIO DATASET")
print("=" * 80)

print("\nShape:")
print(log_ratio.shape)

print("\nColumns:")
print(log_ratio.columns.tolist())

print("\nParticipants:")
print(log_ratio["subject"].nunique())

print("\nChannels:")
print(log_ratio["channel"].nunique())

print("\nConditions:")
print(log_ratio["condition"].value_counts().sort_index())


# ============================================================
# CHECK 1-BACK VALUES
# ============================================================

print("\n" + "=" * 80)
print("1-BACK CHECK")
print("=" * 80)

print(
    log_ratio[
        log_ratio["condition"] == "1-back"
    ][
        [
            "theta_log_ratio",
            "alpha_log_ratio",
            "beta_log_ratio"
        ]
    ].describe()
)


# ============================================================
# SUMMARY OF LOG RATIOS
# ============================================================

print("\n" + "=" * 80)
print("LOG-RATIO SUMMARY")
print("=" * 80)

print(
    log_ratio.groupby("condition")[
        [
            "theta_log_ratio",
            "alpha_log_ratio",
            "beta_log_ratio"
        ]
    ].mean()
)


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "PSD_log_ratio_from_1back.csv"
)

log_ratio.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)
