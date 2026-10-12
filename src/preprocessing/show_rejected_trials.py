import pandas as pd

# Final 23 rejected epochs
REJECTED = {
    "sub-001": [134, 329, 135],
    "sub-002": [379, 366, 378, 365],
    "sub-003": [391, 396, 175],
    "sub-006": [288, 287],
    "sub-008": [327],
    "sub-009": [273],
    "sub-011": [262],
    "sub-014": [138, 141, 321, 266, 150, 164, 289, 316],
}

# Load the QC table
df = pd.read_csv("FINAL_18_ALL_EPOCH_QC.csv")

rejected_rows = []

for participant, epochs in REJECTED.items():

    participant_df = df[df["subject"] == participant]

    for epoch in epochs:

        row = participant_df[
            participant_df["epoch_index"] == epoch
        ]

        if len(row) == 0:
            print(
                f"WARNING: Could not find "
                f"{participant}, epoch {epoch}"
            )
            continue

        rejected_rows.append(row.iloc[0])


# Combine all rejected epochs
rejected = pd.DataFrame(rejected_rows)

# Sort
rejected = rejected.sort_values(
    ["subject", "epoch_index"]
)

# Columns we want to inspect
columns_to_show = [
    "subject",
    "epoch_index",
    "trial_type",
    "onset",
    "max_ptp_uv",
    "median_ptp_uv",
    "channels_above_threshold",
    "dropped_sample_count",
]

print("\n==============================")
print("FINAL REJECTED EPOCHS")
print("==============================\n")

print(
    rejected[columns_to_show].to_string(index=False)
)


# -----------------------------------------
# Summary by N-back condition
# -----------------------------------------

print("\n\n==============================")
print("REJECTED EPOCHS BY CONDITION")
print("==============================\n")

condition_counts = (
    rejected["trial_type"]
    .value_counts()
    .reindex(
        ["1-back", "2-back", "3-back", "4-back"],
        fill_value=0
    )
)

print(condition_counts)


# -----------------------------------------
# Rejection percentage
# -----------------------------------------

print("\n\n==============================")
print("REJECTION RATE")
print("==============================\n")

initial_trials_per_condition = 1800

for condition in ["1-back", "2-back", "3-back", "4-back"]:

    rejected_count = condition_counts[condition]

    percentage = (
        rejected_count /
        initial_trials_per_condition
    ) * 100

    print(
        f"{condition}: "
        f"{rejected_count}/1800 "
        f"({percentage:.2f}%)"
    )


# -----------------------------------------
# Save results
# -----------------------------------------

rejected.to_csv(
    "final_rejected_trials.csv",
    index=False
)

print(
    "\nSaved detailed results to "
    "'final_rejected_trials.csv'"
)
