from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "tables"
    / "behavioral_trials_recalculated.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


CONDITIONS = ["1-back", "2-back", "3-back", "4-back"]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("BEHAVIORAL RESPONSE ANALYSIS")
print("=" * 70)

print(f"\nReading:")
print(INPUT_FILE)

df = pd.read_csv(INPUT_FILE)

print(f"\nTotal trials: {len(df)}")


# ============================================================
# CLASSIFY EACH TRIAL
# ============================================================

df["response_type"] = "unknown"

df.loc[
    (df["matched"] == True) &
    (df["key_press"] == True),
    "response_type"
] = "hit"

df.loc[
    (df["matched"] == True) &
    (df["key_press"] == False),
    "response_type"
] = "miss"

df.loc[
    (df["matched"] == False) &
    (df["key_press"] == True),
    "response_type"
] = "false_alarm"

df.loc[
    (df["matched"] == False) &
    (df["key_press"] == False),
    "response_type"
] = "correct_rejection"


# ============================================================
# CHECK CLASSIFICATION
# ============================================================

print("\nResponse classification:")
print(df["response_type"].value_counts())

unknown = (df["response_type"] == "unknown").sum()

print(f"\nUnknown trials: {unknown}")

if unknown != 0:
    raise ValueError("Some trials could not be classified.")


# ============================================================
# PARTICIPANT × CONDITION ANALYSIS
# ============================================================

rows = []

for subject in sorted(df["subject"].unique()):

    subject_df = df[df["subject"] == subject]

    for condition in CONDITIONS:

        cond_df = subject_df[
            subject_df["trial_type"] == condition
        ]

        hits = (
            cond_df["response_type"] == "hit"
        ).sum()

        misses = (
            cond_df["response_type"] == "miss"
        ).sum()

        false_alarms = (
            cond_df["response_type"] == "false_alarm"
        ).sum()

        correct_rejections = (
            cond_df["response_type"] == "correct_rejection"
        ).sum()

        target_trials = hits + misses

        non_target_trials = (
            false_alarms + correct_rejections
        )

        hit_rate = (
            hits / target_trials
            if target_trials > 0
            else float("nan")
        )

        false_alarm_rate = (
            false_alarms / non_target_trials
            if non_target_trials > 0
            else float("nan")
        )

        miss_rate = (
            misses / target_trials
            if target_trials > 0
            else float("nan")
        )

        correct_rejection_rate = (
            correct_rejections / non_target_trials
            if non_target_trials > 0
            else float("nan")
        )

        accuracy = (
            (hits + correct_rejections) /
            len(cond_df)
        )

        rows.append({
            "subject": subject,
            "condition": condition,
            "hits": hits,
            "misses": misses,
            "false_alarms": false_alarms,
            "correct_rejections": correct_rejections,
            "target_trials": target_trials,
            "non_target_trials": non_target_trials,
            "hit_rate": hit_rate,
            "miss_rate": miss_rate,
            "false_alarm_rate": false_alarm_rate,
            "correct_rejection_rate": correct_rejection_rate,
            "accuracy": accuracy,
        })


participant_results = pd.DataFrame(rows)


# ============================================================
# PRINT PARTICIPANT-LEVEL RESULTS
# ============================================================

print("\n" + "=" * 70)
print("PARTICIPANT × CONDITION")
print("=" * 70)

print(
    participant_results[
        [
            "subject",
            "condition",
            "hits",
            "misses",
            "false_alarms",
            "correct_rejections",
            "hit_rate",
            "false_alarm_rate",
            "accuracy",
        ]
    ].to_string(index=False)
)


# ============================================================
# GROUP MEANS
# ============================================================

group_means = (
    participant_results
    .groupby("condition")
    [
        [
            "hit_rate",
            "miss_rate",
            "false_alarm_rate",
            "correct_rejection_rate",
            "accuracy",
        ]
    ]
    .mean()
    .reindex(CONDITIONS)
)


print("\n" + "=" * 70)
print("MEAN ACROSS 18 PARTICIPANTS")
print("=" * 70)

print(group_means)


print("\nPercentages:")

for condition in CONDITIONS:

    row = group_means.loc[condition]

    print(f"\n{condition}")

    print(
        f"  Accuracy: "
        f"{row['accuracy'] * 100:.2f}%"
    )

    print(
        f"  Hit rate: "
        f"{row['hit_rate'] * 100:.2f}%"
    )

    print(
        f"  Miss rate: "
        f"{row['miss_rate'] * 100:.2f}%"
    )

    print(
        f"  False-alarm rate: "
        f"{row['false_alarm_rate'] * 100:.2f}%"
    )

    print(
        f"  Correct-rejection rate: "
        f"{row['correct_rejection_rate'] * 100:.2f}%"
    )


# ============================================================
# POOLED TRIAL COUNTS
# ============================================================

pooled = (
    participant_results
    .groupby("condition")
    [
        [
            "hits",
            "misses",
            "false_alarms",
            "correct_rejections",
        ]
    ]
    .sum()
    .reindex(CONDITIONS)
)


print("\n" + "=" * 70)
print("POOLED TRIAL COUNTS")
print("=" * 70)

print(pooled)


# ============================================================
# SAVE RESULTS
# ============================================================

participant_output = (
    OUTPUT_DIR /
    "behavioral_hit_false_alarm_participant_condition.csv"
)

group_output = (
    OUTPUT_DIR /
    "behavioral_hit_false_alarm_group_means.csv"
)

pooled_output = (
    OUTPUT_DIR /
    "behavioral_hit_false_alarm_pooled_counts.csv"
)

participant_results.to_csv(
    participant_output,
    index=False
)

group_means.to_csv(
    group_output
)

pooled.to_csv(
    pooled_output
)

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(participant_output)
print(group_output)
print(pooled_output)

print("\nDone.")
