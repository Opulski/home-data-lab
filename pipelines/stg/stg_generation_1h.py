from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import argparse

# AS_OF = pd.Timestamp.now(tz="UTC")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--ingested-at",
    help="YYYY-MM-DDTHH-MM-SSZ (optional for local debug)", required=True
)
args = parser.parse_args()

if args.ingested_at:
    AS_OF = pd.to_datetime(
        args.as_of,
        format="%Y-%m-%dT%H-%M-%SZ",
        utc=True
    )

# Load raw data
RAW_PATH = "./data/01_raw/entsoe/Generation.csv"
df = pd.read_csv(RAW_PATH)


# Split MTU into start/end (keeps it simple and explicit)
mtu = df["MTU (CET/CEST)"].astype(str).str.split(" - ", n=1, expand=True)
df["start_time_str"] = mtu[0].str.strip()
df["end_time_str"] = mtu[1].str.strip()

# Parse as naive timestamps (no timezone yet)
df["start_time"] = pd.to_datetime(
    df["start_time_str"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
df["end_time"] = pd.to_datetime(
    df["end_time_str"],   format="%d/%m/%Y %H:%M:%S", errors="coerce")

# Localize properly for CET/CEST -> use Europe/Berlin (handles DST rules)
# ambiguous: "infer" tries to infer DST fall-back duplicates if sequence is monotonic-ish
# nonexistent: shift forward for the missing hour at DST spring-forward
df["start_time"] = df["start_time"].dt.tz_localize(
    "Europe/Berlin", ambiguous="infer", nonexistent="shift_forward")
df["end_time"] = df["end_time"].dt.tz_localize(
    "Europe/Berlin", ambiguous="infer", nonexistent="shift_forward")

df["Generation (MW)"] = pd.to_numeric(df["Generation (MW)"], errors="coerce")


# Explode Production Type
df = (
    df
    .pivot_table(
        index=["start_time", "Area"],
        columns="Production Type",
        values="Generation (MW)",
        aggfunc="mean"
    )
    .reset_index()
)

# set index
df = df.set_index("start_time").sort_index()

# Resample to hourly frequency, taking the mean of prices within each hour
price_cols = ['Biomass', 'Fossil Brown coal/Lignite',
              'Fossil Coal-derived gas', 'Fossil Gas', 'Fossil Hard coal',
              'Fossil Oil', 'Geothermal', 'Hydro Pumped Storage',
              'Hydro Run-of-river and pondage', 'Hydro Water Reservoir', 'Other',
              'Other renewable', 'Solar', 'Waste', 'Wind Offshore', 'Wind Onshore']

df_1h = (
    df[price_cols]
    .resample("h", label="left", closed="left")
    .mean()
)

df_1h = df_1h.reset_index()

# Add ingestion timestamp
ingested_at = pd.Timestamp.now(tz="UTC")
df_1h["ingested_at"] = ingested_at

ingested_at_st = (
    ingested_at.strftime("%Y-%m-%dT%H-%M-%SZ")
)

OUTPUT_PATH = Path(
    f"./data/02_stg/entsoe/generation_1h/ingested_at={ingested_at_st}")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_PATH / "Generation_1h.csv"

df_1h.to_csv(OUTPUT_PATH, index=False)
