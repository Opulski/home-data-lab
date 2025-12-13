import argparse
from pathlib import Path

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "--ingested-at",
    help="YYYY-MM-DDTHH-MM-SSZ (optional for local debug)",
    required=True,
)
args = parser.parse_args()

ingested_at_str = args.ingested_at

# Load raw data
RAW_PATH = "./data/01_raw/weather/meteostat_2025.csv"
df = pd.read_csv(RAW_PATH)

# time,temp,dwpt,rhum,prcp,snow,wdir,wspd,wpgt,pres,tsun,coco
# 2025-01-01 00:00:00,2.0,-0.9,81.0,0.0,0.0,226.0,22.2,40.8,1018.9,0.0,4.0

# Parse time
df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
df["time"] = df["time"].dt.tz_localize("UTC")

# Explicitly convert numeric columns
numeric_cols = [
    "temp",
    "dwpt",
    "rhum",
    "prcp",
    "snow",
    "wdir",
    "wspd",
    "wpgt",
    "pres",
    "tsun",
    "coco",
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# set index
df = df.set_index("time").sort_index()

# Add ingestion timestamp
ingested_at = pd.to_datetime(ingested_at_str, format="%Y-%m-%dT%H-%M-%SZ", utc=True)
df["ingested_at"] = ingested_at

ingested_at_st = ingested_at_str

OUTPUT_PATH = Path(f"./data/02_stg/weather/meteostat_1h/ingested_at={ingested_at_st}")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_PATH / "Meteostat_1h.csv"

df.to_csv(OUTPUT_PATH, index=True)
