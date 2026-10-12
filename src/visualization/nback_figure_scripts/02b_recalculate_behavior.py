from pathlib import Path
import pandas as pd


# ============================================================
# 1. PATHS
# ============================================================

# This script is located at:
# nback-eeg-working-memory-analysis/
#   src/
#     visualization/
#       nback_figure_scripts/
#
# Therefore, parents[3] = nback-eeg-working-memory-analysis

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Dataset is a sibling of the analysis project
DATASET_ROOT = PROJECT_ROOT.parent / "ds007169"

# Save recalculated results inside the project
OUTPUT_DIR = PROJECT_ROOT / "results" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. SETTINGS
# ============================================================

EXCLUDE = {"sub-013", "sub-017"}

CONDITIONS = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]


# ============================================================
# 3. CHECK DATASET PATH
# ============================================================

print("=" * 70)
print("BEHAVIORAL DATA RE-CALCULATION")
print("=" * 70)

print(f"\nProject root:")
print(PROJECT_ROOT)

print(f"\nDataset root:")
print(DATASET_ROOT)

if not DATASET_ROOT.exists():
    raise FileNotFoundError(
        f"\nDataset not found at:\n{DATASET_ROOT}\n"
        "Check that ds007169 is beside the analysis project."
    )


# ============================================================
# 4. FIND PARTICIPANTS
# ============================================================

participants = sorted(
    [
        p
        for p in DATASET_ROOT.glob("sub-*")
        if p.is_dir() and p.name not in EXCLUDE
    ]
)

print("\nParticipants included:")
print([p.name for p in participants])

print(f"\nNumber included: {len(participants)}")
print(f"Excluded: {sorted(EXCLUDE)}")


# ============================================================
# 5. STORAGE
# ============================================================

all_results = []
all_trials = []


# ============================================================
# 6. PROCESS EACH PARTICIPANT
# ============================================================

for participant_dir in participants:

    subject = participant_dir.name

    event_file = (
        participant_dir
        / "eeg"
        / f"{subject}_task-nback_events.tsv"
    )

    print("\n" + "-" * 70)
    print(subject)
    print("-" * 70)

    if not event_file.exists():
        print(f"WARNING: Event file not found:")
        print(event_file)
        continue

    print(f"Reading:")
    print(event_file)

    # Read TSV
    df = pd.read_csv(event_file, sep="\t")

    # --------------------------------------------------------
    # Keep only experimental N-back trials
    # --------------------------------------------------------

    trials = df[
        df["trial_type"].isin(CONDITIONS)
        & (df["istutorial"] == False)
    ].copy()

    print(f"Experimental trials: {len(trials)}")

    # --------------------------------------------------------
    # Basic checks
    # --------------------------------------------------------

    condition_counts = (
        trials["trial_type"]
        .value_counts()
        .reindex(CONDITIONS)
    )

    print("\nTrials per condition:")
    print(condition_counts)

    # Check missing accuracy
    missing_accuracy = trials["response_accuracy"].isna().sum()

    print(f"\nMissing response_accuracy: {missing_accuracy}")

    # --------------------------------------------------------
    # Save trials for later global analysis
    # --------------------------------------------------------

    trials["subject"] = subject

    all_trials.append(trials)

    # --------------------------------------------------------
    # Calculate accuracy for each condition
    # --------------------------------------------------------

    for condition in CONDITIONS:

        condition_data = trials[
            trials["trial_type"] == condition
        ]

        accuracy = condition_data["response_accuracy"].mean()

        all_results.append({
            "subject": subject,
            "condition": condition,
            "n_trials": len(condition_data),
            "accuracy": accuracy
        })


# ============================================================
# 7. COMBINE RESULTS
# ============================================================

results = pd.DataFrame(all_results)

all_trials_df = pd.concat(
    all_trials,
    ignore_index=True
)


# ============================================================
# 8. PARTICIPANT × CONDITION TABLE
# ============================================================

accuracy_table = (
    results
    .pivot(
        index="subject",
        columns="condition",
        values="accuracy"
    )
    .reindex(columns=CONDITIONS)
)

print("\n" + "=" * 70)
print("PARTICIPANT × CONDITION ACCURACY")
print("=" * 70)

print(
    accuracy_table.to_string(
        float_format=lambda x: f"{x:.3f}"
    )
)


# ============================================================
# 9. MEAN ACCURACY ACROSS PARTICIPANTS
# ============================================================

summary = (
    results
    .groupby("condition")["accuracy"]
    .agg(
        mean="mean",
        std="std",
        n="count"
    )
    .reindex(CONDITIONS)
)

print("\n" + "=" * 70)
print("MEAN ACCURACY ACROSS PARTICIPANTS")
print("=" * 70)

print(
    summary.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\nPercentages:")

for condition in CONDITIONS:

    mean_accuracy = summary.loc[condition, "mean"]

    print(
        f"{condition}: "
        f"{mean_accuracy * 100:.2f}%"
    )


# ============================================================
# 10. IMPORTANT:
#     CHECK HOW response_accuracy RELATES TO
#     matched AND key_press
# ============================================================

print("\n" + "=" * 70)
print("CHECKING response_accuracy LOGIC")
print("=" * 70)

print(
    """
We are testing whether:

    matched == key_press

corresponds to:

    response_accuracy == 1

This is the expected logic if:
    matched=True  means a target was present
    key_press=True means participant responded
"""
)


# Convert values to boolean where necessary
all_trials_df["matched_bool"] = (
    all_trials_df["matched"].astype(bool)
)

all_trials_df["key_press_bool"] = (
    all_trials_df["key_press"].astype(bool)
)

all_trials_df["accuracy_recalculated"] = (
    all_trials_df["matched_bool"]
    == all_trials_df["key_press_bool"]
)


# ------------------------------------------------------------
# Compare reconstructed accuracy with dataset accuracy
# ------------------------------------------------------------

all_trials_df["accuracy_matches_dataset"] = (
    all_trials_df["accuracy_recalculated"].astype(int)
    == all_trials_df["response_accuracy"]
)


print("\nNumber of trials:")
print(len(all_trials_df))

print("\nDoes reconstructed accuracy match dataset accuracy?")

print(
    all_trials_df[
        "accuracy_matches_dataset"
    ].value_counts()
)


mismatch_count = (
    ~all_trials_df["accuracy_matches_dataset"]
).sum()

print("\nMismatch count:")
print(mismatch_count)

print(
    f"Mismatch percentage: "
    f"{mismatch_count / len(all_trials_df) * 100:.2f}%"
)


# ============================================================
# 11. CROSS-TABULATION
# ============================================================

print("\n" + "=" * 70)
print("MATCHED × KEY_PRESS × RESPONSE_ACCURACY")
print("=" * 70)

cross_tab = pd.crosstab(
    [
        all_trials_df["matched"],
        all_trials_df["key_press"]
    ],
    all_trials_df["response_accuracy"]
)

print(cross_tab)


# ============================================================
# 12. SHOW MISMATCHED TRIALS IF ANY
# ============================================================

if mismatch_count > 0:

    print("\n" + "=" * 70)
    print("MISMATCHED TRIALS")
    print("=" * 70)

    mismatch_columns = [
        "subject",
        "onset",
        "trial_type",
        "nback_level",
        "matched",
        "key_press",
        "response_accuracy",
        "outcome",
        "istutorial"
    ]

    print(
        all_trials_df[
            ~all_trials_df["accuracy_matches_dataset"]
        ][mismatch_columns]
        .head(30)
        .to_string(index=False)
    )

else:

    print(
        "\nALL trials agree with the reconstructed "
        "match/response accuracy rule."
    )


# ============================================================
# 13. CHECK ACCURACY BY CONDITION USING OUR OWN RULE
# ============================================================

independent_accuracy = (
    all_trials_df
    .groupby(
        ["subject", "trial_type"]
    )["accuracy_recalculated"]
    .mean()
    .reset_index(name="accuracy_recalculated")
)

independent_summary = (
    independent_accuracy
    .groupby("trial_type")["accuracy_recalculated"]
    .mean()
    .reindex(CONDITIONS)
)

print("\n" + "=" * 70)
print("INDEPENDENTLY RECALCULATED ACCURACY")
print("=" * 70)

for condition in CONDITIONS:

    value = independent_summary.loc[condition]

    print(
        f"{condition}: "
        f"{value * 100:.2f}%"
    )


# ============================================================
# 14. SAVE RESULTS
# ============================================================

results_file = (
    OUTPUT_DIR /
    "behavioral_accuracy_recalculated.csv"
)

trials_file = (
    OUTPUT_DIR /
    "behavioral_trials_recalculated.csv"
)

accuracy_table_file = (
    OUTPUT_DIR /
    "behavioral_accuracy_participant_condition.csv"
)

results.to_csv(
    results_file,
    index=False
)

all_trials_df.to_csv(
    trials_file,
    index=False
)

accuracy_table.to_csv(
    accuracy_table_file
)


# ============================================================
# 15. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(results_file)
print(trials_file)
print(accuracy_table_file)

print("\nDone.")
