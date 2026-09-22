-- ============================================================
-- ANALYTICAL QUERIES
-- ============================================================
-- Business-question queries against the warehouse schema (see
-- docs/data_dictionary.md). These complement sql/validations.sql,
-- which is QA-only (duplicate/orphan/range checks) — the queries
-- below answer real analytical questions directly in SQL, the same
-- ones the Power BI measures answer in DAX.


-- ----------------------------------------------------------------
-- 1. Which provinces pay the most (and least), for the latest
--    month with data? Ranked with RANK() so ties share a position.
-- ----------------------------------------------------------------

WITH salario_provincia AS (
    SELECT
        p.provincia,
        f.fecha,
        AVG(f.sueldo_promedio) AS sueldo_promedio_provincia
    FROM fact_salarios f
    JOIN dim_departamento d
        ON f.codigo_departamento_indec = d.codigo_departamento_indec
    JOIN dim_provincia p
        ON d.id_provincia_indec = p.id_provincia_indec
    WHERE f.fecha = (SELECT MAX(fecha) FROM fact_salarios)
    GROUP BY p.provincia, f.fecha
)
SELECT
    provincia,
    fecha,
    ROUND(sueldo_promedio_provincia, 2) AS sueldo_promedio,
    RANK() OVER (ORDER BY sueldo_promedio_provincia DESC) AS ranking_salario
FROM salario_provincia
ORDER BY ranking_salario;


-- ----------------------------------------------------------------
-- 2. How much did the national average salary change year-over-year,
--    month by month? LAG() 12 rows back over the national monthly
--    average.
-- ----------------------------------------------------------------

WITH salario_nacional_mensual AS (
    SELECT
        fecha,
        AVG(sueldo_promedio) AS sueldo_promedio_nacional
    FROM fact_salarios
    GROUP BY fecha
)
SELECT
    fecha,
    ROUND(sueldo_promedio_nacional, 2) AS sueldo_promedio_nacional,
    ROUND(
        LAG(sueldo_promedio_nacional, 12) OVER (ORDER BY fecha),
        2
    ) AS sueldo_hace_12_meses,
    ROUND(
        100.0 * (
            sueldo_promedio_nacional
            - LAG(sueldo_promedio_nacional, 12) OVER (ORDER BY fecha)
        ) / NULLIF(
            LAG(sueldo_promedio_nacional, 12) OVER (ORDER BY fecha),
            0
        ),
        2
    ) AS variacion_interanual_pct
FROM salario_nacional_mensual
ORDER BY fecha;


-- ----------------------------------------------------------------
-- 3. Which economic activities pay the most, in the latest
--    available month? CTE joins fact_salario_clae with dim_clae,
--    ranks activities, keeps the top 10.
-- ----------------------------------------------------------------

WITH salario_actividad_actual AS (
    SELECT
        c.clae2,
        c.clae2_desc,
        c.letra_desc,
        s.w_mean
    FROM fact_salario_clae s
    JOIN dim_clae c
        ON s.clae2 = c.clae2
    WHERE s.fecha = (SELECT MAX(fecha) FROM fact_salario_clae)
      AND s.w_mean IS NOT NULL
)
SELECT
    clae2,
    clae2_desc,
    letra_desc AS sector,
    w_mean AS salario_promedio,
    RANK() OVER (ORDER BY w_mean DESC) AS ranking_actividad
FROM salario_actividad_actual
ORDER BY ranking_actividad
LIMIT 10;


-- ----------------------------------------------------------------
-- 4. What's the national average salary in real (inflation-adjusted)
--    terms, month by month? Joins the national monthly average with
--    fact_ipc and applies the formula from docs/methodology.md:
--    Real Salary(t) = Nominal Salary(t) / CPI(t) * 100 (base Dec-2016 = 100).
-- ----------------------------------------------------------------

WITH salario_nacional_mensual AS (
    SELECT
        fecha,
        AVG(sueldo_promedio) AS sueldo_promedio_nacional
    FROM fact_salarios
    GROUP BY fecha
)
SELECT
    s.fecha,
    ROUND(s.sueldo_promedio_nacional, 2) AS salario_nominal,
    i.ipc_nacional,
    ROUND(
        s.sueldo_promedio_nacional / i.ipc_nacional * 100,
        2
    ) AS salario_real_base_dic2016
FROM salario_nacional_mensual s
JOIN fact_ipc i
    ON s.fecha = i.fecha
ORDER BY s.fecha;
