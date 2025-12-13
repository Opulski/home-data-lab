# ----------------------------------------------------------------------
# Baseline Regression Model
# ----------------------------------------------------------------------

from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from pathlib import Path
from datetime import datetime, timezone
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--as-of",
    help="YYYY-MM-DDTHH-MM-SSZ (optional for local debug)"
)
args = parser.parse_args()

if args.as_of:
    as_of_str = args.as_of
else:
    # ---------- LOCAL DEBUG DEFAULT ----------
    as_of_str = "2025-12-13T10-17-52Z"

fp = Path(f"./data/03_marts/as_of={as_of_str}/Joined.csv")
df = pd.read_csv(fp)

print(f"Loaded marts as_of={as_of_str}")


RENEWABLE = [
    "Solar", "Wind Onshore", "Wind Offshore",
    "Hydro Run-of-river and pondage",
    "Other renewable",
    "Geothermal"
]

FOSSIL = [
    "Fossil Gas", "Fossil Hard coal", "Fossil Brown coal/Lignite",
    "Fossil Oil", "Fossil Coal-derived gas"
]

# optional (je nachdem wie du’s nutzen willst)
HYDRO = ["Hydro Water Reservoir", "Hydro Pumped Storage",
         "Hydro Run-of-river and pondage"]
OTHER = ["Biomass", "Waste", "Other"]

df["gen_renewable_mw"] = df[RENEWABLE].sum(axis=1)
df["gen_fossil_mw"] = df[FOSSIL].sum(axis=1)
df["gen_total_mw"] = df[[*RENEWABLE, *FOSSIL, *HYDRO, *OTHER]].sum(axis=1)
df["gen_res_share"] = df["gen_renewable_mw"] / df["gen_total_mw"] * 100.0


df["wind_total"] = df["Wind Onshore"] + df["Wind Offshore"]

df["wind_ramp_1h"] = df["wind_total"] - df["wind_total"].shift(1)
df["solar_ramp_1h"] = df["Solar"] - df["Solar"].shift(1)

df["res_ramp_1h"] = (
    df["wind_ramp_1h"] + df["solar_ramp_1h"]
)

df["load_ramp_1h"] = (
    df["Actual Total Load (MW)"] - df["Actual Total Load (MW)"].shift(1)
)

DROP_COLS = RENEWABLE + FOSSIL + HYDRO + OTHER
df = df.drop(columns=DROP_COLS, errors="ignore")


df["load_forecast_mw"] = df["Day-ahead Total Load Forecast (MW)"]
df["load_actual_mw"] = df["Actual Total Load (MW)"]

df["load_error_mw"] = df["load_actual_mw"] - \
    df["load_forecast_mw"]


df["start_time"] = pd.to_datetime(
    df["start_time"],
    utc=True,
    errors="coerce"
)
df["hour"] = df["start_time"].dt.hour
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

df["dow"] = df["start_time"].dt.weekday
df["dow_sin"] = np.sin(2 * np.pi * df["dow"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["dow"] / 7)


FEATURES = [
    "load_forecast_mw",
    "load_error_mw",
    "gen_renewable_mw",
    "gen_fossil_mw",
    "gen_res_share",
    "hour",
    "hour_sin",
    "hour_cos",
    "dow",
    "dow_sin",
    "dow_cos",
    "wind_ramp_1h",
    "solar_ramp_1h",
    "res_ramp_1h",
    "load_ramp_1h"
]

TARGET = "Day-ahead Price (EUR/MWh)"

df_model = df.sort_values("start_time").reset_index(drop=True)

split_ts = pd.Timestamp("2025-09-01T00:00:00Z")

train = df_model[df_model["start_time"] < split_ts]
test = df_model[df_model["start_time"] >= split_ts]


# nach dem Split:
train = train.dropna(subset=FEATURES + [TARGET])
test = test.dropna(subset=FEATURES + [TARGET])

X_train = train[FEATURES]
y_train = train[TARGET]
X_test = test[FEATURES]
y_test = test[TARGET]

assert "Day-ahead Price (EUR/MWh)" not in FEATURES
assert not any("price" in f.lower() for f in FEATURES)
print(train["start_time"].max(), test["start_time"].min())


model = LinearRegression()
model.fit(X_train, y_train)

y_pred_base = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred_base))
mae = mean_absolute_error(y_test, y_pred_base)

print(f"RMSE: {rmse:.2f}")
print(f"MAE:  {mae:.2f}")


df = df.sort_values("start_time")

y_naive = df.loc[test.index, "Day-ahead Price (EUR/MWh)"].shift(24)

mask = y_naive.notna() & y_test.notna()
rmse_naive = np.sqrt(mean_squared_error(y_test[mask], y_naive[mask]))
print(f"Naive RMSE: {rmse_naive:.2f}")

coef = pd.Series(
    model.coef_,
    index=FEATURES
).sort_values()

print(coef)


r2 = r2_score(y_test, y_pred_base)
print(f"R²: {r2:.3f}")


resid = y_test - y_pred_base
print(resid.describe())

# ----------------------------------------------------------------------
# Residual Modeling
# ----------------------------------------------------------------------

# create residual target for train and test set
test["y_pred_base"] = model.predict(X_test)
test["residual"] = test[TARGET] - test["y_pred_base"]
train["y_pred_base"] = model.predict(X_train)
train["residual"] = train[TARGET] - train["y_pred_base"]

TARGET_RESIDUAL = "residual"

X_train = train[FEATURES]
y_train = train[TARGET_RESIDUAL]
X_test = test[FEATURES]
y_test = test[TARGET_RESIDUAL]


res_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=5,
    random_state=42
)

res_model.fit(X_train, y_train)
y_pred_resid = res_model.predict(X_test)
rmse_res = np.sqrt(mean_squared_error(y_test, y_pred_resid))
mae_res = mean_absolute_error(y_test, y_pred_resid)
print(f"Residual Model RMSE: {rmse_res:.2f}")
print(f"Residual Model MAE:  {mae_res:.2f}")
print(f"Residual Model R²:   {r2_score(y_test, y_pred_resid):.3f}")

# ----------------------------------------------------------------------
# Final Evaluation
# ----------------------------------------------------------------------

y_final_pred = test["y_pred_base"] + y_pred_resid
rmse_final = np.sqrt(mean_squared_error(
    test[TARGET], y_final_pred))
mae_final = mean_absolute_error(
    test[TARGET], y_final_pred)
print(f"Final Model RMSE: {rmse_final:.2f}")
print(f"Final Model MAE:  {mae_final:.2f}")

y_pred_final = y_pred_base + y_pred_resid
# final R²
r2_final = r2_score(test[TARGET], y_pred_final)
print(f"Final R²: {r2_final:.3f}")

# Residuals vs Predicted plot
resid = test[TARGET] - y_pred_final

plt.figure(figsize=(10, 6))
plt.scatter(y_pred_final, resid, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel("Predicted Values")
plt.ylabel("Residuals")
plt.title("Residuals vs Predicted Values")
plt.show()
