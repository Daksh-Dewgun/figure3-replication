# Figure 3 Replication — "The political effects of X's feed algorithm"

Replicates **Figure 3** ("Content the algorithm promotes") from:

> Gauthier, Hodler, Widmer & Zhuravskaya (2026). *The political effects of X's feed algorithm*. Nature. https://doi.org/10.1038/s41586-026-10098-2

---

## Repository structure

```
figure3_repo/
├── run_figure3.sh                  ← ONE-CLICK pipeline (run this)
├── data/                           ← Place data file here (see below)
├── regression_outputs/             ← Auto-populated by Stata step
├── figs/                           ← Output: Figure 3 PDF saved here
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

---

## Requirements

**Stata** (version 17+) with packages:
```stata
ssc install reghdfe
ssc install ppmlhdfe
```

**Python 3** with packages (auto-installed by the run script):
```
pandas matplotlib numpy scipy
```

---

## Data

The data file is **not included** in this repository due to size.

1. Download `main_data_and_newsfeed_data.dta` from the replication archive:
   https://doi.org/10.6084/m9.figshare.28033772

2. Place it in the `data/` folder:
   ```
   data/main_data_and_newsfeed_data.dta
   ```

---

## How to run

### One click (recommended)

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
- `figs/newsfeed_barchart_with_pvalues_reps_indeps.pdf` — Republicans & Independents
- `figs/newsfeed_barchart_with_pvalues_dems.pdf` — Democrats

---

## Notes on Stata PATH (macOS)

If `bash run_figure3.sh` cannot find Stata, add it to your PATH first:

```bash
export PATH=$PATH:/Applications/Stata/StataMP.app/Contents/MacOS
```

Or add this line to your `~/.zshrc` to make it permanent.
