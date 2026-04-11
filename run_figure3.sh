#!/bin/bash
# =============================================================================
# run_figure3.sh
# Replicates Figure 3 ("Content the algorithm promotes") from:
#   Gauthier, Hodler, Widmer & Zhuravskaya (2026), Nature
#
# Usage:  bash run_figure3.sh
# Requires: Stata (with reghdfe, ppmlhdfe), Python 3 (with dependencies)
# =============================================================================

set -e  # Exit immediately on any error

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo " Figure 3 Replication Pipeline"
echo "============================================"

# --- Step 1: Check data exists ---
if [ ! -f "$REPO_DIR/data/main_data_and_newsfeed_data.dta" ]; then
    echo ""
    echo "ERROR: Data file not found."
    echo "Please place 'main_data_and_newsfeed_data.dta' in the data/ folder."
    echo "Data is available at: https://doi.org/10.6084/m9.figshare.28033772"
    exit 1
fi

# --- Step 2: Install Python dependencies ---
echo ""
echo "[1/3] Installing Python dependencies..."
pip install -q pandas matplotlib numpy scipy

# --- Step 3: Run Stata pipeline ---
echo ""
echo "[2/3] Running Stata regressions..."

# Detect stata executable
if command -v stata-mp &> /dev/null; then
    STATA_CMD="stata-mp"
elif command -v stata-se &> /dev/null; then
    STATA_CMD="stata-se"
elif command -v stata &> /dev/null; then
    STATA_CMD="stata"
else
    echo ""
    echo "ERROR: Stata not found in PATH."
    echo "Please ensure Stata is installed and accessible from the terminal."
    echo "On Mac, you may need to add it to PATH, e.g.:"
    echo "  export PATH=\$PATH:/Applications/Stata/StataMP.app/Contents/MacOS"
    exit 1
fi

cd "$REPO_DIR/code/stata"
$STATA_CMD -b do run_stata_figure3.do
cd "$REPO_DIR"

# Check Stata succeeded
if [ ! -f "$REPO_DIR/regression_outputs/newsfeed_regression_p_values.csv" ]; then
    echo ""
    echo "ERROR: Stata step failed. Check code/stata/run_stata_figure3.log for details."
    exit 1
fi

# --- Step 4: Generate plot ---
echo ""
echo "[3/3] Generating Figure 3..."
cd "$REPO_DIR/code/py"
python plot_newsfeeds.py
cd "$REPO_DIR"

# --- Step 5: Open plot ---
echo ""
echo "============================================"
echo " Done! Opening Figure 3..."
echo "============================================"
open "$REPO_DIR/figs/newsfeed_barchart_with_pvalues.pdf"
