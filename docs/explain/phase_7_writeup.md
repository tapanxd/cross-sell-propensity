# Phase 7 — Write-up

## What was done
- `docs/summary.md`: the one-page memo for the VP. It opens with the recommendation, then covers what was found, how (one paragraph), the limits, and how to validate.
- `docs/interview_notes.md`: a 90-second spoken version, a table of every major decision with a one-line reason, and the likely interview questions with answers.
- `README.md`: the run order from raw CSV to dashboard, the repo layout, and the headline result.

## Why this way
- **The memo leads with the recommendation, not the process.** A VP reads the first three lines. The method gets one paragraph because the dashboard and the explainers hold the detail.
- **Every number in the memo comes from the held-out test set or the raw data.** Nothing about revenue, savings or "efficiency" is claimed, because there's no real customer base to measure it on. Impact is described as a method (the pilot) instead.
- **Limits are stated plainly:** one public campaign, not our customers. Channel effects are mixed up with customer mix. Labels are synthetic. Saying this unprompted reads better in an interview than being caught on it.

## Key concept: the validation plan
A model trained on one past campaign shows that a pattern **existed** in that campaign. A randomised pilot shows whether acting on it **works now**. Calling a random half of the High tier and holding the other half back gives a clean comparison, because the only difference between the two groups is the call. Adding a small random sample from Medium and Low checks the ranking itself, not just the top. That's the honest answer to "how would you know it worked?"

## Check it yourself
- Read `docs/summary.md` cold. Can you say the recommendation without looking? If not, it's not clear enough yet.
- Time yourself saying the 90-second script in `docs/interview_notes.md` out loud. Aim for 80–100 seconds.
- Every number in the memo can be found in `reports/metrics.json`, `reports/dax_check_values.md` or the EDA output of `python/01_train_score.py`.
