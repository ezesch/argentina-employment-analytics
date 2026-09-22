from extract import extract
from transform import transform
from load import load_tables
from database import get_engine


def main():

    print("Iniciando proceso ETL...")

    # =========================================================
    # EXTRACT
    # =========================================================

    print("\nExtrayendo datos...")

    (
        df_salarios,
        df_ipc,
        df_clae,
        df_puestos,
        df_salario_clae
    ) = extract()

    print("Datos extraídos correctamente.")

    # =========================================================
    # TRANSFORM
    # =========================================================

    print("\nTransformando datos...")

    (
        dim_provincia,
        dim_departamento,
        dim_fecha,
        fact_salarios,
        fact_ipc,
        dim_clae,
        fact_puestos_priv,
        fact_salario_clae
    ) = transform(
        df_salarios,
        df_ipc,
        df_clae,
        df_puestos,
        df_salario_clae
    )

    print("Datos transformados correctamente.")

    # =========================================================
    # LOAD
    # =========================================================

    print("\nCargando datos en PostgreSQL...")

    engine = get_engine()

    resultados = load_tables(
        engine,
        dim_provincia,
        dim_departamento,
        dim_fecha,
        fact_salarios,
        fact_ipc,
        dim_clae,
        fact_puestos_priv,
        fact_salario_clae
    )

    # =========================================================
    # RESULTADOS
    # =========================================================

    print("\nProceso finalizado correctamente.\n")

    for tabla, cantidad in resultados.items():
        print(f"{tabla}: {cantidad:,} registros")


if __name__ == "__main__":
    main()

    