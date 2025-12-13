from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# Load raw data
RAW_PATH = "./data/01_raw/entsoe/DAPrices.csv"
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

# Cleanup
df = df.drop(columns=["MTU (CET/CEST)", "start_time_str", "end_time_str"])

# set index
df = df.set_index("start_time").sort_index()

# Resample to hourly frequency, taking the mean of prices within each hour
price_cols = ["Day-ahead Price (EUR/MWh)"]

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
    f"./data/02_stg/entsoe/daprice_1h/ingested_at={ingested_at_st}")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_PATH / "DAPrices_1h.csv"

df_1h.to_csv(OUTPUT_PATH, index=False)
