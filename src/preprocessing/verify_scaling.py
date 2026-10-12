import mne
import numpy as np

filename = "sub-001/eeg/sub-001_task-nback_eeg.vhdr"

raw = mne.io.read_raw_brainvision(
    filename,
    preload=True
)

print("Before correction:")
fz = raw.get_data(picks=["Fz"])[0]

print("Mean absolute:", np.abs(fz).mean())
print("Std:", np.std(fz))

# Dataset-specific BrainVision scaling correction
scale = 0.1 * 1e-6

raw._data *= scale

print("\nAfter correction:")
fz = raw.get_data(picks=["Fz"])[0]

print("Mean absolute:", np.abs(fz).mean())
print("Std:", np.std(fz))

print("\nIn microvolts:")
fz_uv = fz * 1e6

print("Mean:", np.mean(fz_uv))
print("Std:", np.std(fz_uv))
print("1%:", np.percentile(fz_uv, 1))
print("5%:", np.percentile(fz_uv, 5))
print("50%:", np.percentile(fz_uv, 50))
print("95%:", np.percentile(fz_uv, 95))
print("99%:", np.percentile(fz_uv, 99))
