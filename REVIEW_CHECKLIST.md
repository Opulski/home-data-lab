# Review Checklist for data-ingestion Branch

Quick reference checklist for addressing review findings.

## 🔴 Critical (Must Fix Before Merge)

- [ ] **Remove data files from git**
  - [ ] Run `git rm -r --cached data/` (after backing up)
  - [ ] Add `data/` to `.gitignore`
  - [ ] Commit and push changes
  - [ ] Document how to obtain/generate data files

- [ ] **Fix missing ingestion script**
  - [ ] Create `pipelines/ingest_entsoe.py` OR
  - [ ] Update Makefile to remove ingest target OR
  - [ ] Document the actual ingestion process

- [ ] **Add CLI arguments to staging scripts**
  - [ ] `pipelines/stg/stg_prices_1h.py` - Add `--ingested-at` argument
  - [ ] `pipelines/stg/stg_load_1h.py` - Add `--ingested-at` argument
  - [ ] `pipelines/stg/stg_generation_1h.py` - Add `--ingested-at` argument
  - [ ] `pipelines/stg/stg_weather.py` - Add `--ingested-at` argument
  - [ ] Test that Makefile commands work end-to-end

## 🟡 High Priority (Should Fix Soon)

- [ ] **Standardize mart join logic**
  - [ ] Choose strategy: latest file only OR concatenate+dedupe
  - [ ] Apply consistently to all data sources (price, load, gen, weather)
  - [ ] Add comments explaining the logic

- [ ] **Remove debug statements**
  - [ ] Replace `print()` with proper logging in `marts_join_asof.py`
  - [ ] Set up logging configuration

- [ ] **Add basic documentation**
  - [ ] Create `pipelines/README.md` explaining pipeline flow
  - [ ] Add docstrings to key functions
  - [ ] Document data sources and schemas

## 🟢 Medium Priority (Recommended)

- [ ] **Extract common utilities**
  - [ ] Create `pipelines/utils/common.py`
  - [ ] Extract MTU parsing logic
  - [ ] Extract timezone handling logic
  - [ ] Extract file saving logic

- [ ] **Add data validation**
  - [ ] Install Pandera or Great Expectations
  - [ ] Define schemas for raw data
  - [ ] Add validation checks in staging scripts

- [ ] **Improve error handling**
  - [ ] Standardize use of `errors="coerce"`
  - [ ] Add try/except blocks for file operations
  - [ ] Log when data is coerced or dropped

## ⚪ Low Priority (Nice to Have)

- [ ] **Add testing**
  - [ ] Create `tests/` directory
  - [ ] Add unit tests for transformation logic
  - [ ] Add integration test for full pipeline

- [ ] **Set up linting**
  - [ ] Install ruff/black/flake8
  - [ ] Add `.pre-commit-config.yaml`
  - [ ] Run formatter on all Python files

- [ ] **Add type hints**
  - [ ] Add type hints to function signatures
  - [ ] Run mypy for type checking

## 📋 Verification Steps

After making fixes, verify:

- [ ] `make help` displays correct targets
- [ ] `make ingest` (or equivalent) downloads/prepares data
- [ ] `make stg` processes raw data successfully
- [ ] `make marts` creates joined dataset
- [ ] `python pipelines/models/baseline_regression.py` runs
- [ ] Git repository size is reasonable (<50MB)
- [ ] All scripts accept required CLI arguments
- [ ] No print statements in production code
- [ ] Basic documentation exists

## 📚 Reference Documents

For detailed information, see:

- **CODE_REVIEW_DATA_INGESTION.md** - Full technical review (15 issues)
- **FIXES_REQUIRED.md** - Copy-paste code fixes
- **REVIEW_SUMMARY.md** - Executive summary

## 🎯 Minimum Viable Merge

At minimum, address these 3 items before merging:

1. ✅ Remove data files from git (or accept that repo will be large)
2. ✅ Fix/document the missing ingest script  
3. ✅ Make CLI arguments work OR update Makefile to match reality

Everything else can be addressed in follow-up PRs.

---

*Use this checklist to track your progress fixing the review findings.*
