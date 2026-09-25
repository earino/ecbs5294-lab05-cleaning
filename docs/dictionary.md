# Data dictionary — silver

## `data/silver/waste.parquet`

Municipal waste per inhabitant, from Eurostat's `env_wasmun` (`data/raw/env_wasmun.tsv`), made by `scripts/clean.py`.

- **One row per `(geo, year, wst_oper)`**: one place, one year, one waste operation.
- **One unit**: kilograms per inhabitant (`KG_HAB`). The raw file also has every series in thousand tonnes (`THS_T`);
  those observations are set aside, and counted.
- **Frequency**: annual (`freq = A`) for every row of the raw file.
- Every observation of the raw file that is not in silver — in `THS_T`, or a cell that cannot be read — is in
  `data/silver/rejects.csv`, each with its reason.

| Column | Type | Meaning | Allowed values | Missing means | Made from |
|---|---|---|---|---|---|
| `geo` | VARCHAR | the country, as Eurostat codes it (`DE` Germany, `EL` Greece, `XK` Kosovo), or `EU27_2020`, the EU as a whole | the 38 codes in the file | never missing | the 4th field of the packed first column |
| `wst_oper` | VARCHAR | the waste operation: `GEN` generated, `TRT` treated, `RCY` recycled, … | the codes in `data/raw/codelist_wst_oper.tsv` | never missing | the 2nd field of the packed first column |
| `year` | INTEGER | the year | 2010–2024 | never missing | a column header in the raw file, turned into a row |
| `value` | DOUBLE | kilograms of municipal waste per inhabitant, in that year | 0 or more | Eurostat wrote `:`, "not available" | the number Eurostat wrote in the cell |
| `flag` | VARCHAR | Eurostat's note on that value: `e` estimated, `p` provisional, `b` break in the series, `i` imputed by Eurostat, or a combination (`ep`, `be`) | the codes in `data/raw/codelist_obs_flag.tsv` | the value has no flag | the letters Eurostat wrote after the number, kept as written |
| `is_aggregate` | BOOLEAN | `true` for `EU27_2020`, a group of countries; `false` for a country | `true`, `false` | never missing | `geo` |
