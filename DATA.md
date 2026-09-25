# Data in this repository

Everything under `data/raw/` is real, public data, committed on purpose and **never edited**. Where it came from, its license, and exactly what was changed for this course:

## Eurostat — municipal waste (env_wasmun) and greenhouse-gas emissions (env_air_gge)

**Source:** Eurostat, dissemination API (SDMX 2.1, TSV). Municipal waste by waste management operations,
`env_wasmun`: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/env_wasmun/?format=TSV&compressed=false&startPeriod=2010` (fetched 2026-09-19, SHA-256 `efe7d4fa295909d0…`). Greenhouse gas emissions by source sector, `env_air_gge`:
retrieved through Eurostat's asynchronous extraction of the full dataset from 2010 (the synchronous request for a
file this size is queued by Eurostat, and the old bulk-download URL is retired). Code lists for the dimensions
and the observation flags: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/<LIST>?format=TSV`.

**License:** Eurostat data are reusable under **CC BY 4.0** (Eurostat copyright and reuse policy). Attribution:
*Source: Eurostat, env_wasmun / env_air_gge*, © European Union.

**Changes made for this course:** `env_wasmun.tsv` is unmodified. `env_air_gge_ghg.tsv` keeps only the rows whose
pollutant is `GHG` (all greenhouse gases in CO₂ equivalent), in both units, every source sector, every country;
the header line and every kept row are byte-for-byte as Eurostat published them. The four `codelist_*.tsv` files
are Eurostat's labels for the codes, unmodified.

**How to read the raw files:** the first column packs several dimensions separated by commas (its header says
which, e.g. `freq,unit,airpol,src_crf,geo\TIME_PERIOD`); each year is a column; a value may carry a flag after a
space (`628 e`); `:` means not available and may itself carry a flag (`: m`). Flag meanings: `codelist_obs_flag.tsv`.

## Files

| File | Bytes | SHA-256 |
|---|---:|---|
| `codelist_airpol.tsv` | 2,028 | `3353d0c5d6bce625…` |
| `codelist_obs_flag.tsv` | 2,417 | `5631f76c7c9b8e00…` |
| `codelist_src_crf.tsv` | 7,516 | `085697dd09782f1a…` |
| `codelist_wst_oper.tsv` | 2,763 | `9c54656e6ad17c80…` |
| `env_air_gge_ghg.tsv` | 1,355,639 | `e4d0fe960b1c4b13…` |
| `env_wasmun.tsv` | 65,823 | `efe7d4fa295909d0…` |
