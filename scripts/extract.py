import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")



def read_dataset(data_folder, env_var, reader, **kwargs):
    """
    Lee un archivo fuente definido mediante una variable
    de entorno y valida que exista antes de leerlo.
    """
    filename = os.getenv(env_var)

    if not filename:
        raise ValueError(
            f"No se encontró la variable de entorno: {env_var}"
        )

    path = data_folder / filename

    print(f"Leyendo {env_var}: {path}")

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {path}"
        )

    return reader(path, **kwargs)

# ============================================================
# EXTRACT
# ============================================================

def extract():

    data_folder = BASE_DIR / os.getenv("DATA_FOLDER")

    df_salarios = read_dataset(
        data_folder,
        "DATA_FILE",
        pd.read_excel,
        sheet_name="Total sector privado"
    )

    df_ipc = read_dataset(
        data_folder,
        "IPC_FILE",
        pd.read_csv
    )

    df_clae = read_dataset(
        data_folder,
        "CLAE_FILE",
        pd.read_csv
    )

    df_puestos = read_dataset(
        data_folder,
        "PUESTOS_FILE",
        pd.read_csv
    )

    df_salario_clae = read_dataset(
        data_folder,
        "SALARIO_CLAE_FILE",
        pd.read_csv
    )

    print("\nArchivos extraídos correctamente.")

    return (
        df_salarios,
        df_ipc,
        df_clae,
        df_puestos,
        df_salario_clae
    )