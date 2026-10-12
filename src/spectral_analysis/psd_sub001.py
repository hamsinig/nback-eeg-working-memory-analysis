import mne
import numpy as np
import pandas as pd


# ============================================================
# SETTINGS
# ============================================================

SUBJECT = "sub-001"

EPOCH_FILE = f"final_preprocessed/{SUBJECT}_clean_epochs.fif"
OUTPUT_FILE = f"final_preprocessed/{SUBJECT}_psd_band_power.csv"

# EEG sampling rate
SFREQ = 250

# Analyze only the actual task period
TMIN = 0.0
TMAX = 1.0

# Frequency range for PSD
FMIN = 1.0
FMAX = 40.0

# Welch parameters
N_PER_SEG = 125       # 0.5 seconds at 250 Hz
N_OVERLAP = 62        # ~50% overlap


# Frequency bands
BANDS = {
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30)
}


# ============================================================
# 1. LOAD CLEANED EPOCHS
# ============================================================

print(f"Loading cleaned epochs: {EPOCH_FILE}")

epochs = mne.read_epochs(
    EPOCH_FILE,
    preload=True
)

print("\nLoaded epochs:")
print(epochs)

print("\nNumber of epochs:", len(epochs))
print("Channels:", len(epochs.ch_names))
print("Sampling frequency:", epochs.info["sfreq"])


# ============================================================
# 2. SELECT TASK PERIOD: 0 TO 1 SECOND
# ============================================================

epochs_task = epochs.copy().crop(
    tmin=TMIN,
    tmax=TMAX,
    include_tmax=False
)

print("\nTask-period data:")
print("Shape:", epochs_task.get_data().shape)

# Shape should be:
# (epochs, channels, time)


# ============================================================
# 3. CALCULATE WELCH PSD
# ============================================================

data = epochs_task.get_data()

print("\nCalculating Welch PSD...")

psds, freqs = mne.time_frequency.psd_array_welch(
    data,
    sfreq=SFREQ,
    fmin=FMIN,
    fmax=FMAX,
    n_per_seg=N_PER_SEG,
    n_overlap=N_OVERLAP,
    average="mean"
)

print("PSD shape:", psds.shape)
print("Frequency bins:", len(freqs))


# ============================================================
# 4. CALCULATE BAND POWER
# ============================================================

results = []

for epoch_index in range(psds.shape[0]):

    # Get condition from the epoch
    condition = epochs_task.events[epoch_index, 2]

    # MNE event IDs map integer IDs to condition names
    condition_name = None

    for name, event_id in epochs_task.event_id.items():
        if event_id == condition:
            condition_name = name
            break

    for channel_index, channel_name in enumerate(
        epochs_task.ch_names
    ):

        channel_psd = psds[epoch_index, channel_index]

        row = {
            "subject": SUBJECT,
            "epoch": epoch_index,
            "condition": condition_name,
            "channel": channel_name
        }

        for band_name, (low, high) in BANDS.items():

            mask = (
                (freqs >= low) &
                (freqs < high)
            )

            # Area under PSD curve = band power
            power_v2 = np.trapezoid(
                channel_psd[mask],
                freqs[mask]
            )

            # Convert V² → µV²
            power_uv2 = power_v2 * 1e12

            row[f"{band_name}_power_uv2"] = power_uv2

        results.append(row)


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

band_power_df = pd.DataFrame(results)


# ============================================================
# 6. SAVE
# ============================================================

band_power_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 7. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PSD ANALYSIS COMPLETE")
print("=" * 60)

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nFinal dataframe shape:")
print(band_power_df.shape)

print("\nFirst 20 rows:")
print(
    band_power_df.head(20).to_string(index=False)
)

print("\nConditions:")
print(
    band_power_df["condition"].value_counts()
)

print("\nDone!")
