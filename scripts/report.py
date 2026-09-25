"""Silver -> gold: municipal waste generated per inhabitant, by country, in 2024, and the change since 2010.

Run by pipeline.py (or on its own: uv run python scripts/report.py). Reads data/silver/waste.parquet, writes
data/gold/waste_per_inhabitant.csv, and prints it. This script is correct if silver is right. Do not change it.
"""
import os
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
Path("data/gold").mkdir(parents=True, exist_ok=True)
con = duckdb.connect()

# Gold: one row per country. Waste generated (wst_oper GEN), kilograms per inhabitant.
# The EU27_2020 row is a group of countries, not a country: it is printed below the table, not in it.
con.sql("""
    CREATE VIEW gold AS
    SELECT geo,
           SUM(CASE WHEN year = 2010 THEN value END) AS kg_2010,
           MAX(CASE WHEN year = 2010 THEN flag END)  AS flag_2010,
           SUM(CASE WHEN year = 2024 THEN value END) AS kg_2024,
           MAX(CASE WHEN year = 2024 THEN flag END)  AS flag_2024,
           kg_2024 - kg_2010                         AS change_kg
    FROM 'data/silver/waste.parquet'
    WHERE wst_oper = 'GEN' AND NOT is_aggregate
    GROUP BY geo
""")
con.sql("COPY (SELECT * FROM gold ORDER BY kg_2024 DESC NULLS LAST, geo) TO 'data/gold/waste_per_inhabitant.csv' (HEADER)")

table = con.sql("SELECT * FROM gold ORDER BY kg_2024 DESC NULLS LAST, geo").df()
table[["flag_2010", "flag_2024"]] = table[["flag_2010", "flag_2024"]].fillna("-")
print("Municipal waste generated, kg per inhabitant (flag: e estimated, p provisional, b break in series, i imputed)")
print(table.to_string(index=False, na_rep="-", float_format=lambda v: f"{v:g}"))

countries, with_2024, with_change, flagged_2024 = con.sql("""
    SELECT COUNT(*), COUNT(kg_2024), COUNT(change_kg), COUNT(*) FILTER (WHERE kg_2024 IS NOT NULL AND flag_2024 IS NOT NULL)
    FROM gold
""").fetchone()
eu = con.sql("""
    SELECT value, flag FROM 'data/silver/waste.parquet' WHERE wst_oper = 'GEN' AND is_aggregate AND year = 2024
""").fetchone()
print(f"\nCountries in gold: {countries}")
print(f"Countries with a 2024 value: {with_2024}")
print(f"Countries with a change since 2010: {with_change}")
print(f"2024 values that carry a flag: {flagged_2024}")
if eu is not None:
    eu_value = "-" if eu[0] is None else f"{eu[0]:g}"
    print(f"EU27_2020 (a group of countries, not in the table), 2024: {eu_value} {eu[1] or ''}".rstrip())
print("-> data/gold/waste_per_inhabitant.csv")
