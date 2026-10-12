import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD DATA
# ============================================================

FILE = "final_preprocessed/PSD_channel_condition_summary.csv"

df = pd.read_csv(FILE)


# ============================================================
# CONDITION ORDER
# ============================================================

condition_order = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]


# ============================================================
# CHANNEL ORDER
# ============================================================

channel_order = [
    "Fp1",
    "Fp2",
    "F7",
    "F3",
    "Fz",
    "F4",
    "F8",
    "T3",
    "C3",
    "Cz",
    "C4",
    "T4",
    "T5",
    "P3",
    "Pz",
    "P4",
    "T6",
    "O1",
    "O2"
]


# ============================================================
# BAND INFORMATION
# ============================================================

bands = {
    "theta_power_uv2": "Theta",
    "alpha_power_uv2": "Alpha",
    "beta_power_uv2": "Beta"
}


# ============================================================
# CREATE ONE HEATMAP PER BAND
# ============================================================

for band_column, band_name in bands.items():

    matrix = (
        df.pivot(
            index="channel",
            columns="condition",
            values=band_column
        )
        .reindex(channel_order)
        .reindex(columns=condition_order)
    )

    plt.figure(figsize=(8, 10))

    plt.imshow(
        matrix.values,
        aspect="auto"
    )

    plt.xticks(
        range(4),
        condition_order
    )

    plt.yticks(
        range(len(channel_order)),
        channel_order
    )

    plt.xlabel("Working-memory demand")
    plt.ylabel("EEG channel")

    plt.title(
        f"{band_name} Power Across N-back Conditions"
    )

    plt.colorbar(
        label=f"{band_name} power (µV²)"
    )

    plt.tight_layout()

    plt.show()
