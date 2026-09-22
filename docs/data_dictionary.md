# Data Dictionary

## Database schema

### `dim_provincia`
| Column | Type | Description | Key |
|---|---|---|---|
| `id_provincia_indec` | INTEGER | INDEC province code | PK |
| `provincia` | VARCHAR(100) | Province name | |

### `dim_departamento`
| Column | Type | Description | Key |
|---|---|---|---|
| `codigo_departamento_indec` | INTEGER | INDEC department code | PK |
| `departamento` | VARCHAR(150) | Department name | |
| `id_provincia_indec` | INTEGER | Parent province | FK → dim_provincia |

### `dim_fecha`
| Column | Type | Description | Key |
|---|---|---|---|
| `fecha` | DATE | First-of-month date | PK |
| `año` | INTEGER | Year | |
| `mes` | INTEGER | Month | CHECK (1–12) |
| `trimestre` | INTEGER | Quarter | CHECK (1–4) |
| `año_mes` | VARCHAR(7) | "YYYY-MM" label | |

Built from the union of every date present across all 4 fact tables — its range is wider than any single fact table's own range (see [Data Limitations](#coverage-by-table) below).

### `dim_clae`
| Column | Type | Description | Key |
|---|---|---|---|
| `clae2` | INTEGER | 2-digit economic activity code | PK |
| `clae2_desc` | VARCHAR(255) | Activity description | |
| `letra` | VARCHAR(5) | Top-level activity section code | |
| `letra_desc` | VARCHAR(255) | Section description | |

**Note:** an earlier version of this table also included `clae3`/`clae3_desc`. Since a single `clae2` code maps to multiple distinct `clae3` sub-activities (62 of the table's 86 rows), those columns were not a valid property of this table's grain and were removed during the project's technical audit — see `data_quality.md`.

### `fact_salarios`
Grain: one row per department per month.
| Column | Type | Description | Key |
|---|---|---|---|
| `fecha` | DATE | Month | PK (composite), FK → dim_fecha |
| `codigo_departamento_indec` | INTEGER | Department | PK (composite), FK → dim_departamento |
| `sueldo_promedio` | NUMERIC(12,2) | Average private-sector nominal salary (ARS) | CHECK (> 0) |

### `fact_ipc`
Grain: one row per month, national level.
| Column | Type | Description | Key |
|---|---|---|---|
| `fecha` | DATE | Month | PK, FK → dim_fecha |
| `ipc_nacional` | NUMERIC(10,4) | National CPI index (base Dec-2016 = 100) | NOT NULL, CHECK (> 0) |
| `variacion_mensual` | NUMERIC(10,6) | Month-over-month CPI variation | nullable (blank for the series' first month) |

### `fact_puestos_priv`
Grain: one row per month × province × activity.
| Column | Type | Description | Key |
|---|---|---|---|
| `fecha` | DATE | Month | PK (composite), FK → dim_fecha |
| `id_provincia_indec` | INTEGER | Province | PK (composite), FK → dim_provincia |
| `clae2` | INTEGER | Activity | PK (composite), FK → dim_clae |
| `puestos` | INTEGER | Registered private-sector jobs | nullable (source `-99` sentinel mapped to NULL), CHECK (≥ 0 when not null) |

### `fact_salario_clae`
Grain: one row per month × activity, national level.
| Column | Type | Description | Key |
|---|---|---|---|
| `fecha` | DATE | Month | PK (composite), FK → dim_fecha |
| `clae2` | INTEGER | Activity | PK (composite), FK → dim_clae |
| `w_mean` | NUMERIC(12,2) | Average nominal wage for that activity | CHECK (> 0 when not null) |

### Coverage by table

| Table | Date range |
|---|---|
| `fact_puestos_priv`, `fact_salario_clae` | 2007-01 to 2023-11 |
| `fact_salarios` | 2014-01 to 2023-11 |
| `fact_ipc` | 2016-12 to present |

Any measure comparing salary/employment against inflation is only meaningful from December 2016 onward — see `methodology.md` and `data_quality.md` for the full explanation and its downstream implications.

---

## Power BI measures (`_Medidas` table)

The measures below are grouped by what they answer. Each entry notes what it depends on, to make clear which are base calculations and which are built on top of another measure — the project deliberately avoids duplicating salary/IPC logic across multiple measures.

### Core building blocks
| Measure | Formula basis | Notes |
|---|---|---|
| `Salario Promedio` | `AVERAGE(fact_salarios[sueldo_promedio])` | Base measure — responds to whatever province/date filter is active. |
| `Salario Promedio Nacional` | `Salario Promedio` with `ALL(dim_provincia)` | National average regardless of province, still respects date context. |
| `Salario Promedio Actividad` | `AVERAGE(fact_salario_clae[w_mean])` | Base measure for activity-level wages. |
| `Índice IPC` | `MAX(fact_ipc[ipc_nacional])` | |

### "Current snapshot" measures
These exist because a KPI card with no date filter needs an explicit anchor — `dim_fecha`'s own maximum date is driven by the CPI series (which extends further into the future than salary/employment data), so anchoring to it directly would silently pick up a date with no corresponding salary.
| Measure | Anchored to |
|---|---|
| `Salario Nacional Actual` | `MAX(fact_salarios[fecha])` |
| `Salario Último Período` | `MAX(dim_fecha[fecha])` — used only inside visuals that already have a date filter active |

### Variation measures
`Variación Mensual %`, `Variación Interanual %`, `Inflación Interanual %` — all use `DATEADD` against `dim_fecha` and `DIVIDE()` (never raw `/`) to avoid division-by-zero errors.

### Real wage / purchasing power measures
| Measure | Base period | Depends on |
|---|---|---|
| `Poder Adquisitivo Acumulado %` | Dec-2016 | `Salario Promedio Nacional`, `Índice IPC` |
| `Poder Adquisitivo Provincia %` | Dec-2016 | `Salario Promedio`, `Índice IPC` |

Both compute `(crecimiento del salario / crecimiento del IPC) − 1` — a ratio of growth rates, not a subtraction of percentages — anchored explicitly to each fact table's own latest available date rather than to `dim_fecha`'s. See `methodology.md` for the formula and `data_quality.md` for why this distinction mattered in practice.

### Ranking and "best/worst" measures
| Measure | Returns |
|---|---|
| `Ranking Provincia` | Position, respects active date/filter context |
| `Provincia Mejor Pagada` / `Provincia Peor Pagada` | Province name at the latest available salary month |
| `Actividad Mejor Pagada` | Activity name at the latest available wage month |

These use `ADDCOLUMNS` + `TOPN` + `MAXX` over a virtual table to resolve a name rather than a rank position — see `architecture.md` for why this pattern was chosen over `RANKX` for this specific question.