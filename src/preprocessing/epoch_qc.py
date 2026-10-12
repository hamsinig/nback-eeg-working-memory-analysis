import mne
import pandas as pd
import numpy as np
from mne.preprocessing import ICA

# --------------------------------------------------
# 1. Load EEG
# --------------------------------------------------

raw = mne.io.read_raw_brainvision(
    "sub-001/eeg/sub-001_task-nback_eeg.vhdr",
    preload=True
)

print("Original:")
print(raw)

# --------------------------------------------------
# 2. Keep EEG channels
# --------------------------------------------------

raw.pick("eeg")

print("\nAfter keeping EEG channels:")
print(raw)

# --------------------------------------------------
# 3. Fix channel names
# --------------------------------------------------

raw.rename_channels({
    "FP1": "Fp1",
    "FP2": "Fp2"
})

# --------------------------------------------------
# 4. Set montage
# --------------------------------------------------

montage = mne.channels.make_standard_montage(
    "standard_1020"
)

raw.set_montage(montage)

# --------------------------------------------------
# 5. Correct dataset-specific scaling
# --------------------------------------------------

raw._data *= 1e-7

print("\nScaling correction applied.")

# --------------------------------------------------
# 6. Band-pass filter
# --------------------------------------------------

raw.filter(1.0, 40.0)

print("\n1–40 Hz filtering complete.")

# --------------------------------------------------
# 7. Fit ICA
# --------------------------------------------------

ica = ICA(
    n_components=19,
    method="fastica",
    random_state=42,
    max_iter="auto"
)

print("\nFitting ICA...")

ica.fit(
    raw,
    decim=3
)

print("\nICA fitted.")

# --------------------------------------------------
# 8. Remove ICA000 for sub-001
# --------------------------------------------------

ica.exclude = [0]

print("\nRemoving ICA000...")

ica.apply(raw)

print("ICA cleaning complete.")

# --------------------------------------------------
# 9. Load events.tsv
# --------------------------------------------------

events_file = (
    "sub-001/eeg/"
    "sub-001_task-nback_events.tsv"
)

events_df = pd.read_csv(
    events_file,
    sep="\t"
)

print("\nEvents loaded:")
print(events_df.shape)

# --------------------------------------------------
# 10. Keep only real experimental trials
# --------------------------------------------------

trial_types = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]

experimental = events_df[
    (events_df["trial_type"].isin(trial_types)) &
    (events_df["istutorial"] == False)
].copy()

print("\nExperimental trials:")
print(experimental["trial_type"].value_counts())

# --------------------------------------------------
# 11. Convert event onset to EEG sample
# --------------------------------------------------

sfreq = raw.info["sfreq"]

experimental["sample"] = (
    experimental["onset"] * sfreq
).round().astype(int)

# --------------------------------------------------
# 12. Create MNE event array
# --------------------------------------------------

event_id = {
    "1-back": 1,
    "2-back": 2,
    "3-back": 3,
    "4-back": 4
}

events = np.column_stack([
    experimental["sample"].values,
    np.zeros(len(experimental), dtype=int),
    experimental["trial_type"].map(event_id).values
])

events = events.astype(int)

print("\nMNE events shape:")
print(events.shape)

# --------------------------------------------------
# 13. Create epochs
# --------------------------------------------------

epochs = mne.Epochs(
    raw,
    events,
    event_id=event_id,
    tmin=-0.2,
    tmax=1.0,
    baseline=(-0.2, 0),
    preload=True,
    reject_by_annotation=False
)

print("\nEpochs created:")
print(epochs)

# --------------------------------------------------
# 14. Print number of epochs per condition
# --------------------------------------------------

print("\nEpoch counts:")
print(
    {
        condition: len(epochs[condition])
        for condition in event_id
    }
)

# --------------------------------------------------
# 15. Calculate peak-to-peak amplitude
# --------------------------------------------------

data = epochs.get_data()

print("\nEpoch data shape:")
print(data.shape)

# Peak-to-peak for every epoch and channel
ptp = np.ptp(data, axis=2)

# Maximum channel PTP within each epoch
epoch_max_ptp = np.max(ptp, axis=1)

print("\nEpoch peak-to-peak statistics:")
print(
    f"Minimum: {epoch_max_ptp.min() * 1e6:.2f} µV"
)

print(
    f"Median: {np.median(epoch_max_ptp) * 1e6:.2f} µV"
)

print(
    f"95th percentile: "
    f"{np.percentile(epoch_max_ptp, 95) * 1e6:.2f} µV"
)

print(
    f"99th percentile: "
    f"{np.percentile(epoch_max_ptp, 99) * 1e6:.2f} µV"
)

print(
    f"Maximum: {epoch_max_ptp.max() * 1e6:.2f} µV"
)

# --------------------------------------------------
# 16. Save PTP values for later inspection
# --------------------------------------------------

ptp_df = pd.DataFrame({
    "trial_type": experimental["trial_type"].values,
    "onset": experimental["onset"].values,
    "max_ptp_uv": epoch_max_ptp * 1e6
})

ptp_df.to_csv(
    "sub-001_epoch_ptp.csv",
    index=False
)

print("\nSaved:")
print("sub-001_epoch_ptp.csv")
