import os
import numpy as np
import pandas as pd
import mne

# =========================================================
# SETTINGS
# =========================================================

PARTICIPANTS = [
    "sub-001",
    "sub-002",
    "sub-003",
    "sub-004",
    "sub-005",
    "sub-006",
    "sub-007",
    "sub-008",
    "sub-009",
    "sub-010",
    "sub-011",
    "sub-012",
    "sub-014",
    "sub-015",
    "sub-016",
    "sub-018",
    "sub-019",
    "sub-020",
]

TRIAL_TYPES = [
    "1-back",
    "2-back",
    "3-back",
    "4-back",
]

TMIN = -0.2
TMAX = 1.0

OUTPUT_DIR = "final_preprocessed"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# VISUALLY INSPECTED WIDESPREAD CANDIDATES TO KEEP
# =========================================================

KEEP_CANDIDATES = {
    ("sub-008", 88),
    ("sub-008", 89),
    ("sub-008", 326),
    ("sub-008", 336),
    ("sub-008", 337),
    ("sub-011", 301),
}


# =========================================================
# LOAD WIDESPREAD ARTIFACT CANDIDATES
# =========================================================

candidate_file = "widespread_candidates.csv"

if not os.path.exists(candidate_file):
    raise FileNotFoundError(
        f"Could not find {candidate_file}"
    )

candidates = pd.read_csv(candidate_file)

candidates["epoch_index"] = (
    candidates["epoch_index"].astype(int)
)


# =========================================================
# ALL CANDIDATES EXCEPT THE SIX KEPT ONES ARE REJECTED
# =========================================================

REJECT_CANDIDATES = set()

for _, row in candidates.iterrows():

    participant = row["participant"]
    epoch_index = int(row["epoch_index"])

    if (participant, epoch_index) not in KEEP_CANDIDATES:

        REJECT_CANDIDATES.add(
            (participant, epoch_index)
        )


print("=" * 70)
print("FINAL EEG PREPROCESSING")
print("=" * 70)

print(f"Participants: {len(PARTICIPANTS)}")
print(f"Widespread candidates: {len(candidates)}")
print(f"Candidates kept: {len(KEEP_CANDIDATES)}")
print(f"Candidates rejected: {len(REJECT_CANDIDATES)}")

print()


# =========================================================
# SUMMARY
# =========================================================

summary = []


# =========================================================
# PROCESS EACH PARTICIPANT
# =========================================================

for participant in PARTICIPANTS:

    print()
    print("=" * 70)
    print(f"PROCESSING {participant}")
    print("=" * 70)

    # -----------------------------------------------------
    # FILE PATHS
    # -----------------------------------------------------

    vhdr = (
        f"{participant}/eeg/"
        f"{participant}_task-nback_eeg.vhdr"
    )

    events_file = (
        f"{participant}/eeg/"
        f"{participant}_task-nback_events.tsv"
    )

    if not os.path.exists(vhdr):
        print(f"ERROR: Missing EEG file: {vhdr}")
        continue

    if not os.path.exists(events_file):
        print(f"ERROR: Missing events file: {events_file}")
        continue

    # -----------------------------------------------------
    # LOAD RAW EEG
    # -----------------------------------------------------

    raw = mne.io.read_raw_brainvision(
        vhdr,
        preload=True,
        verbose=False
    )

    print(
        f"Raw data: "
        f"{raw.info['nchan']} channels, "
        f"{raw.n_times} samples"
    )

    # -----------------------------------------------------
    # DATASET-SPECIFIC SCALING CORRECTION
    #
    # The BrainVision data for this dataset required
    # conversion using x 1e-7 to obtain realistic EEG
    # amplitudes.
    # -----------------------------------------------------

    raw._data *= 1e-7

    print("Applied EEG scaling correction: x 1e-7")

    # -----------------------------------------------------
    # KEEP EEG CHANNELS
    # -----------------------------------------------------

    raw.pick("eeg")

    print(
        f"EEG channels retained: "
        f"{len(raw.ch_names)}"
    )

    # -----------------------------------------------------
    # RENAME FP1 / FP2 FOR STANDARD MONTAGE
    # -----------------------------------------------------

    rename_dict = {}

    if "FP1" in raw.ch_names:
        rename_dict["FP1"] = "Fp1"

    if "FP2" in raw.ch_names:
        rename_dict["FP2"] = "Fp2"

    if rename_dict:
        raw.rename_channels(rename_dict)

    # -----------------------------------------------------
    # STANDARD 10-20 MONTAGE
    # -----------------------------------------------------

    montage = mne.channels.make_standard_montage(
        "standard_1020"
    )

    raw.set_montage(
        montage,
        on_missing="ignore"
    )

    # -----------------------------------------------------
    # BAND-PASS FILTER
    # -----------------------------------------------------

    raw.filter(
        1.0,
        40.0,
        verbose=False
    )

    print("Applied 1–40 Hz band-pass filter")

    # =====================================================
    # ICA
    # =====================================================

    print("Running ICA...")

    ica = mne.preprocessing.ICA(
        n_components=len(raw.ch_names),
        method="fastica",
        random_state=42,
        max_iter="auto"
    )

    ica.fit(
        raw,
        decim=3,
        verbose=False
    )

    # -----------------------------------------------------
    # IDENTIFY MOST LIKELY OCULAR COMPONENT
    #
    # We use the component with the highest mean absolute
    # correlation with Fp1/Fp2.
    # -----------------------------------------------------

    sources = (
        ica.get_sources(raw)
        .get_data()
    )

    frontal_channels = []

    if "Fp1" in raw.ch_names:
        frontal_channels.append("Fp1")

    if "Fp2" in raw.ch_names:
        frontal_channels.append("Fp2")

    frontal_indices = [
        raw.ch_names.index(ch)
        for ch in frontal_channels
    ]

    frontal_data = raw.get_data(
        picks=frontal_indices
    )

    correlations = []

    for component in range(
        sources.shape[0]
    ):

        component_signal = sources[
            component
        ]

        component_corrs = []

        for channel_signal in frontal_data:

            corr = np.corrcoef(
                component_signal,
                channel_signal
            )[0, 1]

            component_corrs.append(
                abs(corr)
            )

        correlations.append(
            np.mean(component_corrs)
        )

    ocular_component = int(
        np.argmax(correlations)
    )

    ocular_correlation = correlations[
        ocular_component
    ]

    print(
        f"Selected ICA component: "
        f"ICA{ocular_component:03d}"
    )

    print(
        f"Mean absolute frontal correlation: "
        f"{ocular_correlation:.3f}"
    )

    # -----------------------------------------------------
    # REMOVE SELECTED ICA COMPONENT
    # -----------------------------------------------------

    ica.exclude = [
        ocular_component
    ]

    raw_clean = raw.copy()

    ica.apply(
        raw_clean,
        verbose=False
    )

    print(
        f"Removed ICA{ocular_component:03d}"
    )

    # =====================================================
    # LOAD EVENTS
    # =====================================================

    events_df = pd.read_csv(
        events_file,
        sep="\t"
    )

    # -----------------------------------------------------
    # KEEP ONLY REAL N-BACK TRIAL TYPES
    # -----------------------------------------------------

    events_df = events_df[
        events_df["trial_type"].isin(
            TRIAL_TYPES
        )
    ].copy()

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # Keep ONLY events explicitly marked
    # istutorial == False.
    #
    # Do NOT use fillna(False), because the dataset
    # contains malformed trailing events with NaN
    # in istutorial. Those are not experimental trials.
    # -----------------------------------------------------

    if "istutorial" in events_df.columns:

        events_df = events_df[
            events_df["istutorial"] == False
        ].copy()

    else:

        raise ValueError(
            f"{participant}: "
            "istutorial column not found."
        )

    # -----------------------------------------------------
    # SORT BY ONSET
    # -----------------------------------------------------

    events_df = (
        events_df
        .sort_values("onset")
        .reset_index(drop=True)
    )

    print(
        f"Experimental trials found: "
        f"{len(events_df)}"
    )

    # -----------------------------------------------------
    # CHECK THAT WE HAVE 100 OF EACH CONDITION
    # -----------------------------------------------------

    counts = (
        events_df["trial_type"]
        .value_counts()
    )

    print("Trial counts:")

    for trial_type in TRIAL_TYPES:

        count = counts.get(
            trial_type,
            0
        )

        print(
            f"  {trial_type}: {count}"
        )

        if count != 100:

            raise ValueError(
                f"{participant}: "
                f"{trial_type} has {count} trials "
                f"instead of 100."
            )

    # -----------------------------------------------------
    # FINAL CHECK
    # -----------------------------------------------------

    if len(events_df) != 400:

        raise ValueError(
            f"{participant}: "
            f"Expected 400 trials, "
            f"found {len(events_df)}."
        )

    # =====================================================
    # CREATE MNE EVENT ARRAY
    # =====================================================

    event_id = {
        "1-back": 1,
        "2-back": 2,
        "3-back": 3,
        "4-back": 4,
    }

    event_samples = np.round(
        events_df["onset"].values
        * raw_clean.info["sfreq"]
    ).astype(int)

    event_codes = np.array([
        event_id[t]
        for t in events_df["trial_type"]
    ])

    events = np.column_stack([
        event_samples,
        np.zeros(
            len(events_df),
            dtype=int
        ),
        event_codes
    ])

    # =====================================================
    # CREATE EPOCHS
    # =====================================================

    epochs = mne.Epochs(
        raw_clean,
        events,
        event_id=event_id,
        tmin=TMIN,
        tmax=TMAX,
        baseline=(TMIN, 0),
        preload=True,
        reject_by_annotation=False,
        verbose=False
    )

    print(
        f"Epochs created: {len(epochs)}"
    )

    # -----------------------------------------------------
    # MAKE SURE EPOCH COUNT IS 400
    # -----------------------------------------------------

    if len(epochs) != 400:

        raise ValueError(
            f"{participant}: "
            f"Expected 400 epochs, "
            f"created {len(epochs)}."
        )

    # =====================================================
    # FIND ARTIFACT EPOCHS TO REJECT
    # =====================================================

    participant_rejections = [
        epoch_index
        for participant_id, epoch_index
        in REJECT_CANDIDATES
        if participant_id == participant
    ]

    # Make sure indices are valid
    participant_rejections = [
        i
        for i in participant_rejections
        if i < len(epochs)
    ]

    # -----------------------------------------------------
    # REJECT CONFIRMED ARTIFACTS
    # -----------------------------------------------------

    if participant_rejections:

        print(
            f"Rejecting "
            f"{len(participant_rejections)} "
            f"confirmed artifact epochs:"
        )

        print(
            participant_rejections
        )

        epochs.drop(
            participant_rejections,
            reason="confirmed_widespread_artifact"
        )

    else:

        print(
            "No confirmed widespread artifacts "
            "for this participant."
        )

    # =====================================================
    # SAVE CLEAN EPOCHS
    # =====================================================

    output_file = os.path.join(
        OUTPUT_DIR,
        f"{participant}_clean_epochs.fif"
    )

    epochs.save(
        output_file,
        overwrite=True,
        verbose=False
    )

    print(
        f"Saved: {output_file}"
    )

    # =====================================================
    # COUNT REMAINING TRIALS
    # =====================================================

    remaining_codes = (
        epochs.events[:, 2]
    )

    participant_summary = {
        "participant": participant,
        "original_epochs": 400,
        "rejected_epochs": len(
            participant_rejections
        ),
        "remaining_epochs": len(
            epochs
        ),
        "ica_component_removed":
            ocular_component,
        "ica_frontal_correlation":
            ocular_correlation,
    }

    for trial_type, code in event_id.items():

        participant_summary[
            f"{trial_type}_remaining"
        ] = int(
            np.sum(
                remaining_codes == code
            )
        )

    summary.append(
        participant_summary
    )


# =========================================================
# SAVE FINAL SUMMARY
# =========================================================

summary_df = pd.DataFrame(
    summary
)

summary_file = os.path.join(
    OUTPUT_DIR,
    "final_preprocessing_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


# =========================================================
# FINAL OUTPUT
# =========================================================

print()
print("=" * 70)
print("FINAL PREPROCESSING COMPLETE")
print("=" * 70)

print()

print(
    summary_df.to_string(
        index=False
    )
)

print()
print(
    f"Summary saved to: "
    f"{summary_file}"
)

print(
    f"Clean epochs saved in: "
    f"{OUTPUT_DIR}/"
)
