# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python 3.5.6, conda environment named `hogs`. Activate before doing anything:
```bash
eval "$(/home/jvandevelde/miniconda3/bin/conda shell.bash hook)"
conda activate hogs
```

Launch the application:
```bash
jupyter notebook
```
Then open `Lean_Hogs_v5.ipynb` and run the single cell. There are no tests, no build step, and no linter configured.

Recreate the environment from scratch:
```bash
conda env remove -n hogs
conda env create -f conda/environment.yml
```
Note: PyQt5 must come from the conda channel (`pyqt=5.9.2`), not pip — pip cannot build it from source on Python 3.5.

## Data

The application reads from `hog_settlements.xlsx` in the project root. Expected format:
- Column A: dates (becomes DatetimeIndex)
- Remaining columns: settlement prices named `LN{MONTH}{YEAR}` (e.g. `LNK2024`)
- Sparse data (NaN cells) is fine — the app forward-fills gaps up to 3 days

`output/finalData.xlsx` is written on every `calculate()` call — one sheet per far contract.

## Architecture

The data flow is strictly one-directional:

```
hog_settlements.xlsx
      ↓
dataManager.load_data()        # returns raw DataFrame
      ↓
controller.calculate(near, years)  # returns dfList
      ↓
lhdata.plot_*() / butterfly.create_chart()  # renders matplotlib windows
```

**`dataManager.py`** — thin loader. Sets module-level `DATA_FILE` global (mutated by UI before each call).

**`controller.py`** — the core spread engine. `calculate(near, years)` iterates every far contract and every year, computes `near - far` settlement differences, then date-shifts each year's series so they all align on a shared x-axis (so historical years overlay each other). Critical logic: late-year near contracts (N/Q/V/Z) paired with early-year far contracts (G/J/K/M) must pull `year+1` far data — this is the year-rollover correction at line 89.

**`butterfly.py`** — butterfly spread engine (`x - 2y + z`). `create_contract_to_expiry_map()` handles the same year-rollover problem for 3-leg spreads. `get_contract_data()` forward-fills up to 3 days to smooth weekend/holiday gaps.

**`lhdata.py`** — all matplotlib/seaborn chart rendering. No data logic.

**`utility.py`** — static reference data only: contract month codes (`G`=Feb, `J`=Apr, `K`=May, `M`=Jun, `N`=Jul, `Q`=Aug, `V`=Oct, `Z`=Dec), default far contract sets per near month (`regularMonthSets`), and predefined butterfly combos (`commonButterflies`).

**`uicontrollerv2.py`** — the active UI (imported in the notebook as `ui`). `uicontroller.py` is the legacy version and is no longer used. The v2 UI injects a `<style>` block on every cell run (styles accumulate in the DOM across re-runs — this is a known Jupyter limitation). Button backgrounds are set via both CSS classes and `style.button_color` on each widget instance, because CSS alone is unreliable in this ipywidgets version.

## Key domain facts

- CME Lean Hog contract codes: `LN` prefix + month letter + 4-digit year (e.g. `LNK2025`)
- Contract expiry: 10th business day of the expiry month
- Chart x-axis: all years are date-shifted to overlap, keyed from `get_contract_start_date()` (expiry minus 1 year)
- `dfList` returned by `calculate()` is a list of `[farContractName, dfShifted, dfOriginalDates]` triples
- `ContractException` (in `exceptions.py`) is the only custom exception — raised for invalid butterfly leg selections
