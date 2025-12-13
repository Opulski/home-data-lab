SHELL := /bin/bash

# filesystem-safe UTC timestamp
INGESTED_AT := $(shell date -u +"%Y-%m-%dT%H-%M-%SZ")
AS_OF ?= $(INGESTED_AT)

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make ingest                 -> download raw snapshots (INGESTED_AT=$(INGESTED_AT))"
	@echo "  make stg                     -> build stg (same INGESTED_AT)"
	@echo "  make marts AS_OF=...          -> join latest<=AS_OF into marts/as_of=..."
	@echo "  make run                      -> ingest + stg + marts (AS_OF defaults to INGESTED_AT)"

.PHONY: ingest
ingest:
	uv run python pipelines/ingest_entsoe.py --ingested-at $(INGESTED_AT)

.PHONY: stg
stg:
	uv run python pipelines/stg_prices_1h.py --ingested-at $(INGESTED_AT)
	uv run python pipelines/stg_load_1h.py --ingested-at $(INGESTED_AT)
	uv run python pipelines/stg_generation_1h.py --ingested-at $(INGESTED_AT)
	uv run python pipelines/stg_weather.py --ingested-at $(INGESTED_AT)

.PHONY: marts
marts:
	uv run python pipelines/marts_join_asof.py --as-of $(AS_OF)

.PHONY: run
run: ingest stg marts
