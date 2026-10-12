import mne
import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

SUBJECTS = [
    "sub-001",
    "sub-002",
    "sub-003",
    "sub-004",
    "sub-005",
    "sub-006",
    "sub-007",
    "sub-008",
    "sub-009",
    "sub-010",
    "sub-011",
    "sub-012",
    "sub-014",
    "sub-015",
    "sub-016",
    "sub-018",
    "sub-019",
    "sub-020"
]

INPUT_DIR = Path("final_preprocessed")
OUTPUT_FILE = INPUT_DIR / "ALL_SUBJECTS_psd_band_power.csv"


# ============================================================
# PSD SETTINGS
# ============================================================

SFREQ = 250

# Analyze only the actual task period
TMIN = 0.0
TMAX = 1.0

# Frequency range
FMIN = 1.0
FMAX = 40.0

# Welch parameters
N_PER_SEG = 125       # 0.5 seconds at 250 Hz
N_OVERLAP = 62        # approximately 50% overlap


# ============================================================
# FREQUENCY BANDS
# ============================================================

BANDS = {
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30)
}


# ============================================================
# STORE ALL RESULTS HERE
# ============================================================

all_results = []


# ============================================================
# PROCESS EACH PARTICIPANT
# ============================================================

for subject in SUBJECTS:

    print("\n" + "=" * 70)
    print(f"PROCESSING {subject}")
    print("=" * 70)

    epoch_file = INPUT_DIR / f"{subject}_clean_epochs.fif"

    if not epoch_file.exists():
        print(f"WARNING: File not found: {epoch_file}")
        continue

    # --------------------------------------------------------
    # 1. LOAD CLEANED EPOCHS
    # --------------------------------------------------------

    print(f"Loading: {epoch_file}")

    epochs = mne.read_epochs(
        epoch_file,
        preload=True,
        verbose=False
    )

    print(f"Clean epochs: {len(epochs)}")
    print(f"Channels: {len(epochs.ch_names)}")

    # --------------------------------------------------------
    # 2. CROP TO TASK PERIOD
    # --------------------------------------------------------

    epochs_task = epochs.copy().crop(
        tmin=TMIN,
        tmax=TMAX,
        include_tmax=False
    )

    data = epochs_task.get_data()

    print(f"Task data shape: {data.shape}")

    # Expected:
    # (number of clean trials, 19 channels, 250 samples)


    # --------------------------------------------------------
    # 3. CALCULATE WELCH PSD
    # --------------------------------------------------------

    print("Calculating Welch PSD...")

    psds, freqs = mne.time_frequency.psd_array_welch(
        data,
        sfreq=SFREQ,
        fmin=FMIN,
        fmax=FMAX,
        n_per_seg=N_PER_SEG,
        n_overlap=N_OVERLAP,
        average="mean",
        verbose=False
    )

    print(f"PSD shape: {psds.shape}")


    # --------------------------------------------------------
    # 4. CALCULATE BAND POWER
    # --------------------------------------------------------

    for epoch_index in range(psds.shape[0]):

        # Get event ID for this epoch
        event_id = epochs_task.events[epoch_index, 2]

        # Convert event ID to condition name
        condition_name = None

        for name, value in epochs_task.event_id.items():

            if value == event_id:
                condition_name = name
                break

        # Safety check
        if condition_name is None:
            print(
                f"WARNING: Unknown event ID {event_id} "
                f"for {subject}, epoch {epoch_index}"
            )
            continue


        # ----------------------------------------------------
        # LOOP THROUGH EEG CHANNELS
        # ----------------------------------------------------

        for channel_index, channel_name in enumerate(
            epochs_task.ch_names
        ):

            channel_psd = psds[
                epoch_index,
                channel_index
            ]

            row = {
                "subject": subject,
                "epoch": epoch_index,
                "condition": condition_name,
                "channel": channel_name
            }


            # ------------------------------------------------
            # CALCULATE THETA / ALPHA / BETA POWER
            # ------------------------------------------------

            for band_name, (low, high) in BANDS.items():

                mask = (
                    (freqs >= low) &
                    (freqs < high)
                )

                # Integrate PSD over frequency
                # This gives band power in V²
                power_v2 = np.trapezoid(
                    channel_psd[mask],
                    freqs[mask]
                )

                # Convert V² → µV²
                power_uv2 = power_v2 * 1e12

                row[
                    f"{band_name}_power_uv2"
                ] = power_uv2


            all_results.append(row)


    print(f"Finished {subject}")


# ============================================================
# CREATE MASTER DATAFRAME
# ============================================================

print("\n" + "=" * 70)
print("CREATING MASTER DATAFRAME")
print("=" * 70)

psd_df = pd.DataFrame(all_results)


# ============================================================
# SAVE
# ============================================================

psd_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\nSaved:")
print(OUTPUT_FILE)

print("\nFinal dataframe shape:")
print(psd_df.shape)

print("\nColumns:")
print(psd_df.columns.tolist())


# ------------------------------------------------------------
# Number of clean trials per participant
# ------------------------------------------------------------

print("\nClean trials per participant:")

trial_counts = (
    psd_df
    .groupby(["subject", "epoch"])
    .size()
    .groupby("subject")
    .size()
)

print(trial_counts)


# ------------------------------------------------------------
# Number of trials per condition
# ------------------------------------------------------------

print("\nClean trials per condition:")

condition_counts = (
    psd_df
    .groupby(["subject", "epoch", "condition"])
    .size()
    .reset_index()
    .groupby(["subject", "condition"])
    .size()
    .unstack(fill_value=0)
)

print(condition_counts)


print("\n" + "=" * 70)
print("PSD EXTRACTION COMPLETE")
print("=" * 70)
