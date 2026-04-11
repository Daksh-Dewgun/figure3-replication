# Assessment One: AI for Government and Policy

## Replication of Figure

This repository contains data and code to replicate **Figure 3** "Content the algorithm promotes" from:

> Gauthier, Hodler, Widmer & Zhuravskaya (2026). *The political effects of X's feed algorithm*. Nature. https://doi.org/10.1038/s41586-026-10098-2

---

## The repository is structured as follows:

```
figure3_repo/
├── run_figure3.sh                  ← ONE-CLICK pipeline (run this)
├── data/                           ← Required data file included
├── regression_outputs/             ← Auto-populated by Stata step
├── figs/                           ← Output: Figure 3 and supporting PDFs saved here
└── code/
    ├── stata/
    │   ├── run_stata_figure3.do    ← Master Stata script
    │   ├── newsfeed_content_shares.do
    │   ├── newsfeed_analysis_graph_input.do
    │   ├── newsfeed_analysis_graph_input_rep.do
    │   ├── newsfeed_analysis_graph_input_dem.do
    │   └── Prerequisites/
    │       └── regressions.do
    └── py/
        └── plot_newsfeeds.py       ← Generates the figure
```

**AI-Use Disclaimer:** Above structure is created using Claude Sonnet 4.6.


---

## Requirements

**Stata** (version 17+) with packages:
```stata
ssc install reghdfe
ssc install ppmlhdfe
```
I use Stata 19 - License provided to students by University of Birmingham.

In particular, please use StataSE as it supports large datasets like the one used for this study.

**Python 3** with packages (auto-installed by the run script):
```
pandas matplotlib numpy scipy
```

---

## Data

The data file is **included** in this repository in the `data/` folder:
   ```
   data/main_data_and_newsfeed_data.dta
   ```

---

## How to run

### To run in one go:

```bash
bash run_figure3.sh
```

This will:
1. Install Python dependencies
2. Run the Stata regressions and export p-values to `regression_outputs/`
3. Generate Figure 3 with Python and save to `figs/`
4. Automatically open the PDF

### Manual steps

If you prefer to run each step separately:

**Step 1 — Stata** (from `code/stata/`):
```bash
cd code/stata
stata -b do run_stata_figure3.do
```

**Step 2 — Python** (from `code/py/`):
```bash
cd code/py
python plot_newsfeeds.py
```

---

## Output

- `figs/newsfeed_barchart_with_pvalues.pdf` — **Figure 3** (full sample)

NB: running the `run_figure3.sh` file only opens the above figure automatically.

- `figs/newsfeed_barchart_with_pvalues_reps_indeps.pdf` — Republicans & Independents
- `figs/newsfeed_barchart_with_pvalues_dems.pdf` — Democrats
  

---

## Notes on Stata PATH (macOS)

If `bash run_figure3.sh` cannot find Stata, please add it to your PATH first:

```bash
export PATH=$PATH:/Applications/Stata/StataSE.app/Contents/MacOS
```

Or add this line to your `~/.zshrc` to make it permanent.
