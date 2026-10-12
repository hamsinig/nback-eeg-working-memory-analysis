
N-BACK EEG REPORT FIGURE SCRIPTS
================================

Run these with Python 3.11.

Install packages:
    pip install matplotlib pandas scipy mne

FIGURES
-------
01_analysis_pipeline.py
    No input data required.
    Produces Figure_1_EEG_analysis_pipeline.png

02_behavioral_accuracy.py
    Uses the exact mean accuracy values reported in the analysis.
    Produces Figure_2_behavioral_accuracy.png

03_frequency_bands.py
    Uses the exact mean theta/alpha/beta log-ratio values reported.
    Produces Figure_3_frequency_band_changes.png

04_alpha_2back_vs_4back.py
    Requires participant_level_results.csv

06_alpha_behavior_scatter.py
    Uses the same participant_level_results.csv

05_alpha_topomap.py
    Requires electrode_alpha_results.csv

PARTICIPANT CSV
---------------
Filename:
    participant_level_results.csv

Required columns:
    participant
    alpha_2back
    alpha_4back
    accuracy_2back
    accuracy_4back

Example structure:

participant,alpha_2back,alpha_4back,accuracy_2back,accuracy_4back
sub-001,...
sub-002,...
...

The actual values must come from your analysis. Do not enter estimated values.

ELECTRODE CSV
-------------
Filename:
    electrode_alpha_results.csv

Required columns:
    electrode
    alpha_2back
    alpha_4back
    p_fdr

Example structure:

electrode,alpha_2back,alpha_4back,p_fdr
Fp1,...
Fp2,...
F3,...
...

The script calculates:
    alpha_change = alpha_4back - alpha_2back

and marks electrodes with:
    p_fdr <= 0.05

IMPORTANT
---------
Figures 4, 5 and 6 cannot be correctly generated from the summary statistics
alone. They require the participant-level/electrode-level data used in your
original analysis.

The scripts intentionally stop with an error if the required data are absent,
rather than inventing or reconstructing individual values.
