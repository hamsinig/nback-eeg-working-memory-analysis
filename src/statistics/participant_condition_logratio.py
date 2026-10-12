import pandas as pd


# ============================================================
# LOAD LOG-RATIO DATA
# ============================================================

FILE = "final_preprocessed/PSD_log_ratio_from_1back.csv"

df = pd.read_csv(FILE)


# ============================================================
# AVERAGE ACROSS CHANNELS
#
# Statistical unit = participant
#
# We retain:
# participant × condition
# ============================================================

participant_summary = (
    df.groupby(
        ["subject", "condition"]
    )[
        [
            "theta_log_ratio",
            "alpha_log_ratio",
            "beta_log_ratio"
        ]
    ]
    .mean()
    .reset_index()
)


# ============================================================
# CONDITION ORDER
# ============================================================

condition_order = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

participant_summary["condition"] = pd.Categorical(
    participant_summary["condition"],
    categories=condition_order,
    ordered=True
)

participant_summary = participant_summary.sort_values(
    ["subject", "condition"]
)


# ============================================================
# PRINT DATASET
# ============================================================

print("\n" + "=" * 80)
print("PARTICIPANT-LEVEL STATISTICAL DATASET")
print("=" * 80)

print("\nShape:")
print(participant_summary.shape)

print("\nParticipants:")
print(participant_summary["subject"].nunique())

print("\nConditions:")
print(
    participant_summary["condition"]
    .value_counts()
    .sort_index()
)

print("\nFirst 30 rows:")
print(
    participant_summary.head(30)
    .to_string(index=False)
)


# ============================================================
# GROUP MEANS
# ============================================================

print("\n" + "=" * 80)
print("GROUP MEANS")
print("=" * 80)

print(
    participant_summary.groupby("condition")[
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

OUTPUT = (
    "final_preprocessed/"
    "PSD_participant_condition_logratio.csv"
)

participant_summary.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved:")
print(OUTPUT)
