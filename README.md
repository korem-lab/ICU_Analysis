## Project Overview ##

This repository contains code and results for the analysis of gut microbiome profiles and their ability to predict ICU outcomes, including infection and mortality. The analysis includes two cohorts of ICU patients profiled with 16S rRNA sequencing, combined with clinical metadata.

## Summary of Findings ##

Microbiome-based models did not consistently improve prediction of ICU-acquired infection or mortality compared to standard clinical scores (e.g., SOFA). External validation revealed limited generalizability, with predictive performance varying by outcome, cohort, and time horizon. These results suggest that, in their current form, gut microbiome features offer limited incremental value for clinical risk prediction in the ICU.

## Reproduction Steps ##

1. Access Raw Data
* Original cohort: /manitou/pmg/projects/korem_lab/Data/Freedberg_inulin_trial/
* Validation cohort: /manitou/pmg/projects/korem_lab/Data/Freedberg_inulin_trial/validation_data/

2. Preprocess 16S Sequencing Data (on manitou)

Follow the first two steps from the pipeline in /burg/pmg/users/se2481/scripts/16S_pipeline/README.md, with the following customizations:

(a) Human genome filtering

Remove human reads with the MMMBP pipeline:

```bash
pybatch run_mmmbp.py
```

Output in tmp/HGF2 contains filtered FASTQs and a df_path table of human-read counts.

(b) Primer trimming
```bash
conda activate shared
python /burg/pmg/users/se2481/scripts/16S_pipeline/trim_primers.py \
  --reads /manitou/pmg/users/mc5672/orig_data/hgf2_filtered/tmp/HGF2 \
  --fwd CCTACGGGNGGCWGCAG \
  --rev GACTACHVGGGTATCTAATCC \
  --batch 20 \
  --out /manitou/pmg/users/mc5672/orig_data/primer_trimmed \
  --exclude m014,m015 \
  --paired
```

Verify trimming:

```bash
cat *.log | grep 'with adapter'
```
(should be high, i.e. 98-99%)

3. (Optionally) Transfer Trimmed Files to Local Machine (& gunzip)

4. Process Data

(a) DADA2 + Taxonomy + SCRuB

Run `Data_Processing.ipynb`

This notebook:
	•	Performs denoising with DADA2
	•	Assigns taxonomy
	•	Removes contaminants using SCRuB
	•	Computes α- and β-diversity

(b) Enrich with Metadata

Run `Data_Enriching.ipynb`

This joins ASV tables with clinical reference data, performs CLR-transformation, and adds derived features (e.g., SOFA scores, infection timing).


5. Run Predictive Models:

Choose one of the models in `prediction_models/`, e.g:
```bash
pybatch Death_Next_7_SOFA.py
```
Each notebook is configured to predict a specific outcome (e.g., infection, mortality) using combinations of microbiome and clinical features.

6. Evaluate and Plot Results

To evaluate model AUROCs and plot ROC curves, run `Evaluate_Model.ipynb`

(Helpful utility) To generate plots for all models in prediction_models/, run: `Generate_Plots.ipynb`


