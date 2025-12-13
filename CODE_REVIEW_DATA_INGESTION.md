# Code Review: data-ingestion Branch

## Executive Summary

The `data-ingestion` branch introduces a data pipeline for processing energy market and weather data, along with a baseline machine learning model for price prediction. The implementation includes 5 commits adding approximately 915,549 lines (primarily data files) with Python-based ETL pipelines and ML code.

**Overall Assessment: Needs Significant Improvements** ⚠️

While the branch demonstrates a functional proof-of-concept for data ingestion and modeling, it has several critical issues that should be addressed before merging:

---

## 🔴 Critical Issues

### 1. **Large Data Files Committed to Git (CRITICAL)**
**Severity: HIGH** - This is the most serious issue

- **Problem**: Raw and processed CSV files totaling ~900K+ lines committed directly to the repository
  - `data/01_raw/entsoe/Generation.csv`: 735,841 lines
  - `data/01_raw/entsoe/DAPrices.csv`: 66,817 lines  
  - `data/01_raw/entsoe/Load.csv`: 35,041 lines
  - Multiple staged and marts CSV files
  
- **Impact**: 
  - Repository size bloat (7.73 MiB in one commit)
  - Slow git operations
  - Difficult to maintain and version
  - Not following data engineering best practices

- **Recommendation**: 
  - Remove all data files from git
  - Add `data/` to `.gitignore` (currently commented: `#data/`)
  - Use external storage (S3, GCS, or local volumes outside repo)
  - Add data download/generation scripts instead
  - Only commit small sample/fixture data if needed for testing

### 2. **Missing Ingestion Script**
**Severity: HIGH**

- **Problem**: `Makefile` references `pipelines/ingest_entsoe.py` which doesn't exist
  ```makefile
  ingest:
      uv run python pipelines/ingest_entsoe.py --ingested-at $(INGESTED_AT)
  ```

- **Impact**: The pipeline cannot be executed end-to-end as documented

- **Recommendation**: 
  - Create the missing `ingest_entsoe.py` script
  - Or update Makefile to reference existing scripts
  - Document the actual ingestion process

### 3. **No Command-Line Interface for STG Scripts**
**Severity: MEDIUM**

- **Problem**: Staging scripts (`stg_*.py`) don't accept the `--ingested-at` parameter that Makefile passes to them
  ```python
  # Current: Hard-coded timestamp
  ingested_at = pd.Timestamp.now(tz="UTC")
  ```

- **Impact**: 
  - Cannot replay historical data with specific timestamps
  - Makes testing and debugging difficult
  - Violates functional programming principles (not idempotent)

- **Recommendation**: Add argparse to all staging scripts:
  ```python
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--ingested-at", required=True)
  args = parser.parse_args()
  ingested_at = pd.to_datetime(args.ingested_at, format="%Y-%m-%dT%H-%M-%SZ", utc=True)
  ```

---

## 🟡 Major Issues

### 4. **Inconsistent Error Handling**
**Severity: MEDIUM**

- **Problem**: Inconsistent use of `errors="coerce"` in parsing
  - Some places use it: `pd.to_datetime(..., errors="coerce")`
  - Others don't, which could cause pipeline failures on bad data

- **Recommendation**: Standardize error handling strategy and add logging for coerced values

### 5. **Code Duplication**
**Severity: MEDIUM**

- **Problem**: Heavy duplication across staging scripts:
  - MTU parsing logic repeated 3 times (prices, load, generation)
  - Timezone localization logic duplicated
  - Ingestion timestamp generation duplicated
  - File output logic duplicated

- **Recommendation**: Extract common functions into a shared utility module:
  ```python
  # pipelines/utils/common.py
  def parse_mtu_column(df, mtu_col_name, datetime_format):
      """Parse MTU column into start_time and end_time."""
      ...
  
  def localize_to_berlin(dt_series):
      """Localize timezone-naive datetime to Europe/Berlin."""
      ...
  
  def save_with_ingestion_timestamp(df, base_path, filename_prefix, ingested_at):
      """Save dataframe with ingestion timestamp partitioning."""
      ...
  ```

### 6. **Hardcoded Paths**
**Severity: MEDIUM**

- **Problem**: All paths are hardcoded strings starting with `./data/`
  ```python
  RAW_PATH = "./data/01_raw/entsoe/DAPrices.csv"
  ```

- **Impact**: 
  - Not configurable for different environments
  - Difficult to test
  - Breaks if run from different working directory

- **Recommendation**: 
  - Use environment variables or config files
  - Pass paths as CLI arguments
  - Use `pathlib.Path` consistently and define root paths centrally

### 7. **No Data Validation**
**Severity: MEDIUM**

- **Problem**: No validation of:
  - Expected columns exist
  - Data types are correct
  - Value ranges are reasonable
  - No nulls in critical fields
  - Timestamps are sequential

- **Recommendation**: 
  - Add data validation using Pandera or Great Expectations
  - Implement checks before and after transformations
  - Fail fast on schema mismatches

### 8. **Problematic mart join logic in `marts_join_asof.py`**
**Severity: MEDIUM**

- **Problems**:
  1. Inconsistent ingestion time handling:
     - Price data: Uses `max(candidates)` to pick latest
     - Load data: Concatenates ALL files before cutoff
     - Generation data: Concatenates ALL files  
     - Weather data: Uses `max(candidates)` to pick latest
  
  2. This creates duplicates for load/generation data and could cause:
     - Data quality issues
     - Incorrect aggregations
     - Confusing results

  3. Debugging print statements left in production code:
     ```python
     print(f"Found {len(files)} files.")
     print(df_weather.columns)
     print(df_weather.head())
     ```

- **Recommendation**:
  - Standardize to use latest ingestion file for all sources OR
  - If concatenation is intentional, deduplicate on `(start_time, source)` key
  - Remove or convert print statements to proper logging
  - Add comments explaining the logic

---

## 🟢 Minor Issues / Improvements

### 9. **Missing Documentation**
- No docstrings on any functions
- No README in `pipelines/` explaining the data flow
- No data dictionary explaining what each field means
- Comments are sparse and sometimes in German ("ingested_at aus Pfad extrahieren (kein Magic)")

### 10. **Code Style Inconsistencies**
- Inconsistent spacing around operators
- Some scripts use blank lines liberally, others don't
- No linting configuration (ruff, black, flake8)
- Would benefit from pre-commit hooks

### 11. **No Testing**
- No unit tests for any pipeline code
- No integration tests
- No data quality tests
- Makes refactoring risky

### 12. **Timezone Handling Could Be Clearer**
- Uses "Europe/Berlin" for CET/CEST which is correct but could be confusing
- Mixed use of UTC for ingestion timestamps and Berlin time for data
- Could benefit from explicit documentation about timezone strategy

### 13. **Resource Management**
- Large dataframes loaded entirely into memory
- No streaming or chunking for big files
- Could cause memory issues with larger datasets

### 14. **Model Code Issues** (`baseline_regression.py`)

**Good practices observed:**
- Time-based train/test split (appropriate for time series)
- Proper feature engineering (lag features, cyclical encoding)
- Residual modeling approach

**Issues:**
- Hardcoded default as_of timestamp: `"2025-12-13T16-28-39Z"`
- Feature leakage risk: Model uses actual load which may not be available at prediction time
- Hard-coded feature lists make it fragile to schema changes
- No model serialization/persistence
- Visualization calls `plt.show()` which won't work in headless environments
- No evaluation metrics saved to disk
- Assert statements for validation (will be removed in optimized Python)

### 15. **Git Hygiene Issues**

**Commit messages:**
- `"basic data ingestion still broken af"` - Unprofessional language
- `"fixed missing time in weather stg and tried weather features for residual model"` - Too vague, combines multiple concerns

**Branch management:**
- Committed generated data files should have been in separate commits from code

---

## 🟢 What Was Done Well

### Positive Aspects ✅

1. **Good Directory Structure**: Using medallion architecture pattern (raw → stg → marts)
2. **Partitioning Strategy**: Using ingestion timestamps for versioning is a good practice
3. **Timezone Awareness**: Properly handling CET/CEST with DST transitions
4. **Feature Engineering**: Good ML features (cyclical encoding, lag features, renewable share)
5. **Makefile**: Good use of Make for orchestration with clear targets
6. **pyproject.toml + uv.lock**: Modern Python packaging with locked dependencies
7. **Explicit Resampling**: Clear resampling logic with labels and closed parameters

---

## 📋 Recommended Action Plan

### Immediate (Before Merge):
1. ✅ Remove all data files from git and update `.gitignore`
2. ✅ Create or fix `pipelines/ingest_entsoe.py`
3. ✅ Add CLI argument parsing to all staging scripts
4. ✅ Standardize the marts join logic
5. ✅ Add basic README documentation

### Short-term (Next Sprint):
1. Extract common code into utilities module
2. Add data validation with Pandera schemas
3. Set up logging framework
4. Add unit tests for transformation logic
5. Configure linting and formatting

### Long-term:
1. Move to proper orchestration (Airflow/Dagster)
2. Add data quality monitoring
3. Implement incremental loading
4. Set up CI/CD pipelines
5. Containerize the application

---

## Summary Statistics

- **Commits**: 5
- **Files Changed**: 25
- **Lines Added**: ~915,549 (mostly data)
- **Code Files**: ~10 Python files
- **Critical Issues**: 3
- **Major Issues**: 5
- **Minor Issues**: 7

---

## Conclusion

This branch represents a solid proof-of-concept for a data ingestion and modeling pipeline. However, it requires significant cleanup before being production-ready. The most critical issue is the inclusion of large data files in git, which should be addressed immediately. The code quality is reasonable for a prototype but needs refactoring, testing, and documentation improvements.

**Recommendation**: Do not merge as-is. Request changes to address critical and major issues first.

---

*Reviewer: GitHub Copilot*
