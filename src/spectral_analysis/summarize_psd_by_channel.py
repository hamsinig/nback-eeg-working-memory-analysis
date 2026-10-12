import pandas as pd


# ============================================================
# LOAD PSD DATA
# ============================================================

FILE = "final_preprocessed/ALL_SUBJECTS_psd_band_power.csv"

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
# AVERAGE ACROSS EPOCHS
# ============================================================

channel_summary = (
    df.groupby(
        ["channel", "condition"]
    )[
        [
            "theta_power_uv2",
            "alpha_power_uv2",
            "beta_power_uv2"
        ]
    ]
    .mean()
    .reset_index()
)


# ============================================================
# ORDER CONDITIONS
# ============================================================

channel_summary["condition"] = pd.Categorical(
    channel_summary["condition"],
    categories=condition_order,
    ordered=True
)

channel_summary = channel_summary.sort_values(
    ["channel", "condition"]
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 80)
print("CHANNEL × CONDITION PSD SUMMARY")
print("=" * 80)

print(channel_summary.to_string(index=False))


# ============================================================
# SAVE
# ============================================================

output_file = (
    "final_preprocessed/"
    "PSD_channel_condition_summary.csv"
)

channel_summary.to_csv(
    output_file,
    index=False
)

print("\nSaved:")
print(output_file)

print("\nShape:")
print(channel_summary.shape)
