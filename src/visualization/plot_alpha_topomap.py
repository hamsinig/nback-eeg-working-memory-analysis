import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne

# ---------------------------------------------------------
# Load spatial statistical results
# ---------------------------------------------------------

FILE = "final_preprocessed/alpha_spatial_2vs4_fdr.csv"

df = pd.read_csv(FILE)

# ---------------------------------------------------------
# Get channel names and effect values
# ---------------------------------------------------------

channels = df["channel"].tolist()

effects = df["mean_difference_4minus2"].values

significant = df["significant_fdr"].values.astype(bool)

# ---------------------------------------------------------
# Create MNE info with standard 10-20 montage
# ---------------------------------------------------------

info = mne.create_info(
    ch_names=channels,
    sfreq=250,
    ch_types="eeg"
)

montage = mne.channels.make_standard_montage("standard_1020")

info.set_montage(montage)

# ---------------------------------------------------------
# Plot topographic map
# ---------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 7))

im, _ = mne.viz.plot_topomap(
    effects,
    info,
    axes=ax,
    show=False,
    contours=0,
    names=[
        ch if sig else ""
        for ch, sig in zip(channels, significant)
    ],
    sensors=True
)

# ---------------------------------------------------------
# Mark significant electrodes
# ---------------------------------------------------------

pos = np.array([
    info["chs"][i]["loc"][:2]
    for i in range(len(channels))
])

# The 2D positions used by MNE's topomap are not directly
# the raw x/y coordinates above, so use MNE's plotting
# output for labels and add a title.

ax.set_title(
    "Alpha log-ratio difference: 4-back − 2-back",
    fontsize=14
)

cbar = plt.colorbar(im, ax=ax, shrink=0.75)
cbar.set_label("Alpha log-ratio difference")

plt.tight_layout()

OUTPUT = "final_preprocessed/alpha_topomap_4minus2.png"

plt.savefig(
    OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:")
print(OUTPUT)

print()
print("FDR-significant channels:")
print(
    df[df["significant_fdr"]]["channel"].tolist()
)
