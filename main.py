import os
import requests
from dotenv import load_dotenv
import pandas as pd


# Load variables from the .env file
load_dotenv()

# Define the API endpoint
url = "https://api.coingecko.com/api/v3/coins/markets"

# Read the .env file with os
api_key = os.getenv("COINGECKO_API_KEY")

# Check if API key is set in .env file
if not api_key:
    raise RuntimeError("COINGECKO_API_KEY is not set in .env")

headers = {
    "x-cg-demo-api-key": api_key
}

# Define the request parameters
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,
    "page": 1,
    "sparkline": False
}

# Send request with specified URL, API KEY, Param and timeout
response = requests.get(url, headers=headers, params=params, timeout=30)

# Check whether the request succeeded
response.raise_for_status()

# Convert the JSON response into Python data
data = response.json()

df = pd.DataFrame(data)

# 2-- CLEANUP THE DATA

# Keep only the columns we need
columns_to_keep = [
       "id",
       "symbol",
       "name",
       "current_price",
       "total_volume",
       "circulating_supply",
       "total_supply",
       "max_supply",
       "last_updated",
]

# .copy() makes a separate DataFrame
df = df[columns_to_keep].copy()

# last_updated arrives as string, so convert it to a real datetime
df["last_updated"] = pd.to_datetime(df["last_updated"])

# Make text consistent
df["symbol"] = df["symbol"].str.upper()
df["name"] = df["name"].str.strip()
df["current_price"] = df["current_price"].round(2)

# Drop duplicates: each coin id should appear only once
df = df.drop_duplicates(subset="id")

# Drop Rows without price
df = df.dropna(subset="current_price")

# Add a column saying when WE fetched the data
df["fetched_at"] = pd.Timestamp.now(tz="UTC")

# Reset the row numbers (0, 1, 2...) after dropping rows
df = df.reset_index(drop=True)

# 3-- VALIDATE THE DATA
# Each assert says "this must be true". If not, the script stops
# and prints the message, so bad data never gets saved.

# Check 1: we got data at all
assert len(df) > 0, "The DataFrame is empty"

# Check 2: the important columns have no missing values
# (max_supply is NOT in this list, because NaN is normal there)
required_columns = ["id", "symbol", "name", "current_price", "last_updated"]
assert df[required_columns].notna().all().all(), "Missing values in required columns"

# Check 3: each coin id appears only once
assert df["id"].is_unique, "Duplicate coin ids found"

# Check 4: prices must be above zero
assert (df["current_price"] > 0).all(), "Found a price <= 0"

# Check 5: volume and supply can't be negative
number_columns = ["total_volume", "circulating_supply", "total_supply"]
assert (df[number_columns] >= 0).all().all(), "Found a negative volume or supply"

# Check 6: if a coin has a max supply, it can't be below circulating supply
# We only compare rows where max_supply exists, because NaN can't be compared
has_cap = df["max_supply"].notna()
assert (df.loc[has_cap, "max_supply"] >= df.loc[has_cap, "circulating_supply"]).all(), \
    "max_supply is lower than circulating_supply"

print("All validation checks passed")
