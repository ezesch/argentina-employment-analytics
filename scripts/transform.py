import pandas as pd


# ============================================================
# SALARIOS POR DEPARTAMENTO
# ============================================================

def transform_salarios(df):

    columnas_id = [
        "provincia",
        "id_provincia_indec",
        "departamento",
        "codigo_departamento_indec"
    ]

    df_long = df.melt(
        id_vars=columnas_id,
        var_name="periodo",
        value_name="sueldo_promedio"
    )

    df_long["fecha"] = pd.to_datetime(
        df_long["periodo"].str[1:],
        format="%Y%m"
    )

    df_long.drop(
        columns=["periodo"],
        inplace=True
    )

    # Eliminar departamentos con más de 95% de valores nulos
    nulos_departamento = (
        df_long
        .groupby("departamento")["sueldo_promedio"]
        .apply(lambda x: x.isna().mean() * 100)
    )

    departamentos_eliminar = nulos_departamento[
        nulos_departamento > 95
    ].index

    df_long = df_long[
        ~df_long["departamento"].isin(
            departamentos_eliminar
        )
    ]

    # Eliminar registros sin salario
    df_long = df_long.dropna(
        subset=["sueldo_promedio"]
    )

    dim_provincia = (
        df_long[
            [
                "id_provincia_indec",
                "provincia"
            ]
        ]
        .drop_duplicates()
        .sort_values("id_provincia_indec")
        .reset_index(drop=True)
    )

    dim_departamento = (
        df_long[
            [
                "codigo_departamento_indec",
                "departamento",
                "id_provincia_indec"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "codigo_departamento_indec"
        )
        .reset_index(drop=True)
    )

    fact_salarios = df_long[
        [
            "fecha",
            "codigo_departamento_indec",
            "sueldo_promedio"
        ]
    ].copy()

    fechas_salarios = df_long["fecha"].unique()

    return (
        dim_provincia,
        dim_departamento,
        fact_salarios,
        fechas_salarios
    )


# ============================================================
# IPC
# ============================================================

def transform_ipc(df):

    fact_ipc = df[
        [
            "indice_tiempo",
            "ipc_ng_nacional",
            "ipc_ng_nacional_tasa_variacion_mensual"
        ]
    ].copy()

    fact_ipc = fact_ipc.rename(
        columns={
            "indice_tiempo": "fecha",
            "ipc_ng_nacional": "ipc_nacional",
            "ipc_ng_nacional_tasa_variacion_mensual":
                "variacion_mensual"
        }
    )

    fact_ipc["fecha"] = pd.to_datetime(
        fact_ipc["fecha"],
        errors="coerce"
    )

    fact_ipc["ipc_nacional"] = pd.to_numeric(
        fact_ipc["ipc_nacional"],
        errors="coerce"
    )

    fact_ipc["variacion_mensual"] = pd.to_numeric(
        fact_ipc["variacion_mensual"],
        errors="coerce"
    )

    fact_ipc = fact_ipc.dropna(
        subset=["fecha", "ipc_nacional"]
    )
    

    return fact_ipc[
        [
            "fecha",
            "ipc_nacional",
            "variacion_mensual"
        ]
    ]


# ============================================================
# DICCIONARIO CLAE
# ============================================================

def transform_clae(df):

    dim_clae = df[
        [
            "clae2",
            "clae2_desc",
            "letra",
            "letra_desc"
        ]
    ].copy()

    dim_clae["clae2"] = pd.to_numeric(
        dim_clae["clae2"],
        errors="coerce"
    )

    dim_clae = dim_clae.dropna(
        subset=["clae2"]
    )

    dim_clae["clae2"] = (
        dim_clae["clae2"]
        .astype(int)
    )

    dim_clae = (
        dim_clae
        .drop_duplicates(subset=["clae2"])
        .sort_values("clae2")
        .reset_index(drop=True)
    )

    return dim_clae


# ============================================================
# PUESTOS DE TRABAJO PRIVADOS
# ============================================================

def transform_puestos_priv(df):

    fact_puestos_priv = df.copy()

    fact_puestos_priv["fecha"] = pd.to_datetime(
        fact_puestos_priv["fecha"],
        errors="coerce"
    )

    fact_puestos_priv["clae2"] = pd.to_numeric(
        fact_puestos_priv["clae2"],
        errors="coerce"
    )

    fact_puestos_priv["puestos"] = (
        fact_puestos_priv["puestos"]
        .replace(-99, pd.NA) # Con estos eliminamos los null values del dataset original
    )   

    mapa_provincias = {
        "BUENOS AIRES": 6,
        "CAPITAL FEDERAL": 2,
        "CATAMARCA": 10,
        "CHACO": 22,
        "CHUBUT": 26,
        "CORDOBA": 14,
        "CORRIENTES": 18,
        "ENTRE RIOS": 30,
        "FORMOSA": 34,
        "JUJUY": 38,
        "LA PAMPA": 42,
        "LA RIOJA": 46,
        "MENDOZA": 50,
        "MISIONES": 54,
        "NEUQUEN": 58,
        "RIO NEGRO": 62,
        "SALTA": 66,
        "SAN JUAN": 70,
        "SAN LUIS": 74,
        "SANTA CRUZ": 78,
        "SANTA FE": 82,
        "SANTIAGO DEL ESTERO": 86,
        "TIERRA DEL FUEGO": 94,
        "TUCUMAN": 90
    }

    fact_puestos_priv["id_provincia_indec"] = (
        fact_puestos_priv["zona_prov"]
        .map(mapa_provincias)
    )

    # Detectar provincias sin correspondencia
    if fact_puestos_priv[
        "id_provincia_indec"
    ].isna().any():

        provincias_sin_mapeo = (
            fact_puestos_priv.loc[
                fact_puestos_priv[
                    "id_provincia_indec"
                ].isna(),
                "zona_prov"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Hay provincias sin mapeo: "
            f"{provincias_sin_mapeo}"
        )

    fact_puestos_priv = fact_puestos_priv.dropna(
        subset=[
            "fecha",
            "id_provincia_indec",
            "clae2"
        ]
    )

    fact_puestos_priv["id_provincia_indec"] = (
        fact_puestos_priv[
            "id_provincia_indec"
        ].astype(int)
    )

    fact_puestos_priv["clae2"] = (
        fact_puestos_priv["clae2"]
        .astype(int)
    )

    return fact_puestos_priv[
        [
            "fecha",
            "id_provincia_indec",
            "clae2",
            "puestos"
        ]
    ]


# ============================================================
# SALARIO PROMEDIO POR CLAE2
# ============================================================

def transform_salario_clae(df):

    fact_salario_clae = df.copy()

    fact_salario_clae["fecha"] = pd.to_datetime(
        fact_salario_clae["fecha"],
        errors="coerce"
    )

    fact_salario_clae["clae2"] = pd.to_numeric(
        fact_salario_clae["clae2"],
        errors="coerce"
    )

    fact_salario_clae["w_mean"] = pd.to_numeric(
        fact_salario_clae["w_mean"],
        errors="coerce"
    )

     # -99 represents missing values in the source dataset
    fact_salario_clae["w_mean"] = (
        fact_salario_clae["w_mean"]
        .replace(-99, pd.NA)
    )

    fact_salario_clae = fact_salario_clae.dropna(
        subset=[
            "fecha",
            "clae2"
        ]
    )

    fact_salario_clae["clae2"] = (
        fact_salario_clae["clae2"]
        .astype(int)
    )

    return fact_salario_clae[
        [
            "fecha",
            "clae2",
            "w_mean"
        ]
    ]


# ============================================================
# TRANSFORMACIÓN GENERAL
# ============================================================

def transform(
    df_salarios,
    df_ipc,
    df_clae,
    df_puestos,
    df_salario_clae
):

    # Salarios
    (
        dim_provincia,
        dim_departamento,
        fact_salarios,
        fechas_salarios
    ) = transform_salarios(df_salarios)

    # IPC
    fact_ipc = transform_ipc(df_ipc)

    # CLAE
    dim_clae = transform_clae(df_clae)

    # Puestos privados
    fact_puestos_priv = transform_puestos_priv(
        df_puestos
    )

    # Salarios por CLAE2
    fact_salario_clae = transform_salario_clae(
        df_salario_clae
    )

    # ========================================================
    # DIM_FECHA
    # ========================================================

    fechas = pd.concat(
        [
            pd.Series(fechas_salarios),
            fact_ipc["fecha"],
            fact_puestos_priv["fecha"],
            fact_salario_clae["fecha"]
        ],
        ignore_index=True
    )

    fechas = (
        pd.to_datetime(
            fechas,
            errors="coerce"
        )
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    dim_fecha = pd.DataFrame({
        "fecha": fechas
    })

    dim_fecha["año"] = (
        dim_fecha["fecha"].dt.year
    )

    dim_fecha["mes"] = (
        dim_fecha["fecha"].dt.month
    )

    dim_fecha["trimestre"] = (
        dim_fecha["fecha"].dt.quarter
    )

    dim_fecha["año_mes"] = (
        dim_fecha["fecha"].dt.strftime("%Y-%m")
    )

    return (
        dim_provincia,
        dim_departamento,
        dim_fecha,
        fact_salarios,
        fact_ipc,
        dim_clae,
        fact_puestos_priv,
        fact_salario_clae
    )