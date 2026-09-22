-- Validar duplicados en fact_salarios

SELECT 
    fecha,
    codigo_departamento_indec,
    COUNT(*)
FROM fact_salarios
GROUP BY 
    fecha,
    codigo_departamento_indec
HAVING COUNT(*) > 1;

-- Validar relaciones entre tablas

SELECT
    p.provincia,
    d.departamento,
    f.fecha,
    f.sueldo_promedio
FROM fact_salarios f
JOIN dim_departamento d
    ON f.codigo_departamento_indec = d.codigo_departamento_indec
JOIN dim_provincia p
    ON d.id_provincia_indec = p.id_provincia_indec
LIMIT 10;

-- IPC

-- Chequear que se importaron los datos con las fechas correctas
SELECT
    MIN(fecha),
    MAX(fecha),
    COUNT(*)
FROM fact_ipc;

-- Chequear si los datos estan correctos
SELECT *
FROM fact_ipc
ORDER BY fecha
LIMIT 5;

-- Verificar Nulls
SELECT *
FROM fact_ipc
WHERE fecha IS NULL
   OR ipc_nacional IS NULL;


-- Puestos sin provincia válida (resultado esperado: 0)
SELECT COUNT(*)
FROM fact_puestos_priv p
LEFT JOIN dim_provincia d
    ON p.id_provincia_indec = d.id_provincia_indec
WHERE d.id_provincia_indec IS NULL;

-- Puestos sin CLAE válido (resultado esperado: 0)
SELECT COUNT(*)
FROM fact_puestos_priv p
LEFT JOIN dim_clae c
    ON p.clae2 = c.clae2
WHERE c.clae2 IS NULL;

-- Salarios CLAE sin CLAE válido (resultado esperado: 0)
SELECT COUNT(*)
FROM fact_salario_clae s
LEFT JOIN dim_clae c
    ON s.clae2 = c.clae2
WHERE c.clae2 IS NULL;

-- Validar rango temporal
SELECT
    MIN(fecha) AS fecha_minima,
    MAX(fecha) AS fecha_maxima
FROM fact_puestos_priv;

SELECT
    MIN(fecha) AS fecha_minima,
    MAX(fecha) AS fecha_maxima
FROM fact_salario_clae;

-- Validar provincias (resultado esperado: 24)

SELECT
    COUNT(DISTINCT id_provincia_indec) AS provincias
FROM fact_puestos_priv;

-- Validar actividades:
SELECT
    COUNT(DISTINCT clae2) AS actividades
FROM fact_puestos_priv;

-- Validacion de cual es la actividad extra:

SELECT
    c.clae2,
    c.clae2_desc
FROM dim_clae c
LEFT JOIN (
    SELECT DISTINCT clae2
    FROM fact_puestos_priv
) p
    ON c.clae2 = p.clae2
WHERE p.clae2 IS NULL
ORDER BY c.clae2; -- No se encuentra en la tabla de puestos_priv porque no es una actividad privada

-- Deteccion de Nulls en puestos_priv
SELECT
    COUNT(*) AS total_registros,
    COUNT(*) FILTER (WHERE puestos IS NULL) AS registros_null,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE puestos IS NULL) / COUNT(*),
        2
    ) AS porcentaje_null
FROM fact_puestos_priv;

-- Ubicar los Nulls en actividades
SELECT
    c.clae2,
    c.clae2_desc,
    COUNT(*) AS registros_menos_99
FROM fact_puestos_priv p
JOIN dim_clae c
    ON p.clae2 = c.clae2
WHERE p.puestos IS NULL
GROUP BY c.clae2, c.clae2_desc
ORDER BY registros_menos_99 DESC;

-- Ubicar los NUlls en provincias:
SELECT
    d.provincia,
    COUNT(*) AS registros_menos_99
FROM fact_puestos_priv p
JOIN dim_provincia d
    ON p.id_provincia_indec = d.id_provincia_indec
WHERE p.puestos IS NULL
GROUP BY d.provincia
ORDER BY registros_menos_99 DESC;

-- Salarios no positivos (esperado: 0)
SELECT COUNT(*) AS invalid_salaries
FROM fact_salarios
WHERE sueldo_promedio <= 0;

-- IPC no positivo (esperado: 0)
SELECT COUNT(*) AS invalid_ipc
FROM fact_ipc
WHERE ipc_nacional <= 0;

-- Fechas inválidas (esperado: 0)
SELECT COUNT(*) AS invalid_dates
FROM dim_fecha
WHERE mes NOT BETWEEN 1 AND 12
   OR trimestre NOT BETWEEN 1 AND 4;

-- Salarios CLAE no positivos (esperado: 0)
SELECT COUNT(*) AS invalid_salary_clae
FROM fact_salario_clae
WHERE w_mean <= 0;

-- Comparar COUNTS con Python

SELECT 'dim_provincia' AS tabla, COUNT(*) AS registros FROM dim_provincia
UNION ALL
SELECT 'dim_departamento', COUNT(*) FROM dim_departamento
UNION ALL
SELECT 'dim_fecha', COUNT(*) FROM dim_fecha
UNION ALL
SELECT 'dim_clae', COUNT(*) FROM dim_clae
UNION ALL
SELECT 'fact_salarios', COUNT(*) FROM fact_salarios
UNION ALL
SELECT 'fact_ipc', COUNT(*) FROM fact_ipc
UNION ALL
SELECT 'fact_puestos_priv', COUNT(*) FROM fact_puestos_priv
UNION ALL
SELECT 'fact_salario_clae', COUNT(*) FROM fact_salario_clae;

-- Confirmar estructura dim_clae

SELECT column_name
FROM information_schema.columns
WHERE table_name = 'dim_clae'
ORDER BY ordinal_position;