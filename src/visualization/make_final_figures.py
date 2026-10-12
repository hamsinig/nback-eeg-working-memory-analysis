import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import wilcoxon, spearmanr
from statsmodels.stats.multitest import multipletests

import mne


# ============================================================
# SETTINGS
# ============================================================

# This script is being run from:
# src/visualization/

RESULTS_DIR = "../../results"
TABLES_DIR = os.path.join(RESULTS_DIR, "tables")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")

os.makedirs(FIGURES_DIR, exist_ok=True)

CONDITIONS = [
    "1-back",
    "2-back",
    "3-back",
    "4-back"
]


# ============================================================
# FIGURE 1
# EXPERIMENT / ANALYSIS PIPELINE
# ============================================================

print("\nCreating Figure 1...")

fig, ax = plt.subplots(figsize=(14, 5))
ax.axis("off")

boxes = [
    (
        0.03,
        0.50,
        "N-back task\n1-back → 4-back"
    ),
    (
        0.22,
        0.50,
        "EEG recording\n19 channels\n250 Hz"
    ),
    (
        0.41,
        0.50,
        "Preprocessing\n1–40 Hz band-pass\nICA + QC"
    ),
    (
        0.60,
        0.50,
        "Epoching\n−0.2 → +1.0 s\nTask period: 0–1 s"
    ),
    (
        0.79,
        0.50,
        "Welch PSD\nTheta / Alpha / Beta"
    )
]

for x, y, text in boxes:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=12,
        bbox=dict(
            boxstyle="round,pad=0.6",
            linewidth=1.5
        ),
        transform=ax.transAxes
    )

# Arrows between boxes
for i in range(len(boxes) - 1):

    x1 = boxes[i][0] + 0.065
    x2 = boxes[i + 1][0] - 0.065

    ax.annotate(
        "",
        xy=(x2, 0.50),
        xytext=(x1, 0.50),
        xycoords=ax.transAxes,
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.5
        )
    )

# Statistical analysis box
ax.text(
    0.50,
    0.17,
    "Statistical analysis\n"
    "Condition effects → spatial effects → "
    "individual differences → EEG–behavior association",
    ha="center",
    va="center",
    fontsize=12,
    bbox=dict(
        boxstyle="round,pad=0.6",
        linewidth=1.5
    ),
    transform=ax.transAxes
)

# Arrow down to statistics
ax.annotate(
    "",
    xy=(0.50, 0.30),
    xytext=(0.50, 0.43),
    xycoords=ax.transAxes,
    arrowprops=dict(
        arrowstyle="->",
        linewidth=1.5
    )
)

ax.set_title(
    "EEG analysis pipeline for investigating N-back working-memory demand",
    fontsize=15,
    pad=20
)

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_1_pipeline.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 2
# BEHAVIORAL ACCURACY
# ============================================================

print("Creating Figure 2...")

behavior = pd.read_csv(
    os.path.join(
        TABLES_DIR,
        "behavioral_audit_summary.csv"
    )
)

behavior["condition"] = pd.Categorical(
    behavior["condition"],
    categories=CONDITIONS,
    ordered=True
)

behavior_wide = behavior.pivot(
    index="subject",
    columns="condition",
    values="accuracy_mean"
)

fig, ax = plt.subplots(
    figsize=(8, 6)
)

# Individual participants
for subject in behavior_wide.index:

    ax.plot(
        CONDITIONS,
        behavior_wide.loc[
            subject,
            CONDITIONS
        ],
        marker="o",
        alpha=0.12,
        linewidth=1
    )

# Group mean ± SEM
means = behavior_wide[
    CONDITIONS
].mean()

sem = behavior_wide[
    CONDITIONS
].sem()

ax.errorbar(
    CONDITIONS,
    means,
    yerr=sem,
    marker="o",
    linewidth=3,
    capsize=5,
    label="Group mean ± SEM"
)

ax.set_xlabel(
    "N-back condition"
)

ax.set_ylabel(
    "Accuracy"
)

ax.set_title(
    "Behavioral performance across N-back conditions"
)

ax.set_ylim(
    0,
    1
)

ax.grid(
    axis="y",
    alpha=0.2
)

ax.legend()

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_2_behavior.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 3
# ALPHA POWER ACROSS WORKLOAD
# ============================================================

print("Creating Figure 3...")

alpha = pd.read_csv(
    os.path.join(
        TABLES_DIR,
        "PSD_participant_condition_logratio.csv"
    )
)

alpha["condition"] = pd.Categorical(
    alpha["condition"],
    categories=CONDITIONS,
    ordered=True
)

alpha_wide = alpha.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)

fig, ax = plt.subplots(
    figsize=(8, 6)
)

# Individual participant trajectories
for subject in alpha_wide.index:

    ax.plot(
        CONDITIONS,
        alpha_wide.loc[
            subject,
            CONDITIONS
        ],
        marker="o",
        alpha=0.20,
        linewidth=1
    )

# Group mean ± SEM
alpha_means = alpha_wide[
    CONDITIONS
].mean()

alpha_sem = alpha_wide[
    CONDITIONS
].sem()

ax.errorbar(
    CONDITIONS,
    alpha_means,
    yerr=alpha_sem,
    marker="o",
    linewidth=2.5,
    capsize=4,
    label="Group mean ± SEM"
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1
)

ax.set_xlabel(
    "N-back condition"
)

ax.set_ylabel(
    "Alpha log-ratio relative to 1-back"
)

ax.set_title(
    "Alpha-band modulation across N-back conditions"
)

ax.legend()

ax.grid(
    axis="y",
    alpha=0.2
)

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_3_alpha_workload.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 4
# ALPHA 4-BACK − 2-BACK SPATIAL EFFECT
# ============================================================

print("Creating Figure 4...")

spatial = pd.read_csv(
    os.path.join(
        TABLES_DIR,
        "PSD_log_ratio_from_1back.csv"
    )
)

# Keep only 2-back and 4-back
spatial = spatial[
    spatial["condition"].isin(
        ["2-back", "4-back"]
    )
].copy()

# Participant × channel × condition
spatial_wide = spatial.pivot_table(
    index=["subject", "channel"],
    columns="condition",
    values="alpha_log_ratio"
).reset_index()

channels = sorted(
    spatial_wide["channel"].unique()
)

# ------------------------------------------------------------
# Channel-wise Wilcoxon tests
# ------------------------------------------------------------

fdr_results = []

for channel in channels:

    channel_data = spatial_wide[
        spatial_wide["channel"] == channel
    ]

    x = channel_data["2-back"].values
    y = channel_data["4-back"].values

    stat, p = wilcoxon(
        x,
        y,
        alternative="two-sided"
    )

    difference = y - x

    fdr_results.append({
        "channel": channel,
        "wilcoxon_statistic": stat,
        "p_raw": p,
        "mean_difference": difference.mean()
    })

fdr_results = pd.DataFrame(
    fdr_results
)

# ------------------------------------------------------------
# FDR correction across 19 electrodes
# ------------------------------------------------------------

reject, p_fdr, _, _ = multipletests(
    fdr_results["p_raw"],
    alpha=0.05,
    method="fdr_bh"
)

fdr_results["p_fdr"] = p_fdr
fdr_results["significant"] = reject

# Save spatial statistics
fdr_results.to_csv(
    os.path.join(
        TABLES_DIR,
        "FINAL_alpha_spatial_statistics.csv"
    ),
    index=False
)

# ------------------------------------------------------------
# Prepare channel names
# ------------------------------------------------------------

rename_map = {
    "FP1": "Fp1",
    "FP2": "Fp2"
}

plot_channels = [
    rename_map.get(ch, ch)
    for ch in fdr_results["channel"]
]

values = fdr_results[
    "mean_difference"
].values

significant = fdr_results[
    "significant"
].values

# ------------------------------------------------------------
# Standard 10-20 montage
# ------------------------------------------------------------

montage = mne.channels.make_standard_montage(
    "standard_1020"
)

info = mne.create_info(
    ch_names=plot_channels,
    sfreq=250,
    ch_types="eeg"
)

info.set_montage(
    montage
)

# ------------------------------------------------------------
# Symmetric color scale centered at zero
# ------------------------------------------------------------

max_abs = np.max(
    np.abs(values)
)

# ------------------------------------------------------------
# Create figure
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(8, 7)
)

# ------------------------------------------------------------
# Plot topomap
# ------------------------------------------------------------

im, _ = mne.viz.plot_topomap(
    values,
    info,
    axes=ax,
    show=False,
    contours=0,
    sensors=True,
    cmap="RdBu_r",
    vlim=(-max_abs, max_abs),

    # Mark statistically significant electrodes
    mask=significant,

    mask_params=dict(
        marker="o",
        markerfacecolor="none",
        markeredgecolor="black",
        linewidth=0,
        markersize=12
    )
)

ax.set_title(
    "Alpha power difference: 4-back − 2-back",
    fontsize=15,
    pad=15
)

# Colorbar
cbar = fig.colorbar(
    im,
    ax=ax,
    shrink=0.75,
    pad=0.05
)

cbar.set_label(
    "Mean alpha log-ratio difference"
)

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_4_alpha_topomap.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 5
# INDIVIDUAL ALPHA RESPONSES
# ============================================================

print("Creating Figure 5...")

individual_alpha = alpha_wide.copy()

individual_alpha[
    "delta_alpha"
] = (
    individual_alpha[
        "4-back"
    ]
    -
    individual_alpha[
        "2-back"
    ]
)

individual_alpha = (
    individual_alpha[
        ["delta_alpha"]
    ]
    .sort_values(
        "delta_alpha"
    )
)

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.bar(
    individual_alpha.index,
    individual_alpha[
        "delta_alpha"
    ]
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1
)

ax.set_xlabel(
    "Participant"
)

ax.set_ylabel(
    "Alpha change (4-back − 2-back)"
)

ax.set_title(
    "Individual alpha responses to increased working-memory demand"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_5_individual_alpha.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FIGURE 6
# ALPHA-BEHAVIOR ASSOCIATION
# ============================================================

print("Creating Figure 6...")

behavior_24 = behavior[
    behavior["condition"].isin(
        [
            "2-back",
            "4-back"
        ]
    )
].copy()

behavior_corr = behavior_24.pivot(
    index="subject",
    columns="condition",
    values="accuracy_mean"
)

behavior_corr[
    "delta_accuracy"
] = (
    behavior_corr[
        "4-back"
    ]
    -
    behavior_corr[
        "2-back"
    ]
)

# Combine EEG and behavior
corr_data = pd.DataFrame(
    {
        "delta_alpha":
            alpha_wide[
                "4-back"
            ]
            -
            alpha_wide[
                "2-back"
            ],

        "delta_accuracy":
            behavior_corr[
                "4-back"
            ]
            -
            behavior_corr[
                "2-back"
            ]
    }
).dropna()

# Spearman correlation
rho, p_value = spearmanr(
    corr_data[
        "delta_alpha"
    ],
    corr_data[
        "delta_accuracy"
    ]
)

fig, ax = plt.subplots(
    figsize=(8, 6)
)

ax.scatter(
    corr_data[
        "delta_alpha"
    ],
    corr_data[
        "delta_accuracy"
    ],
    s=70
)

# Reference lines
ax.axhline(
    0,
    linestyle="--",
    linewidth=1
)

ax.axvline(
    0,
    linestyle="--",
    linewidth=1
)

ax.set_xlabel(
    "Alpha change (4-back − 2-back)"
)

ax.set_ylabel(
    "Accuracy change (4-back − 2-back)"
)

ax.set_title(
    f"Alpha–behavior association\n"
    f"Spearman ρ = {rho:.3f}, p = {p_value:.3f}"
)

ax.grid(
    alpha=0.2
)

plt.tight_layout()

fig.savefig(
    os.path.join(
        FIGURES_DIR,
        "FINAL_FIGURE_6_alpha_behavior.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("FINAL FIGURES CREATED")
print("=" * 70)

files = [
    "FINAL_FIGURE_1_pipeline.png",
    "FINAL_FIGURE_2_behavior.png",
    "FINAL_FIGURE_3_alpha_workload.png",
    "FINAL_FIGURE_4_alpha_topomap.png",
    "FINAL_FIGURE_5_individual_alpha.png",
    "FINAL_FIGURE_6_alpha_behavior.png",
    "FINAL_alpha_spatial_statistics.csv"
]

for filename in files:

    print(
        os.path.join(
            FIGURES_DIR,
            filename
        )
    )

print()

print(
    f"Spearman alpha-behavior rho = "
    f"{rho:.4f}"
)

print(
    f"Spearman alpha-behavior p = "
    f"{p_value:.6f}"
)

print()
print("DONE.")