from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# AS_OF = pd.to_datetime(
#     "2025-12-13T09-30-00Z",
#     format="%Y-%m-%dT%H-%M-%SZ",
#     utc=True
# )
AS_OF = pd.Timestamp.now(tz="UTC")

# ------------------------------------------------
# Load price data
# ------------------------------------------------
RAW_ROOT = Path("./data/02_stg/entsoe/daprice_1h")
files = sorted(RAW_ROOT.glob("ingested_at=*/DAPrices_1h.csv"))
print(f"Found {len(files)} files.")
dfs = []
candidates = []
for fp in files:

    # ingested_at aus Pfad extrahieren (kein Magic)
    ingested_at_str = fp.parent.name.split("=", 1)[1]
    ingested_at = pd.to_datetime(
        ingested_at_str,
        format="%Y-%m-%dT%H-%M-%SZ",
        utc=True
    )
    if ingested_at > AS_OF:
        continue
    candidates.append((ingested_at, fp))

chosen_ingested_at, chosen_fp = max(candidates, key=lambda x: x[0])
df_price = pd.read_csv(chosen_fp)
df_price["ingested_at"] = pd.Timestamp(chosen_ingested_at)

# ------------------------------------------------
# Load load data
# ------------------------------------------------
RAW_ROOT = Path("./data/02_stg/entsoe/load_1h")
files = sorted(RAW_ROOT.glob("ingested_at=*/Load_1h.csv"))
print(f"Found {len(files)} files.")
dfs = []
for fp in files:

    # ingested_at aus Pfad extrahieren (kein Magic)
    ingested_at_str = fp.parent.name.split("=", 1)[1]
    ingested_at = pd.to_datetime(
        ingested_at_str,
        format="%Y-%m-%dT%H-%M-%SZ",
        utc=True
    )
    if ingested_at > AS_OF:
        continue
    df_load = pd.read_csv(fp)
    df_load["ingested_at"] = pd.Timestamp(ingested_at)

    dfs.append(df_load)

df_load = pd.concat(dfs, ignore_index=True)

# ------------------------------------------------
# Load generation data
# ------------------------------------------------
RAW_ROOT = Path("./data/02_stg/entsoe/generation_1h")
files = sorted(RAW_ROOT.glob("ingested_at=*/Generation_1h.csv"))
print(f"Found {len(files)} files.")
dfs = []
for fp in files:

    # ingested_at aus Pfad extrahieren (kein Magic)
    ingested_at_str = fp.parent.name.split("=", 1)[1]
    ingested_at = pd.to_datetime(
        ingested_at_str,
        format="%Y-%m-%dT%H-%M-%SZ",
        utc=True
    )
    if ingested_at > AS_OF:
        continue
    df_gen = pd.read_csv(fp)
    df_gen["ingested_at"] = pd.Timestamp(ingested_at)

    dfs.append(df_gen)

df_gen = pd.concat(dfs, ignore_index=True)

# ------------------------------------------------
# Load weather data
# ------------------------------------------------
RAW_ROOT = Path("./data/02_stg/weather/meteostat_1h")
files = sorted(RAW_ROOT.glob("ingested_at=*/Meteostat_1h.csv"))
print(f"Found {len(files)} files.")
dfs = []
candidates = []
for fp in files:

    # ingested_at aus Pfad extrahieren (kein Magic)
    ingested_at_str = fp.parent.name.split("=", 1)[1]
    ingested_at = pd.to_datetime(
        ingested_at_str,
        format="%Y-%m-%dT%H-%M-%SZ",
        utc=True
    )
    if ingested_at > AS_OF:
        continue
    candidates.append((ingested_at, fp))

chosen_ingested_at, chosen_fp = max(candidates, key=lambda x: x[0])
df_weather = pd.read_csv(chosen_fp)
df_weather["ingested_at"] = pd.Timestamp(chosen_ingested_at)

# Rename time column to start_time in weather data
df_weather = df_weather.rename(columns={"time": "start_time"})
print(df_weather.columns)
print(df_weather.head())
# ------------------------------------------------
# Join data
# ------------------------------------------------
# Ensure 'start_time' exists in all DataFrames
if 'start_time' not in df_price.columns:
    raise KeyError("Column 'start_time' is missing in df_price")
if 'start_time' not in df_load.columns:
    raise KeyError("Column 'start_time' is missing in df_load")
if 'start_time' not in df_gen.columns:
    raise KeyError("Column 'start_time' is missing in df_gen")
if 'start_time' not in df_weather.columns:
    raise KeyError("Column 'start_time' is missing in df_weather")


df_price["start_time"] = pd.to_datetime(df_price["start_time"], utc=True)
df_weather["start_time"] = pd.to_datetime(df_weather["start_time"], utc=True)
df_gen["start_time"] = pd.to_datetime(df_gen["start_time"], utc=True)
df_load["start_time"] = pd.to_datetime(df_load["start_time"], utc=True)

df = df_price.merge(
    df_load,
    on="start_time",
    how="outer",
    suffixes=("_price", "_load")
).merge(
    df_gen,
    on="start_time",
    how="outer",
    suffixes=("", "_gen")
).merge(
    df_weather,
    on="start_time",
    how="outer",
    suffixes=("", "_weather")
)

# Add ingestion timestamp
ingested_at = pd.Timestamp.now(tz="UTC")
df["ingested_at"] = ingested_at
ingested_at_st = (
    ingested_at.strftime("%Y-%m-%dT%H-%M-%SZ")
)

OUTPUT_PATH = Path(
    f"./data/03_marts/as_of={AS_OF.strftime('%Y-%m-%dT%H-%M-%SZ')}")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_PATH / "Joined.csv"

df.to_csv(OUTPUT_PATH, index=False)
