-- CREAR TODAS LAS TABLAS




-- DIM PROVINCIA


CREATE TABLE dim_provincia (
    id_provincia_indec INTEGER PRIMARY KEY,
    provincia VARCHAR(100) NOT NULL
);



-- DIM DEPARTAMENTO


CREATE TABLE dim_departamento (
    codigo_departamento_indec INTEGER PRIMARY KEY,
    departamento VARCHAR(150) NOT NULL,
    id_provincia_indec INTEGER NOT NULL,

    CONSTRAINT fk_departamento_provincia
        FOREIGN KEY (id_provincia_indec)
        REFERENCES dim_provincia(id_provincia_indec)
);



-- DIM FECHA


CREATE TABLE dim_fecha (
    fecha DATE PRIMARY KEY,
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    trimestre INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    año_mes VARCHAR(7) NOT NULL
);

-- FACT SALARIOS


CREATE TABLE fact_salarios (
    fecha DATE NOT NULL,
    codigo_departamento_indec INTEGER NOT NULL,
    sueldo_promedio NUMERIC(12,2) NOT NULL CHECK (sueldo_promedio > 0),

    PRIMARY KEY (
        fecha,
        codigo_departamento_indec
    ),

    CONSTRAINT fk_salarios_fecha
        FOREIGN KEY (fecha)
        REFERENCES dim_fecha(fecha),

    CONSTRAINT fk_salarios_departamento
        FOREIGN KEY (codigo_departamento_indec)
        REFERENCES dim_departamento(
            codigo_departamento_indec
        )
);


-- FACT IPC


CREATE TABLE fact_ipc (
    fecha DATE PRIMARY KEY,
    ipc_nacional NUMERIC(10,4) NOT NULL CHECK (ipc_nacional > 0),
    variacion_mensual NUMERIC(10,6),

    CONSTRAINT fk_ipc_fecha
        FOREIGN KEY (fecha)
        REFERENCES dim_fecha(fecha)
);

-- DIM CLAE


CREATE TABLE dim_clae (
    clae2 INTEGER PRIMARY KEY,
    clae2_desc VARCHAR(255),
    letra VARCHAR(5),
    letra_desc VARCHAR(255)
);


-- FACT PUESTOS PRIVADOS


CREATE TABLE fact_puestos_priv (
    fecha DATE NOT NULL,
    id_provincia_indec INTEGER NOT NULL,
    clae2 INTEGER NOT NULL,
    puestos INTEGER CHECK (puestos >= 0),

    PRIMARY KEY (
        fecha,
        id_provincia_indec,
        clae2
    ),

    CONSTRAINT fk_puestos_fecha
        FOREIGN KEY (fecha)
        REFERENCES dim_fecha(fecha),

    CONSTRAINT fk_puestos_provincia
        FOREIGN KEY (id_provincia_indec)
        REFERENCES dim_provincia(id_provincia_indec),

    CONSTRAINT fk_puestos_clae
        FOREIGN KEY (clae2)
        REFERENCES dim_clae(clae2)
);


-- ============================================================
-- FACT SALARIO CLAE
-- ============================================================

CREATE TABLE fact_salario_clae (
    fecha DATE NOT NULL,
    clae2 INTEGER NOT NULL,
    w_mean NUMERIC(12,2) CHECK (w_mean > 0),

    PRIMARY KEY (
        fecha,
        clae2
    ),

    CONSTRAINT fk_salario_clae_fecha
        FOREIGN KEY (fecha)
        REFERENCES dim_fecha(fecha),

    CONSTRAINT fk_salario_clae_clae
        FOREIGN KEY (clae2)
        REFERENCES dim_clae(clae2)
);

