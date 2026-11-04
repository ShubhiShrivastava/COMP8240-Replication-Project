# COMP8240 — Text Classification Replication Project

## Project Overview

This repository contains the COMP8240 Applications of Data Science replication project at Macquarie University.

The project investigates the reproducibility and generalisation of the paper:

**Linear Classifier: An Often-Forgotten Baseline for Text Classification**

Yu-Chen Lin, Si-An Chen, Jie-Jyun Liu, and Chih-Jen Lin (ACL 2023).

Original authors' repository:
https://github.com/JamesLYC88/text_classification_baseline_code

The project reproduces the original linear classification baseline on UNFAIR-ToS, evaluates the approach on five additional public datasets, and constructs a new Australian Government Media Releases classification dataset.

## Project Objectives

1. Reproduce selected results from the original paper.
2. Compare the reproduced results with the published results.
3. Evaluate the original linear classification approach on new text classification datasets.
4. Construct and evaluate a new topic classification dataset.
5. Analyse model performance, computational efficiency, annotation reliability and limitations.

## Original Paper Replication

The original authors' code was used to reproduce the UNFAIR-ToS experiment.

| Metric       | Published Result | Replicated Result |
| ------------ | ---------------: | ----------------: |
| Micro-F1 (%) |             94.9 |           94.8702 |
| Macro-F1 (%) |             75.1 |           75.0596 |

The replication completed in approximately 3 seconds on CPU.

Replication output:
`results/preliminary_run.txt`

## Evaluation on New Datasets

The original TF-IDF and LIBLINEAR one-vs-rest linear classification approach was evaluated on six datasets.

| Dataset                              | Micro-F1 (%) | Macro-F1 (%) |
| ------------------------------------ | -----------: | -----------: |
| AG News                              |      91.9474 |      91.9330 |
| BANKING77                            |      89.5130 |      89.5039 |
| GoEmotions                           |      47.3303 |      33.7782 |
| IMDb                                 |      87.7200 |      87.7185 |
| TREC                                 |      87.8000 |      87.5229 |
| Australian Government Media Releases |      98.0000 |      97.9950 |

The experiments use the original LIBLINEAR options:

`-s 2 -B 1 -e 0.0001 -q`

The random seed is 1337 where applicable.

For single-label classification, the predicted category is selected using the highest decision score.

For GoEmotions, which is multilabel, a decision-score threshold of zero is used.

These results are not directly comparable as measures of dataset difficulty because the datasets differ in size, number of categories, label structure and task.

## Constructed Australian Government Dataset

A new topic classification dataset was constructed from Australian Government media releases.

The final dataset contains 248 documents across five categories:

| Category                | Documents |
| ----------------------- | --------: |
| Economy and Finance     |        48 |
| Education               |        52 |
| Environment and Climate |        49 |
| Foreign Affairs         |        49 |
| Health                  |        50 |

Initial topic labels were assigned using the official government portfolio or source.

Cross-class title similarity and keyword screening identified potentially ambiguous records for manual review.

Manual review resulted in three exclusions and two relabelling decisions.

The final dataset has no missing or blank required values, duplicate source URLs or duplicate exact texts.

The dataset was evaluated using a stratified 80/20 train/test split with random seed 1337.

- Training documents: 198
- Testing documents: 50
- Micro-F1: 98.0000%
- Macro-F1: 97.9950%

The small test set and potential department-specific language are limitations when interpreting the result.

## Annotation Validation

A stratified sample of 50 documents, with 10 documents from each category, was used for LLM-assisted label validation.

The second labels were compared with the original dataset labels.

Results:

- Agreement: 49/50 documents (98.00%)
- Cohen's Kappa: 0.9750
- Disagreements: 1

The disagreement concerned "Government maintains fuel security", originally labelled `environment_climate` and assigned `economy_finance` in the LLM review.

The original dataset and experiment results were retained unchanged. The disagreement was documented as a possible source-based labelling ambiguity.

These figures measure agreement between original labels and LLM-assigned labels. They do not represent human-human inter-annotator agreement or independently verified ground-truth accuracy.

## Repository Structure

- `scripts/` — data preparation and evaluation scripts
- `results/` — replication results, evaluation outputs and annotation documentation
- `data/constructed/` — constructed dataset and annotation records, where available
- `data/external/` — downloaded public datasets stored locally
- `original_code/` — original authors' code stored locally
- `README.md` — project overview and reproduction instructions

Some datasets and original-code resources may not be tracked in Git. Their availability should be checked before attempting to reproduce the experiments.

## Environment and Dependencies

The experiments were conducted in a Windows environment using a Conda environment named `comp8240-baseline`.

Main Python dependencies:

- Python
- NumPy
- pandas
- scikit-learn
- PyArrow
- LIBLINEAR Python bindings

The original authors' `libmultilabel` code is also required.

## Reproducing the Experiments

1. Clone this repository.
2. Create a compatible Python environment and install the required dependencies.
3. Obtain the original authors' code and place it in `original_code/`.
4. Obtain the external datasets and place their Arrow files in the expected locations under `data/external/`.
5. Ensure the constructed Australian Government CSV is available at:

   `data/constructed/australian_gov_media/australian_gov_media_final.csv`

6. Run the evaluation scripts from the project root:

```cmd
python scripts/evaluate_ag_news.py
python scripts/evaluate_banking77.py
python scripts/evaluate_goemotions.py
python scripts/evaluate_imdb.py
python scripts/evaluate_trec.py
python scripts/evaluate_australian_gov.py
```

The scripts save evaluation results under `results/`.

The Australian Government evaluation also saves its stratified train/test split.

## Limitations

- Dataset sizes and classification tasks differ substantially.
- GoEmotions is multilabel, while the other new datasets use single-label classification.
- The constructed dataset is relatively small.
- Source-based labels may reflect departmental vocabulary rather than document topics.
- LLM-assisted annotation agreement is not equivalent to independent human inter-annotator agreement.
- The results do not establish that the linear approach is superior to other methods on these datasets.

## Research Ethics

The project uses publicly available text datasets and government media releases.

Research considerations include dataset licensing, attribution, possible bias in labels, transparent reporting, reproducibility and responsible interpretation of model performance.

The original authors' work and external datasets should be appropriately credited.

## Project Status

Original replication, six new-dataset evaluations, constructed dataset preparation and LLM-assisted annotation validation have been completed.

Final report preparation and repository reproducibility checks are in progress.
