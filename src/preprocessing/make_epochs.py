import mne
import pandas as pd
import numpy as np

# Load EEG
raw = mne.io.read_raw_brainvision(
    "sub-001/eeg/sub-001_task-nback_eeg.vhdr",
    preload=True
)

# Filter
raw.filter(1.0, 40.0)

# Load events
events_df = pd.read_csv(
    "sub-001/eeg/sub-001_task-nback_events.tsv",
    sep="\t"
)

# Keep only real experimental trials
events_df = events_df[
    (events_df["trial_type"].isin(["1-back", "2-back", "3-back", "4-back"]))
    & (events_df["istutorial"] == False)
].copy()

print("Experimental trials:", len(events_df))

# Convert onset times → EEG sample numbers
sfreq = raw.info["sfreq"]

event_samples = (events_df["onset"] * sfreq).astype(int)

# Create MNE event array
events = np.column_stack([
    event_samples,
    np.zeros(len(event_samples), dtype=int),
    events_df["nback_level"].astype(int)
])

# Create epochs
epochs = mne.Epochs(
    raw,
    events,
    tmin=-0.2,
    tmax=1.0,
    picks=["Fz"],
    baseline=(-0.2, 0),
    preload=True
)

print(epochs)
