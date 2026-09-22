# Architecture

## Overview

```text
Official Government Datasets (datos.gob.ar)
              │
              ▼
        Python (pandas)
     extract → transform → load
              │
              ▼
         PostgreSQL
      (star-schema data warehouse)
              │
              ▼
          Power BI
   (data model + DAX measures)
              │
              ▼
    7-page interactive dashboard
    (Overview + 6 analytical pages)
```

## Components

### 1. Extract (`scripts/extract.py`)

Reads the 5 source files (1 XLSX, 4 CSV) from the folder configured in `DATA_FOLDER`. Each file is read through a single reusable helper, `read_dataset()`, which validates the path exists before attempting to read it and raises a `FileNotFoundError` with the exact missing path if not. This replaced five near-duplicate read blocks that existed in the project's first version.

### 2. Transform (`scripts/transform.py`)

One function per source dataset, each returning a DataFrame shaped to match its target table's grain:

- `transform_salarios` — reshapes the wide (one column per month) salary file into long format, builds `dim_provincia` and `dim_departamento`, drops departments with >95% missing salary history.
- `transform_ipc` — types and validates the national CPI series; drops rows with an invalid date or CPI value.
- `transform_clae` — builds `dim_clae` at `clae2` grain only. An earlier version of this function also kept `clae3`/`clae3_desc` columns, but since a single `clae2` maps to multiple `clae3` sub-activities, those columns were not functionally dependent on the table's key and were removed during the project's technical audit.
- `transform_puestos_priv` — maps province names to INDEC codes via an explicit dictionary; raises a descriptive `ValueError` listing any unmapped province names instead of silently dropping them. Replaces the source's `-99` null sentinel with `NULL`.
- `transform_salario_clae` — types and validates the activity-level wage series.
- `transform()` — orchestrates all of the above and builds `dim_fecha` from the union of every date present across the four fact tables.

### 3. Load (`scripts/load.py`)

Truncates all 8 tables and reloads them inside a single transaction (`engine.begin()`), in dependency order — dimensions first, then fact tables. If any step fails, the entire transaction rolls back, leaving the database in its previous state. This is a full-refresh strategy, not incremental — an appropriate simplification for a dataset that updates on a monthly government release cycle, not a real-time source.

### 4. Database connection (`scripts/database.py`)

Builds a SQLAlchemy engine from environment variables loaded via `python-dotenv`. No credentials are hardcoded anywhere in the codebase.

### 5. Orchestration (`scripts/main.py`)

Runs extract → transform → load in sequence and prints a per-table row count summary on completion.

### 6. Data warehouse (PostgreSQL)

A star schema with 4 dimensions and 4 fact tables. See `data_dictionary.md` for the full column-level reference and each fact table's grain. Referential integrity is enforced via foreign keys, and basic domain validity (non-negative wages, valid month/quarter ranges) via `CHECK` constraints.

### 7. Analysis layer (Power BI)

Connects directly to PostgreSQL. The data model mirrors the warehouse's star schema, with DAX measures centralized in a dedicated `_Medidas` table rather than scattered across fact tables. The dashboard has 7 pages: an Overview summarizing 5 key metrics, and 6 analytical pages covering salary evolution, provincial ranking, purchasing power, the nominal-vs-real comparison, productive structure, and activity-level wages.

## Design decisions worth knowing

- **Full reload, not incremental**: appropriate given the source data's release cadence and the project's scale (hundreds of thousands of rows, not millions).
- **No raw data committed to git**: source files are downloaded locally per `data/README.md`; only the pipeline and its output schema are version-controlled.
- **Measures anchored to their own fact table's latest date, not to `dim_fecha`'s**: `dim_fecha` is built from the union of all 4 fact tables' dates, and the CPI series (`fact_ipc`) extends further into the future than the salary/employment series. Any DAX measure meant to represent "the current value" explicitly anchors to `CALCULATE(MAX('fact_salarios'[fecha]))` (or the equivalent for its own table) rather than `MAX(dim_fecha[fecha])`, to avoid silently picking up a date with no corresponding salary data.