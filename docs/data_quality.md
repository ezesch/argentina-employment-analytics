# Data Quality

This document records the data quality issues found while building the pipeline, how each was detected, and how it was resolved. Numbers below were recomputed directly against the raw source files in `data_raw/` to confirm they still hold.

## Summary

| # | Issue | Table affected | Detected via | Resolution |
|---|---|---|---|---|
| 1 | `clae2` → `clae3` is not a 1-to-many-safe relationship for a `clae2`-grain table | `dim_clae` | Manual review of `clae_agg.csv` while designing the dimension | Dropped `clae3`/`clae3_desc` from `dim_clae`; kept it at `clae2` grain only |
| 2 | Source uses `-99` as a null sentinel instead of a blank cell | `fact_puestos_priv`, `fact_salario_clae` | Inspecting raw value distributions in `puestos_priv.csv` / `w_mean_privado_mensual_por_clae2.csv` | Replaced `-99` with `NULL` in `transform_puestos_priv()` / `transform_salario_clae()` |
| 3 | A small number of departments have almost no salary history | `fact_salarios` / `dim_departamento` | Null-rate check per department after reshaping to long format | Dropped departments with >95% missing `sueldo_promedio` in `transform_salarios()` |
| 4 | Province names in the source don't match INDEC codes 1:1 by construction | `fact_puestos_priv` | Explicit mapping dictionary + fail-fast validation in `transform_puestos_priv()` | Raises a `ValueError` listing any unmapped names instead of silently dropping rows (in practice, all 24 provinces map correctly — see Validations below) |
| 5 | IPC source column types are inconsistent (mixed string/numeric on ingestion) | `fact_ipc` | Type coercion during `transform_ipc()` | Coerces `fecha` and `ipc_nacional` with `errors="coerce"` and drops rows that fail to parse |

## Issues in detail

### 1. `clae2`/`clae3` cardinality — columns removed from `dim_clae`

An earlier version of `dim_clae` kept `clae3`/`clae3_desc` alongside `clae2`. Re-checking `clae_agg.csv` directly:

- 86 distinct `clae2` codes.
- **62 of those 86 (72%) map to more than one distinct `clae3` sub-activity.**

Since `dim_clae` is built and used at `clae2` grain (it's the FK target for `fact_puestos_priv` and `fact_salario_clae`, both of which only carry `clae2`), `clae3`/`clae3_desc` were not functionally dependent on the table's key — keeping them would have meant either duplicating `clae2` rows (breaking the PK) or arbitrarily picking one `clae3` per `clae2` (silently losing information). Both columns were removed; a `clae2`-grain `dim_clae` is the correct model for the data this project actually has. A properly-modeled `dim_clae3` (at its own grain, as its own table) is listed under Future Improvements in the README rather than bolted onto the wrong dimension.

### 2. `-99` null sentinel

Two source files encode missing values as the literal integer `-99` instead of a blank cell:

- `puestos_priv.csv` → `puestos` column: **9,164 of 387,234 rows (2.37%)**.
- `w_mean_privado_mensual_por_clae2.csv` → `w_mean` column: **53 of 17,255 rows (0.31%)**.

Left as-is, `-99` would silently corrupt any `AVERAGE`/`SUM` in SQL or DAX (e.g. dragging down average wages or job counts). `transform_puestos_priv()` and `transform_salario_clae()` both replace `-99` with `pd.NA` before load, and the corresponding `CHECK` constraints in `sql/create_tables.sql` (`puestos >= 0`, `w_mean > 0`) treat the column as legitimately nullable rather than requiring a placeholder value.

### 3. Departments with near-total missing salary history

After reshaping the wide salary file (423 departments × monthly columns) into long format, two departments had almost no usable data:

| Department | % missing `sueldo_promedio` |
|---|---|
| Ramón Lista (Formosa) | 99.2% |
| Santa Victoria (Salta) | 98.3% |

Both are low-population departments where the source itself has almost no monthly readings, not a transformation bug. `transform_salarios()` drops any department above a 95% missing-value threshold — kept below that, an average computed from 1-2 non-null months across a decade would be misleading in a province/department ranking. This is a deliberate, threshold-based exclusion, documented here so the exact departments and criterion are traceable rather than an unexplained silent drop.

### 4. Province name → INDEC code mapping

`fact_puestos_priv` identifies provinces by free-text name (`zona_prov`), not by INDEC code. `transform_puestos_priv()` maps names to codes via an explicit dictionary and raises a descriptive `ValueError` (listing the exact unmapped names) if any row doesn't match, instead of silently dropping unmatched rows. Confirmed against the raw file: `zona_prov` contains exactly 24 distinct values, matching Argentina's 24 provinces (23 + CABA) and the 24 keys in the mapping dictionary — the validation currently never fires, which is itself the expected, checked-for outcome.

### 5. IPC type coercion

`ipc_ng_nacional` and `indice_tiempo` are read as generic columns by `pandas.read_csv` and coerced explicitly (`pd.to_numeric` / `pd.to_datetime`, both with `errors="coerce"`) rather than trusted as already-typed. Re-checking the raw file: all 115 rows parse cleanly (0 rows dropped by this step in the current source snapshot) — the coercion is a defensive safeguard against a future release of the same dataset introducing a malformed row, not a fix for a problem found in the current data.

## Validations applied

`sql/validations.sql` is run manually against the loaded warehouse after each `python scripts/main.py` run. It checks, with the expected result noted for each:

- **Duplicate keys in `fact_salarios`** on `(fecha, codigo_departamento_indec)` — expected: 0 rows returned.
- **Orphaned foreign keys** — `fact_puestos_priv` rows with no matching `dim_provincia` or `dim_clae`, `fact_salario_clae` rows with no matching `dim_clae` — expected: 0 for all three.
- **Null checks on `fact_ipc`** (`fecha`, `ipc_nacional`) — expected: 0 rows.
- **Distinct province count** in `fact_puestos_priv` — expected: 24 (confirmed above from the raw file, independent of the loaded DB).
- **Non-positive value checks** — `sueldo_promedio <= 0`, `ipc_nacional <= 0`, `w_mean <= 0` — expected: 0 for all (backed by the `CHECK` constraints in `sql/create_tables.sql`, which make these structurally impossible to load, not just observed-to-be-zero).
- **Invalid `mes`/`trimestre` ranges** in `dim_fecha` — expected: 0 (also structurally enforced via `CHECK` constraints).
- **Row-count reconciliation** — per-table `COUNT(*)` compared against the row counts `scripts/main.py` prints after `load_tables()`, to catch a partial/mismatched load.
- **The one non-zero-by-design check**: `dim_clae` rows with no matching row in `fact_puestos_priv` — expected: exactly 1 (`clae2 = 84`, public administration, intentionally absent from the private-sector employment dataset; see Geographic Scope in `methodology.md`).

## Known limitations (not bugs)

These are constraints of the source data, not defects found during development — documented here for completeness, with the full reasoning in `methodology.md`:

- Real/inflation-adjusted metrics are only computable from December 2016 onward, since `fact_ipc` doesn't extend further back than that.
- Government wage/employment statistics cover **registered private-sector jobs only**; informal employment is out of scope for the source data itself.
- CLAE taxonomy revisions by INDEC over the 2007–2023 window are assumed consistent and not independently reconciled.
