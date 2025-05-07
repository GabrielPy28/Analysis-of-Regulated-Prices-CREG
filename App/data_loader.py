import pandas as pd
import os

def load_data(downloads_folder):
    data_files = []
    for file_name in os.listdir(downloads_folder):
        if file_name.startswith("combustibles_") and file_name.endswith(".csv"):
            data_files.append(os.path.join(downloads_folder, file_name))
    
    df_list = [pd.read_csv(file) for file in data_files]
    df = pd.concat(df_list, ignore_index=True)
    # Unir "Bogotá D.C." y "Bogotá" en una sola entrada
    df['Ciudad'] = df['Ciudad'].replace({'Bogotá D.C.': 'Bogotá'})
    # Convertir la columna 'fecha' al formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y', errors='coerce')
    return df

def load_annual_data(resumen_file):
    return pd.read_csv(resumen_file)

def calcular_porcentaje(cambio_actual, cambio_anterior):
    if cambio_anterior == 0:
        return 0
    return ((cambio_actual - cambio_anterior) / cambio_anterior) * 100