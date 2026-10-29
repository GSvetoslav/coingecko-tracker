# CoinGecko Tracker

A small learning project where I'm building a data pipeline in Python. It pulls cryptocurrency market data from the [CoinGecko API](https://docs.coingecko.com/), cleans it with pandas, and checks that the data makes sense.

I'm building this step by step to practice data engineering basics, so the code is kept simple and commented on purpose. The plan is to store the data in PostgreSQL and run the pipeline with Apache Airflow.

## What it does right now

1. **Extract**: gets market data (price, volume, supply...) for the top coins from CoinGecko. It loops through several pages, because the API returns at most 250 coins per page.
2. **Transform / clean**: with pandas it:
   - keeps only the columns I need
   - converts `last_updated` to a real datetime
   - makes text consistent (e.g. symbols in uppercase)
   - removes duplicate coins and rows without a price
   - adds a `fetched_at` column (when I pulled the data)
3. **Validate**: checks that the data is sane before going further:
   - the table is not empty
   - important columns have no missing values
   - every coin `id` is unique
   - prices are above zero
   - volume and supply are never negative
   - `max_supply` is never lower than `circulating_supply`

A note on `max_supply`: it is empty for many coins (like Ethereum or Tether) because they have no supply cap. That's expected, so those values are kept as missing instead of being dropped or filled with 0.

## Tech used

- Python 3
- `requests` for the API calls
- `pandas` for cleaning and validation
- `python-dotenv` to keep the API key out of the code

**Planned:** PostgreSQL to store the data, and Apache Airflow to run and schedule the pipeline (orchestration).

## Project structure

```
coingecko-tracker/
├── main.py            # the whole pipeline (for now)
├── requirements.txt   # Python libraries needed
├── .env.example       # shows which variable is needed (no real key!)
├── .gitignore         # keeps .env and .venv out of git
└── README.md
```

## How to run it

**1. Clone the repo**

```bash
git clone https://github.com/YOUR-USERNAME/coingecko-tracker.git
cd coingecko-tracker
```

**2. Create a virtual environment and install the libraries**

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows PowerShell: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add your API key**

Get a free demo key from CoinGecko, then copy the example file and put your key in it:

```bash
cp .env.example .env
```

Open `.env` and set:

```
COINGECKO_API_KEY=your_key_here
```

The `.env` file is ignored by git, so the key never gets uploaded.

**4. Run**

```bash
python main.py
```

If everything is fine, you will see the cleaned data and the message `All validation checks passed`.

## What I learned so far

- Calling an API with `requests` (headers, parameters, timeout, error checking)
- Keeping secrets in a `.env` file and out of git
- Pagination: looping over pages and collecting the results
- Cleaning data with pandas (types, duplicates, missing values)
- Writing validation checks with `assert`
- Working with Python inside WSL (Ubuntu on Windows)

## Next steps

- [ ] Save the cleaned data to a file (CSV or Parquet)
- [ ] Save the raw API response before cleaning
- [ ] Split the code into `extract`, `transform` and `load` functions
- [ ] Add retries for rate limit errors (HTTP 429) and use logging instead of `print`
- [ ] Write some tests with `pytest`
- [ ] Load the data into PostgreSQL (with upserts, so re-running does not create duplicates)
- [ ] Run it with Docker
- [ ] Orchestrate and schedule the pipeline with Apache Airflow (extract, transform and load as separate tasks)

## Data source

Data comes from the [CoinGecko API](https://www.coingecko.com/en/api). Please check their terms and rate limits if you use it.
