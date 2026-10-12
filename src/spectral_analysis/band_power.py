import mne
import pandas as pd
import numpy as np

# -------------------------
# 1. Load EEG
# -------------------------
raw = mne.io.read_raw_brainvision(
    "sub-001/eeg/sub-001_task-nback_eeg.vhdr",
    preload=True
)

# -------------------------
# 2. Filter
# -------------------------
raw.filter(
    l_freq=1.0,
    h_freq=40.0
)

# -------------------------
# 3. Load events
# -------------------------
events_df = pd.read_csv(
    "sub-001/eeg/sub-001_task-nback_events.tsv",
    sep="\t"
)

# Keep actual experimental trials
events_df = events_df[
    (events_df["trial_type"].isin(
        ["1-back", "2-back", "3-back", "4-back"]
    ))
    & (events_df["istutorial"] == False)
].copy()

# -------------------------
# 4. Convert onset → samples
# -------------------------
sfreq = raw.info["sfreq"]

event_samples = (
    events_df["onset"] * sfreq
).astype(int)

events = np.column_stack([
    event_samples,
    np.zeros(len(event_samples), dtype=int),
    events_df["nback_level"].astype(int)
])

# -------------------------
# 5. Create epochs
# -------------------------
epochs = mne.Epochs(
    raw,
    events,
    tmin=-0.2,
    tmax=1.0,
    picks=["Fz"],
    baseline=(-0.2, 0),
    preload=True
)

# -------------------------
# 6. First epoch
# -------------------------
epoch = epochs[0]

# -------------------------
# 7. PSD
# -------------------------
spectrum = epoch.compute_psd(
    method="welch",
    fmin=1,
    fmax=40,
    n_fft=256
)

power = spectrum.get_data()[0, 0, :]
frequencies = spectrum.freqs

# -------------------------
# 8. Define frequency bands
# -------------------------
bands = {
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30)
}

# -------------------------
# 9. Calculate band power
# -------------------------
for band_name, (low, high) in bands.items():

    mask = (
        (frequencies >= low)
        & (frequencies <= high)
    )

    band_power = np.trapezoid(
        power[mask],
        frequencies[mask]
    )

    print(
        f"{band_name.capitalize()} power: "
        f"{band_power:.4f}"
    )
