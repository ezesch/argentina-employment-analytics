from sqlalchemy import text


def load_tables(
    engine,
    dim_provincia,
    dim_departamento,
    dim_fecha,
    fact_salarios,
    fact_ipc,
    dim_clae,
    fact_puestos_priv,
    fact_salario_clae
):

    with engine.begin() as conn:

        # =====================================================
        # LIMPIAR TABLAS
        # =====================================================

        print("Limpiando tablas anteriores...")

        conn.execute(text("""
            TRUNCATE TABLE
                fact_salario_clae,
                fact_puestos_priv,
                fact_ipc,
                fact_salarios,
                dim_clae,
                dim_fecha,
                dim_departamento,
                dim_provincia
            RESTART IDENTITY CASCADE;
        """))

        # =====================================================
        # DIMENSIONES
        # =====================================================

        print("Cargando dim_provincia...")

        dim_provincia.to_sql(
            "dim_provincia",
            conn,
            if_exists="append",
            index=False
        )

        print("Cargando dim_departamento...")

        dim_departamento.to_sql(
            "dim_departamento",
            conn,
            if_exists="append",
            index=False
        )

        print("Cargando dim_clae...")

        dim_clae.to_sql(
            "dim_clae",
            conn,
            if_exists="append",
            index=False
        )

        print("Cargando dim_fecha...")

        dim_fecha.to_sql(
            "dim_fecha",
            conn,
            if_exists="append",
            index=False
        )

        # =====================================================
        # FACT SALARIOS
        # =====================================================

        print("Cargando fact_salarios...")

        fact_salarios.to_sql(
            "fact_salarios",
            conn,
            if_exists="append",
            index=False,
            chunksize=5000
        )

        # =====================================================
        # FACT IPC
        # =====================================================

        print("Cargando fact_ipc...")

        fact_ipc.to_sql(
            "fact_ipc",
            conn,
            if_exists="append",
            index=False
        )

        # =====================================================
        # FACT PUESTOS PRIVADOS
        # =====================================================

        print("Cargando fact_puestos_priv...")

        fact_puestos_priv.to_sql(
            "fact_puestos_priv",
            conn,
            if_exists="append",
            index=False,
            chunksize=5000
        )

        # =====================================================
        # FACT SALARIO CLAE
        # =====================================================

        print("Cargando fact_salario_clae...")

        fact_salario_clae.to_sql(
            "fact_salario_clae",
            conn,
            if_exists="append",
            index=False,
            chunksize=5000
        )

    return {
        "dim_provincia": len(dim_provincia),
        "dim_departamento": len(dim_departamento),
        "dim_fecha": len(dim_fecha),
        "dim_clae": len(dim_clae),
        "fact_salarios": len(fact_salarios),
        "fact_ipc": len(fact_ipc),
        "fact_puestos_priv": len(fact_puestos_priv),
        "fact_salario_clae": len(fact_salario_clae)
    }

