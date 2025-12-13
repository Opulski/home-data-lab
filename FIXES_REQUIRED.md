# Required Fixes for data-ingestion Branch

## 🔴 CRITICAL - Must Fix Before Merge

### 1. Fix Data Leakage in ML Model

**⚠️ CRITICAL**: The model uses features that won't be available at prediction time, making results invalid.

**File**: `pipelines/models/baseline_regression.py`

**Problem**: Lines 76-79 use actual load data that won't be known when predicting day-ahead prices:
```python
df["load_forecast_mw"] = df["Day-ahead Total Load Forecast (MW)"]
df["load_actual_mw"] = df["Actual Total Load (MW)"]  # ❌ LEAKAGE
df["load_error_mw"] = df["load_actual_mw"] - df["load_forecast_mw"]  # ❌ LEAKAGE
```

**Fix**:
```python
# Remove these lines from FEATURES list (lines 96-112):
# "load_error_mw",  # ❌ Remove - contains actual load
# "load_ramp_1h",   # ❌ Remove - uses actual load

# Keep only:
FEATURES = [
    "load_forecast_mw",  # ✅ Available day-ahead
    "gen_renewable_mw",   # If available at bidding time
    "gen_fossil_mw",      # If available at bidding time
    "gen_res_share",      # If available at bidding time
    "hour",
    "hour_sin",
    "hour_cos",
    "dow",
    "dow_sin",
    "dow_cos",
    "wind_ramp_1h",      # Only if using forecasted values
    "solar_ramp_1h",     # Only if using forecasted values
    "res_ramp_1h",       # Only if using forecasted values
]
```

**Important considerations**:
- Day-ahead prices are for delivery 24h in the future
- Bidding typically closes around 12:00 CET for next-day delivery
- Only use features that would be available at bidding cutoff time
- Consider proper time alignment (lag the target or shift features forward)
- Retrain model after fixing features to get realistic performance metrics

### 2. Remove Data Files from Git

**⚠️ WARNING**: This operation will remove data files from git tracking. Make sure you have backups of any important data before proceeding!

```bash
# First, ensure you're in the correct directory and check what will be removed
cd /path/to/home-data-lab
git status

# Remove data directory from tracking (keeps local files)
git rm -r --cached data/
echo "data/" >> .gitignore

# Commit the removal
git commit -m "Remove data files from git tracking"
```

**Why**: Repository contains ~900K lines of CSV data, bloating repo size and violating best practices.

### 3. Create Missing `ingest_entsoe.py` Script

The Makefile references this script but it doesn't exist:
```makefile
ingest:
    uv run python pipelines/ingest_entsoe.py --ingested-at $(INGESTED_AT)
```

**Options:**
- Create the script to download/generate data
- Update Makefile to match existing workflow
- Add documentation about how to obtain data

### 4. Add CLI Arguments to Staging Scripts

**Files to update:**
- `pipelines/stg/stg_prices_1h.py`
- `pipelines/stg/stg_load_1h.py`
- `pipelines/stg/stg_generation_1h.py`
- `pipelines/stg/stg_weather.py`

**Change needed:**
```python
# Add at top of each file
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ingested-at", required=True, 
                   help="Ingestion timestamp in format YYYY-MM-DDTHH-MM-SSZ")
args = parser.parse_args()

# Replace this line:
# ingested_at = pd.Timestamp.now(tz="UTC")

# With this:
ingested_at = pd.to_datetime(args.ingested_at, format="%Y-%m-%dT%H-%M-%SZ", utc=True)
```

---

## 🟡 HIGH PRIORITY - Should Fix Soon

### 5. Fix Inconsistent Mart Join Logic

**File**: `pipelines/marts/marts_join_asof.py`

**Problems:**
- Price/Weather: Takes latest file only
- Load/Generation: Concatenates ALL files (creates duplicates)

**Fix Option A** - Use latest for all:
```python
# Apply same logic to load and generation as used for price
for section in [df_price, df_load, df_gen, df_weather]:
    # Use max(candidates) pattern consistently
    chosen_ingested_at, chosen_fp = max(candidates, key=lambda x: x[0])
    df = pd.read_csv(chosen_fp)
    df["ingested_at"] = pd.Timestamp(chosen_ingested_at)
```

**Fix Option B** - Deduplicate concatenated data:
```python
# After concatenation, deduplicate
df_load = pd.concat(dfs, ignore_index=True)
df_load = df_load.sort_values(['start_time', 'ingested_at'])
df_load = df_load.drop_duplicates(subset=['start_time'], keep='last')
```

### 6. Remove Debug Print Statements

**File**: `pipelines/marts/marts_join_asof.py`

Remove or replace with logging:
```python
# Remove these:
print(f"Found {len(files)} files.")
print(df_weather.columns)
print(df_weather.head())

# Replace with proper logging:
import logging
logger = logging.getLogger(__name__)
logger.info(f"Found {len(files)} files for {source}")
logger.debug(f"Weather columns: {df_weather.columns.tolist()}")
```

### 7. Add Data Directory to .gitignore

**File**: `.gitignore`

Currently line 125 has:
```
.pixi
```

Add after line 125:
```
# Data files
data/
!data/.gitkeep
```

Then create `.gitkeep` files to preserve directory structure:
```bash
mkdir -p data/{01_raw,02_stg,03_marts}
touch data/01_raw/.gitkeep
touch data/02_stg/.gitkeep
touch data/03_marts/.gitkeep
```

---

## 🟢 MEDIUM PRIORITY - Good to Have

### 8. Add Basic Documentation

Create `pipelines/README.md`:
```markdown
# Data Pipelines

## Pipeline Flow
1. **Raw** (01_raw/): Raw data from ENTSOE and weather APIs
2. **Staging** (02_stg/): Cleaned, resampled to 1h, timezone-aware
3. **Marts** (03_marts/): Joined datasets ready for analysis

## Running Pipelines
```bash
# Full pipeline
make run

# Individual stages
make ingest
make stg
make marts AS_OF=2025-12-13T10-00-00Z
```

## Data Sources
- ENTSOE: Day-ahead prices, generation, load
- Meteostat: Historical weather data
```

### 9. Add Type Hints

Example for `stg_prices_1h.py`:
```python
from pathlib import Path
import pandas as pd
from datetime import datetime

def parse_mtu(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Parse MTU (CET/CEST) column into start_time and end_time."""
    mtu = df[column].astype(str).str.split(" - ", n=1, expand=True)
    df["start_time_str"] = mtu[0].str.strip()
    df["end_time_str"] = mtu[1].str.strip()
    return df
```

### 10. Add Basic Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage:
logger.info(f"Processing {len(df)} rows")
logger.warning(f"Found {null_count} null values in critical column")
```

---

## ⚪ LOW PRIORITY - Nice to Have

### 11. Extract Common Utilities

Create `pipelines/utils/common.py`:
```python
from pathlib import Path
import pandas as pd

def parse_mtu_column(
    df: pd.DataFrame, 
    mtu_col: str, 
    datetime_format: str
) -> pd.DataFrame:
    """Parse MTU column into timezone-aware start_time and end_time."""
    mtu = df[mtu_col].astype(str).str.split(" - ", n=1, expand=True)
    df["start_time"] = pd.to_datetime(
        mtu[0].str.strip(), 
        format=datetime_format, 
        errors="coerce"
    )
    df["end_time"] = pd.to_datetime(
        mtu[1].str.strip(), 
        format=datetime_format, 
        errors="coerce"
    )
    df["start_time"] = df["start_time"].dt.tz_localize(
        "Europe/Berlin", ambiguous="infer", nonexistent="shift_forward"
    )
    df["end_time"] = df["end_time"].dt.tz_localize(
        "Europe/Berlin", ambiguous="infer", nonexistent="shift_forward"
    )
    return df.drop(columns=[mtu_col])

def save_partitioned(
    df: pd.DataFrame,
    base_path: str,
    filename: str,
    ingested_at: pd.Timestamp
) -> Path:
    """Save dataframe with ingestion timestamp partitioning."""
    partition = ingested_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    output_path = Path(base_path) / f"ingested_at={partition}"
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / filename
    df.to_csv(output_file, index=False)
    return output_file
```

### 12. Add Pre-commit Configuration

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
```

### 13. Add Basic Tests

Create `tests/test_staging.py`:
```python
import pandas as pd
import pytest
from pipelines.stg import stg_prices_1h  # after refactoring

def test_mtu_parsing():
    """Test MTU column parsing."""
    sample_data = pd.DataFrame({
        'MTU (CET/CEST)': ['01/01/2025 00:00:00 - 01/01/2025 00:15:00'],
        'Day-ahead Price (EUR/MWh)': [2.16]
    })
    # Test parsing logic
    ...

def test_timezone_localization():
    """Test timezone handling."""
    ...
```

---

## Checklist

Copy this to track progress:

```markdown
### Critical (Before Merge)
- [ ] Fix data leakage in ML model (remove actual load features)
- [ ] Remove data files from git
- [ ] Add data/ to .gitignore  
- [ ] Create ingest_entsoe.py or update Makefile
- [ ] Add --ingested-at argument to all stg scripts

### High Priority
- [ ] Fix mart join logic inconsistency
- [ ] Remove debug print statements
- [ ] Add basic pipelines/README.md

### Medium Priority
- [ ] Extract common utilities
- [ ] Add basic logging
- [ ] Add type hints

### Low Priority  
- [ ] Add pre-commit hooks
- [ ] Add unit tests
- [ ] Set up linting/formatting
```

---

*Document created for data-ingestion branch review*
