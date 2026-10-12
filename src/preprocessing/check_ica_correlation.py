import mne
import numpy as np
from mne.preprocessing import ICA
from scipy.stats import pearsonr

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
# 2. Keep only EEG channels
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

montage = mne.channels.make_standard_montage("standard_1020")
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

ica.fit(raw, decim=3)

print("\nICA fitted.")

# --------------------------------------------------
# 8. Get ICA source signals
# --------------------------------------------------

ica_sources = ica.get_sources(raw).get_data()

print("\nICA source shape:")
print(ica_sources.shape)

# --------------------------------------------------
# 9. Get frontal electrode signals
# --------------------------------------------------

fp1 = raw.get_data(picks="Fp1")[0]
fp2 = raw.get_data(picks="Fp2")[0]

# --------------------------------------------------
# 10. Select 100–110 second window
# --------------------------------------------------

start_sample = int(100 * raw.info["sfreq"])
stop_sample = int(110 * raw.info["sfreq"])

fp1_window = fp1[start_sample:stop_sample]
fp2_window = fp2[start_sample:stop_sample]

# --------------------------------------------------
# 11. Correlate ICA components with FP1 / FP2
# --------------------------------------------------

print("\nCorrelation with frontal electrodes")
print("-----------------------------------")

for component in [0, 2, 8, 10]:

    component_signal = ica_sources[
        component,
        start_sample:stop_sample
    ]

    corr_fp1, _ = pearsonr(
        component_signal,
        fp1_window
    )

    corr_fp2, _ = pearsonr(
        component_signal,
        fp2_window
    )

    print(
        f"ICA{component:03d}: "
        f"Fp1 = {corr_fp1:.3f}, "
        f"Fp2 = {corr_fp2:.3f}"
    )
