# Obtaining the Source Data

This project uses 5 raw files, all official Argentine government statistics published on [datos.gob.ar](https://datos.gob.ar). They are **not committed to this repository** (see `.gitignore`) — download them yourself before running the ETL.

## Files needed

| # | File to download | Search for on datos.gob.ar | Format | Save as |
|---|---|---|---|---|
| 1 | Average private-sector salary by department | `salario-promedio-por-departamento` | XLSX | `Salario-promedio-por-departamento.xlsx` |
| 2 | National CPI, base Dec-2016 = 100, monthly | `indice-precios-al-consumidor-nivel-general-base-diciembre-2016-mensual` | CSV | `indice-precios-al-consumidor-nivel-general-base-diciembre-2016-mensual.csv` |
| 3 | CLAE economic activity classification dictionary | `clae_agg` | CSV | `clae_agg.csv` |
| 4 | Registered private-sector jobs by province and activity | `puestos_priv` | CSV | `puestos_priv.csv` |
| 5 | Average monthly wage by economic activity (national) | `w_mean_privado_mensual_por_clae2` | CSV | `w_mean_privado_mensual_por_clae2.csv` |

## Where to put them

Place all 5 files in the folder configured by `DATA_FOLDER` in your `.env` (default: `data_raw/`, at the project root — sibling to this `data/` folder, not inside it). File names must match exactly what's set in `DATA_FILE`, `IPC_FILE`, `CLAE_FILE`, `PUESTOS_FILE`, and `SALARIO_CLAE_FILE` in your `.env` — see [`.env.example`](../.env.example).

`scripts/extract.py` validates that each configured path exists before reading it and raises a `FileNotFoundError` naming the exact missing file if one is not found in that folder.

For the full pipeline setup (database, `.env`, running the ETL), see the [main README](../README.md#installation).
