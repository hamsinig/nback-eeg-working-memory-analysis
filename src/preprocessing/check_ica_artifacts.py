import mne
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
# 2. Keep only EEG channels
# --------------------------------------------------

raw.pick("eeg")

print("\nAfter keeping EEG channels:")
print(raw)

# --------------------------------------------------
# 3. Fix channel names for standard montage
# --------------------------------------------------

raw.rename_channels({
    "FP1": "Fp1",
    "FP2": "Fp2"
})

# --------------------------------------------------
# 4. Apply standard 10-20 montage
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

ica.fit(
    raw,
    decim=3
)

print("\nICA fitted.")
print(ica)

# --------------------------------------------------
# 8. Compare ICA components with frontal electrodes
# --------------------------------------------------

print("\nCorrelation with frontal electrodes:")

scores_fp1 = ica.score_sources(
    raw,
    target="Fp1",
    score_func="pearsonr",
    l_freq=1.0,
    h_freq=10.0,
    start=100,
    stop=110,
    verbose=False
)

scores_fp2 = ica.score_sources(
    raw,
    target="Fp2",
    score_func="pearsonr",
    l_freq=1.0,
    h_freq=10.0,
    start=100,
    stop=110,
    verbose=False
)

for component in [0, 2, 8, 10]:

    print(
        f"ICA{component:03d}: "
        f"Fp1 = {scores_fp1[component]:.3f}, "
        f"Fp2 = {scores_fp2[component]:.3f}"
    )
