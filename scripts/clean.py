"""Bronze -> silver: municipal waste per inhabitant, from Eurostat's raw TSV.

Run by pipeline.py (or on its own: uv run python scripts/clean.py). Reads data/raw/env_wasmun.tsv and never edits it.
Writes data/silver/waste.parquet, the silver table (docs/dictionary.md says what silver must contain), and
data/silver/rejects.csv, every observation that is not in silver, with its reason.

A colleague wrote this parser. It reuses the steps from another Eurostat file. It runs without an error.
"""
import os
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
Path("data/silver").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

# A. Bronze: the file as it arrived. Every cell is read as text, so nothing is converted before we say so.
#    The first column packs four fields, "freq,wst_oper,unit,geo\TIME_PERIOD"; we call it `series`.
con.sql("""
    CREATE VIEW bronze AS
    SELECT * FROM read_csv('data/raw/env_wasmun.tsv', delim = '\t', all_varchar = true, names = ['series'])
""")

# B. Long: one observation per (freq, wst_oper, unit, geo, year). Split the packed column; turn the years into rows.
#    INCLUDE NULLS: without it, UNPIVOT silently drops an empty cell, and it could never be counted.
con.sql("""
    CREATE VIEW long AS
    SELECT split_part(series, ',', 1) AS freq,
           split_part(series, ',', 2) AS wst_oper,
           split_part(series, ',', 3) AS unit,
           split_part(series, ',', 4) AS geo,
           CAST(year AS INTEGER)      AS year,
           cell                                   -- the text Eurostat wrote in that cell
    FROM bronze
    UNPIVOT INCLUDE NULLS (cell FOR year IN (COLUMNS('^[0-9]{4}$')))
""")

#    Eurostat's list of flags: every letter a cell may carry after its number (column `code`), and what it means.
con.sql("""
    CREATE VIEW flags AS
    SELECT code, label
    FROM read_csv('data/raw/codelist_obs_flag.tsv', delim = '\t', header = false, names = ['code', 'label'])
""")

# C. Parse and sort: the colleague's. The README says what this section must become: you rewrite it.
#    It must end with two views. `parsed`: every observation of `long`, with `value`, `flag`, and a `reason` that is
#    NULL when the observation goes into silver and says why when it does not. `silver`: the dictionary's columns.
con.sql("""
    CREATE VIEW parsed AS
    SELECT *,
           TRY_CAST(cell AS DOUBLE) AS value,          -- kilograms per inhabitant
           CAST(NULL AS VARCHAR)    AS flag,           -- see docs/dictionary.md
           CASE                                        -- the first WHEN that is true wins
               WHEN unit <> 'KG_HAB' THEN 'not KG_HAB' -- silver keeps one unit; the file has THS_T for every row too
           END AS reason
    FROM long
""")
con.sql("""
    CREATE VIEW silver AS
    SELECT geo, wst_oper, year, value, flag,
           geo = 'EU27_2020' AS is_aggregate    -- the EU as a whole: a group of countries, not a country
    FROM parsed
    WHERE reason IS NULL
""")

# D. Write silver, and every observation that is not in silver, with its reason. Supplied: do not change it.
#    Both files are overwritten on every run, so two runs make the same files.
con.sql("COPY (SELECT * FROM silver ORDER BY geo, wst_oper, year) TO 'data/silver/waste.parquet' (FORMAT parquet)")
con.sql("""
    COPY (SELECT freq, wst_oper, unit, geo, year, cell, reason FROM parsed WHERE reason IS NOT NULL
          ORDER BY geo, wst_oper, unit, year)
    TO 'data/silver/rejects.csv' (HEADER)
""")
n = con.sql("SELECT COUNT(*) FROM 'data/silver/waste.parquet'").fetchone()[0]
m = con.sql("SELECT COUNT(*) FROM read_csv('data/silver/rejects.csv', all_varchar = true)").fetchone()[0]
print(f"silver: {n:,} rows -> data/silver/waste.parquet; set aside: {m:,} rows -> data/silver/rejects.csv")

# ---------------------------------------------------------------------------------------------------------------------
# Your work starts here. The README says what each section must do.
# ---------------------------------------------------------------------------------------------------------------------

# E. The accounting: the four destinations, counted from the two files section D wrote.
#    rejected (cannot be read) and excluded (not KG_HAB): rows of data/silver/rejects.csv, by reason.
#    aggregate (EU27_2020) and retained (everything else): rows of data/silver/waste.parquet.
#    Print them as one line that adds up to the observations in `long`, on every run. Stop the run if it does not.


# F. The key check.
#    Stop the run, with the number in the message, if silver's key is not unique.
