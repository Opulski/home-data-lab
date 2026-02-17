import os

import pandas as pd
from entsoe import EntsoePandasClient

ENTSOE_API_KEY = os.getenv("ENTSOE_TOKEN")
if ENTSOE_API_KEY is None:
    raise RuntimeError("ENTSOE_TOKEN not set")

client = EntsoePandasClient(api_key=ENTSOE_API_KEY)

start = pd.Timestamp("20240101", tz="Europe/Brussels")
end = pd.Timestamp("20241201", tz="Europe/Brussels")
country_code = "DE_LU"
type_marketagreement_type = "A01"
contract_marketagreement_type = "A01"
process_type = "A51"


# df = client.query_load_and_forecast(country_code, start=start, end=end)
df = client.query_generation(country_code, start=start, end=end, psr_type=None)
print(df.head())
