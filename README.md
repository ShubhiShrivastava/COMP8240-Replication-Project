\# COMP8240 Replication Project



\## Project Overview



This repository contains work for the COMP8240 Applications of Data Science novel replication project at Macquarie University.



The project is based on the paper:



\*\*"Linear Classifier: An Often-Forgotten Baseline for Text Classification"\*\*  

Yu-Chen Lin, Si-An Chen, Jie-Jyun Liu, and Chih-Jen Lin  

ACL 2023



The project will investigate the replicability of the paper's experiments and examine whether its findings generalise to new text classification datasets.



\## Project Objectives



The project aims to:



1\. Reproduce selected results from the original paper using the authors' code and original data.

2\. Compare linear text classification methods with more computationally expensive approaches where feasible.

3\. Apply the methods to additional text classification datasets not evaluated in the original paper.

4\. Construct and evaluate a new text classification dataset.

5\. Analyse model performance, computational efficiency, and cases where different approaches succeed or fail.



\## Preliminary Replication



A preliminary feasibility experiment has been successfully completed using the \*\*UNFAIR-ToS\*\* dataset and the paper's one-vs-rest linear classification method.



| Metric | Paper Result | Preliminary Replication |

|---|---:|---:|

| Micro-F1 | 94.9 | 94.8702 |

| Macro-F1 | 75.1 | 75.0596 |



The preliminary experiment completed successfully on CPU in approximately \*\*3 seconds\*\*, providing initial evidence that the linear replication component is computationally feasible.



\## Repository Structure



\- `scripts/` – scripts created for data preparation and later experiments

\- `results/` – preliminary and future experimental results

\- `proposal/` – project proposal material

\- `data/` – local datasets (not tracked where appropriate)

\- `original\_code/` – local copy of the authors' repository (not tracked)



\## Original Resources



The original authors' code and datasets are kept separate from this repository. Instructions for obtaining and reproducing the required resources will be added as the project develops.



\## Status



\*\*Current stage:\*\* Project proposal and preliminary feasibility testing.

