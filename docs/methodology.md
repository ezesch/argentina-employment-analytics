# Methodology

## Nominal vs. Real Salary

This project distinguishes between **nominal salary** (raw peso values from the
source data) and **real salary / purchasing power** (nominal salary adjusted for
inflation), since comparing nominal figures across time in a high-inflation
economy is misleading on its own.

Real salary is calculated as:

    Real Salary(t) = Nominal Salary(t) / CPI(t) * 100

where CPI is Argentina's national Consumer Price Index (INDEC), base December
2016 = 100.

## Data Availability Window

- Employment (`fact_puestos_priv`) and activity-level wages
  (`fact_salario_clae`): 2007-01 to 2023-11.
- Department-level salaries (`fact_salarios`): 2014-01 to 2023-11.
- CPI (`fact_ipc`): 2016-12 to present.

**As a result, all purchasing-power / real-salary metrics are only computable
from December 2016 onward.** This is a limitation of the source CPI series
(tied to INDEC's 2016 methodology change), not a defect in this project's
pipeline. Nominal salary and employment figures are available for the full
2007–2023 range; only the inflation-adjusted comparison is restricted to the
shorter window.

## Regional Inflation

The source CPI dataset includes regional indices (GBA, Pampeana, NOA, NEA,
Cuyo, Patagonia) in addition to the national index. This project uses only
the **national CPI** to deflate salaries across all provinces. This is a
deliberate simplification: it prioritizes comparability of purchasing power
across provinces over per-region precision, since a regional deflator would
make cross-province rankings harder to interpret (each province's "real"
salary would be on a different base). Deflating with the matching regional
index instead of the national one is listed under Future Improvements in the
README.

## Economic Activity Classification (CLAE)

Activities are classified using INDEC's CLAE (Clasificador de Actividades
Económicas) at the `clae2` (2-digit) level. This project assumes classification
consistency across the 2007–2023 period; INDEC revisions to the CLAE taxonomy
over time are not independently reconciled.

## Geographic Scope

`fact_puestos_priv` covers private-sector employment only (public
administration, `clae2 = 84`, is intentionally excluded — it is not part of
the private-sector employment dataset).