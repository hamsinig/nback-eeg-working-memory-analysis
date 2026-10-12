import pandas as pd
import matplotlib.pyplot as plt
import mne
from pathlib import Path

# ---------------------------------------------------------
# INPUT FILE
# ---------------------------------------------------------
# Create a CSV named electrode_alpha_results.csv.
#
# Required columns:
# electrode, alpha_2back, alpha_4back, p_fdr
#
# The script calculates:
# alpha_change = alpha_4back - alpha_2back
#
# Electrode labels should preferably be:
# Fp1, Fp2, F3, F4, F7, F8, Fz, C3, C4, Cz,
# T3, T4, T5, T6, P3, P4, Pz, O1, O2
# ---------------------------------------------------------

FILE = Path("electrode_alpha_results.csv")

if not FILE.exists():
    raise FileNotFoundError(
        "electrode_alpha_results.csv was not found. "
        "Put it in the same folder as this script."
    )

df = pd.read_csv(FILE)

required = {"electrode", "alpha_2back", "alpha_4back", "p_fdr"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

df["alpha_change"] = df["alpha_4back"] - df["alpha_2back"]

# MNE's standard montage uses modern aliases for several older labels.
rename = {
    "T3": "T7",
    "T4": "T8",
    "T5": "P7",
    "T6": "P8",
}

plot_names = [rename.get(x, x) for x in df["electrode"]]

montage = mne.channels.make_standard_montage("standard_1020")
available = montage.get_positions()["ch_pos"]

missing_pos = [ch for ch in plot_names if ch not in available]
if missing_pos:
    raise ValueError(
        f"These electrodes were not found in the standard_1020 montage: {missing_pos}"
    )

values = df["alpha_change"].to_numpy()
mask = (df["p_fdr"] <= 0.05).to_numpy()

# Build an EvokedArray only to reuse MNE's topomap plotting.
info = mne.create_info(plot_names, sfreq=250, ch_types="eeg")
info.set_montage(montage)

evoked = mne.EvokedArray(values[:, None], info, tmin=0)

fig, ax = plt.subplots(figsize=(6, 5))

im, _ = mne.viz.plot_topomap(
    evoked.data[:, 0],
    evoked.info,
    axes=ax,
    show=False,
    contours=0,
    sensors=True,
    mask=mask,
    mask_params=dict(marker="o", markerfacecolor="none",
                     markeredgecolor="black", linewidth=1.5, markersize=8)
)

ax.set_title("Alpha change: 4-back − 2-back\nBlack circles = FDR-significant electrodes")

cbar = fig.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label("Alpha log-ratio difference")

plt.tight_layout()
plt.savefig("Figure_5_alpha_topomap.png", dpi=300, bbox_inches="tight")
plt.show()
