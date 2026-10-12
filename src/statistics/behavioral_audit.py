import pandas as pd
from pathlib import Path

SUBJECTS = [
    "sub-001", "sub-002", "sub-003", "sub-004",
    "sub-005", "sub-006", "sub-007", "sub-008",
    "sub-009", "sub-010", "sub-011", "sub-012",
    "sub-014", "sub-015", "sub-016", "sub-018",
    "sub-019", "sub-020"
]

rows = []

print("=" * 80)
print("BEHAVIORAL DATA AUDIT")
print("=" * 80)

for subject in SUBJECTS:

    # Find events file
    files = list(
        Path(subject).glob("**/*events.tsv")
    )

    if not files:
        print(f"\nWARNING: No events file found for {subject}")
        continue

    events_file = files[0]

    df = pd.read_csv(events_file, sep="\t")

    print()
    print("-" * 80)
    print(subject)
    print("-" * 80)

    print("File:", events_file)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nNumber of rows:", len(df))

    # Show unique task conditions
    if "trial_type" in df.columns:
        print("\nTrial types:")
        print(df["trial_type"].value_counts(dropna=False).to_string())

    # Experimental trials only
    if "istutorial" in df.columns:
        task = df[
            (df["istutorial"] == False) &
            (df["trial_type"].isin(
                ["1-back", "2-back", "3-back", "4-back"]
            ))
        ].copy()
    else:
        task = df[
            df["trial_type"].isin(
                ["1-back", "2-back", "3-back", "4-back"]
            )
        ].copy()

    print("\nExperimental N-back trials:", len(task))

    # -----------------------------------------------------
    # Accuracy
    # -----------------------------------------------------

    if "response_accuracy" in task.columns:

        print("\nresponse_accuracy values:")
        print(
            task["response_accuracy"]
            .value_counts(dropna=False)
            .to_string()
        )

        accuracy = pd.to_numeric(
            task["response_accuracy"],
            errors="coerce"
        )

        print("\nNumeric accuracy summary:")
        print(accuracy.describe().to_string())

    # -----------------------------------------------------
    # Key presses
    # -----------------------------------------------------

    if "key_press" in task.columns:

        print("\nkey_press values:")
        print(
            task["key_press"]
            .value_counts(dropna=False)
            .head(20)
            .to_string()
        )

    # -----------------------------------------------------
    # Matched
    # -----------------------------------------------------

    if "matched" in task.columns:

        print("\nmatched values:")
        print(
            task["matched"]
            .value_counts(dropna=False)
            .to_string()
        )

    # -----------------------------------------------------
    # Potential reaction-time columns
    # -----------------------------------------------------

    print("\nPotential timing columns:")

    timing_cols = [
        c for c in task.columns
        if any(
            word in c.lower()
            for word in [
                "reaction",
                "response_time",
                "rt",
                "latency",
                "duration"
            ]
        )
    ]

    if timing_cols:
        print(timing_cols)

        for col in timing_cols:
            print(f"\n{col}:")
            print(task[col].describe().to_string())

    else:
        print("No obvious reaction-time column found.")

    # -----------------------------------------------------
    # Condition-level counts
    # -----------------------------------------------------

    print("\nTrials per condition:")

    condition_counts = (
        task.groupby("trial_type")
        .size()
    )

    print(condition_counts.to_string())

    # -----------------------------------------------------
    # Save participant-level basic information
    # -----------------------------------------------------

    for condition in ["1-back", "2-back", "3-back", "4-back"]:

        subset = task[
            task["trial_type"] == condition
        ]

        row = {
            "subject": subject,
            "condition": condition,
            "n_trials": len(subset)
        }

        if "response_accuracy" in subset.columns:

            acc = pd.to_numeric(
                subset["response_accuracy"],
                errors="coerce"
            )

            row["accuracy_mean"] = acc.mean()
            row["accuracy_valid_n"] = acc.notna().sum()

        rows.append(row)


# ---------------------------------------------------------
# Save summary
# ---------------------------------------------------------

summary = pd.DataFrame(rows)

output = (
    "final_preprocessed/"
    "behavioral_audit_summary.csv"
)

summary.to_csv(
    output,
    index=False
)

print()
print("=" * 80)
print("SUMMARY SAVED")
print("=" * 80)

print(output)

print()
print(summary.to_string(index=False))
