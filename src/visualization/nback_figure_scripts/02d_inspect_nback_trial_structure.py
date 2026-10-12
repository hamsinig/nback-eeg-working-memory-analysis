
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_ROOT = PROJECT_ROOT.parent / "ds007169"

SUBJECTS = [
    f"sub-{i:03d}"
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 20]
]

CONDITIONS = ["1-back", "2-back", "3-back", "4-back"]


def to_bool(value):
    """Convert common TSV boolean representations safely."""
    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value == "true":
        return True
    if value == "false":
        return False

    return None


all_trials = []

for subject in SUBJECTS:
    path = (
        DATASET_ROOT
        / subject
        / "eeg"
        / f"{subject}_task-nback_events.tsv"
    )

    df = pd.read_csv(path, sep="\t")

    trials = df[
        df["trial_type"].isin(CONDITIONS)
        & df["istutorial"].apply(to_bool).eq(False)
    ].copy()

    trials["subject"] = subject
    trials["matched_bool"] = trials["matched"].apply(to_bool)
    trials["key_press_bool"] = trials["key_press"].apply(to_bool)

    all_trials.append(trials)

df = pd.concat(all_trials, ignore_index=True)

print("=" * 70)
print("1. AVAILABLE EVENT COLUMNS")
print("=" * 70)
print(df.columns.tolist())

print("\n" + "=" * 70)
print("2. EXAMPLE RAW MARKERS: sub-001")
print("=" * 70)

example = df[df["subject"] == "sub-001"]

columns = [
    c for c in [
        "onset",
        "trial_type",
        "marker",
        "nback_level",
        "matched",
        "key_press",
        "response_accuracy",
        "outcome",
    ]
    if c in example.columns
]

print(example[columns].head(20).to_string(index=False))

print("\n" + "=" * 70)
print("3. UNIQUE MARKER VALUES")
print("=" * 70)

if "marker" in df.columns:
    print(
        df["marker"]
        .dropna()
        .astype(str)
        .value_counts()
        .head(40)
        .to_string()
    )

print("\n" + "=" * 70)
print("4. TARGET COUNTS BY CONDITION")
print("=" * 70)

target_summary = (
    df.groupby(["subject", "trial_type"])["matched_bool"]
    .agg(
        target_trials=lambda x: (x == True).sum(),
        non_target_trials=lambda x: (x == False).sum(),
        unknown=lambda x: x.isna().sum(),
    )
    .reset_index()
)

print(
    target_summary
    .groupby("trial_type")[
        ["target_trials", "non_target_trials", "unknown"]
    ]
    .agg(["mean", "std", "min", "max"])
    .reindex(CONDITIONS)
    .to_string()
)

print("\n" + "=" * 70)
print("5. TARGET PROPORTION FOR EACH PARTICIPANT")
print("=" * 70)

target_summary["target_percentage"] = (
    target_summary["target_trials"] /
    (
        target_summary["target_trials"]
        + target_summary["non_target_trials"]
    )
    * 100
)

print(
    target_summary.pivot(
        index="subject",
        columns="trial_type",
        values="target_percentage",
    )
    .reindex(columns=CONDITIONS)
    .round(1)
    .to_string()
)

print("\n" + "=" * 70)
print("6. CHECK RESPONSE ACCURACY CONSISTENCY")
print("=" * 70)

valid = df[
    df["matched_bool"].notna()
    & df["key_press_bool"].notna()
    & df["response_accuracy"].notna()
].copy()

reconstructed = (
    valid["matched_bool"] == valid["key_press_bool"]
).astype(int)

stored = valid["response_accuracy"].astype(int)

print(f"Trials checked: {len(valid)}")
print(f"Mismatches: {(reconstructed != stored).sum()}")

print("\nInspection complete.")
