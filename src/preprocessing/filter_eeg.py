import mne
import matplotlib.pyplot as plt

# Load the raw EEG
raw = mne.io.read_raw_brainvision(
    "sub-001/eeg/sub-001_task-nback_eeg.vhdr",
    preload=True
)

# Keep a copy of the original
raw_filtered = raw.copy()

# Apply a 1–40 Hz band-pass filter
raw_filtered.filter(
    l_freq=1.0,
    h_freq=40.0
)

# Remove annotations from the visualization
raw_filtered.set_annotations(mne.Annotations([], [], []))

# Plot 5 seconds of Fz before filtering
raw.plot(
    picks=["Fz"],
    duration=5,
    start=100,
    n_channels=1
)

# Plot 5 seconds of Fz after filtering
raw_filtered.plot(
    picks=["Fz"],
    duration=5,
    start=100,
    n_channels=1
)

plt.show()
