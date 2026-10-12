import pandas as pd
import matplotlib.pyplot as plt

FILE = "final_preprocessed/PSD_participant_condition_logratio.csv"

df = pd.read_csv(FILE)

# ---------------------------------------------------------
# Get 2-back and 4-back alpha values for each participant
# ---------------------------------------------------------

wide = df.pivot(
    index="subject",
    columns="condition",
    values="alpha_log_ratio"
)

wide = wide[["2-back", "4-back"]].copy()

# 4-back minus 2-back
wide["alpha_response_4minus2"] = (
    wide["4-back"] - wide["2-back"]
)

# Sort participants by response
wide = wide.sort_values("alpha_response_4minus2")

print("=" * 70)
print("INDIVIDUAL ALPHA RESPONSE — 4-BACK VS 2-BACK")
print("=" * 70)

print()

print(wide.to_string())

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

response = wide["alpha_response_4minus2"]

print(f"Participants = {len(response)}")
print(f"Mean response = {response.mean():.6f}")
print(f"Median response = {response.median():.6f}")
print(f"Minimum response = {response.min():.6f}")
print(f"Maximum response = {response.max():.6f}")

print()
print(
    f"Participants with positive response: "
    f"{(response > 0).sum()}/{len(response)}"
)

print(
    f"Participants with negative response: "
    f"{(response < 0).sum()}/{len(response)}"
)

print(
    f"Participants with zero response: "
    f"{(response == 0).sum()}/{len(response)}"
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

output = (
    "final_preprocessed/"
    "individual_alpha_2vs4_response.csv"
)

wide.reset_index().to_csv(output, index=False)

print()
print("Saved:")
print(output)

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------

plt.figure(figsize=(11, 6))

plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

plt.bar(
    wide.index,
    wide["alpha_response_4minus2"]
)

plt.xlabel("Participant")
plt.ylabel("Alpha log-ratio difference (4-back − 2-back)")
plt.title(
    "Individual alpha response: 4-back vs 2-back"
)

plt.xticks(rotation=45)

plt.tight_layout()

plot_output = (
    "final_preprocessed/"
    "individual_alpha_2vs4_response.png"
)

plt.savefig(
    plot_output,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:")
print(plot_output)
