import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD RELATIVE-CHANGE DATA
# ============================================================

FILE = "final_preprocessed/PSD_relative_change_from_1back.csv"

df = pd.read_csv(FILE)


# ============================================================
# CONDITION ORDER
# ============================================================

condition_order = [
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
    "theta_relative_change_pct": "Theta",
    "alpha_relative_change_pct": "Alpha",
    "beta_relative_change_pct": "Beta"
}


# ============================================================
# AVERAGE ACROSS PARTICIPANTS
# ============================================================

group_summary = (
    df.groupby(
        ["channel", "condition"]
    )[list(bands.keys())]
    .mean()
    .reset_index()
)


# ============================================================
# CREATE HEATMAPS
# ============================================================

for band_column, band_name in bands.items():

    matrix = (
        group_summary
        .pivot(
            index="channel",
            columns="condition",
            values=band_column
        )
        .reindex(channel_order)
        .reindex(columns=condition_order)
    )

    plt.figure(figsize=(8, 10))

    # Center the color scale at zero
    max_abs = matrix.abs().max().max()

    plt.imshow(
        matrix.values,
        aspect="auto",
        cmap="RdBu_r",
        vmin=-max_abs,
        vmax=max_abs
    )

    plt.xticks(
        range(3),
        condition_order
    )

    plt.yticks(
        range(len(channel_order)),
        channel_order
    )

    plt.xlabel("Working-memory demand")
    plt.ylabel("EEG channel")

    plt.title(
        f"{band_name} Relative Change from 1-back"
    )

    plt.colorbar(
        label="Change from 1-back (%)"
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# SAVE GROUP SUMMARY
# ============================================================

output_file = (
    "final_preprocessed/"
    "PSD_group_relative_change_summary.csv"
)

group_summary.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)
