import os
import logging
import pandas as pd
import psycopg2
from psycopg2 import sql
from config import get_db_config

# Crear el directorio de logs si no existe
os.makedirs('Logs', exist_ok=True)

# Configuración de logging
logging.basicConfig(
    filename='Logs/load_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Guardar los datos en archivos CSV
def save_to_csv(transformed_data, resumen_data, output_dir='../Download'):
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar los datos transformados (combustibles)
        for date_str, table in transformed_data.items():
            date_str = date_str.replace('-', '_')  # Para nombres de archivo seguros
            filename = f"{output_dir}/combustibles_{date_str}.csv"
            df = pd.DataFrame(table['data'], columns=table['headers'])
            df['fecha'] = table['date']  # Agregar la fecha como columna
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logging.info(f"Datos guardados en CSV: {filename}")

        # Guardar el resumen anual de los valores de combustibles
        resumen_filename = f"{output_dir}/resumen_combustibles_anuales.csv"
        resumen_df = pd.DataFrame(resumen_data)
        resumen_df.to_csv(resumen_filename, index=False, encoding='utf-8-sig')
        logging.info(f"Resumen anual guardado en CSV: {resumen_filename}")
    
    except Exception as e:
        logging.error(f"Error al guardar CSV: {e}")

# Guardar los datos en PostgreSQL (Tabla de precios combustibles)
def save_to_postgresql_combustibles(transformed_data, db_config, table_name='precios_combustibles'):
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        for date_str, table in transformed_data.items():
            df = pd.DataFrame(table['data'], columns=table['headers'])
            df['fecha'] = date_str  # Agregar la fecha como columna

            # Cambiar nombre de columnas para referenciarlos a los de la tabla
            df = df.rename(columns={"No.": "numero", "Ciudad": 'ciudad', 'Gasolina MC ($/gal)': 'gasolina_mc', 'ACPM ($/gal)': 'acpm'})

            for _, row in df.iterrows():
                values = list(row.values)
                columns = list(row.index)
                
                # Usar sql.Identifier para las columnas
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(values))
                )
                
                cur.execute(insert_query, values)
        
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Datos insertados en la tabla PostgreSQL: {table_name}")
    
    except Exception as e:
        logging.error(f"Error al insertar en PostgreSQL: {e}")


# Guardar los valores agregados por año en PostgreSQL (Tabla resumen de combustibles anuales)
def save_to_postgresql_resumen_anual(resumen_data, db_config, table_name='resumen_combustibles_anuales'):
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        for row in resumen_data:
            values = [
                row['year'],
                row['gasolina_max'], 
                row['gasolina_min'], 
                row['gasolina_avg'], 
                row['acpm_max'], 
                row['acpm_min'], 
                row['acpm_avg']
            ]
            
            insert_query = sql.SQL("""
                INSERT INTO {} (year, max_gasolina_mc, min_gasolina_mc, avg_gasolina_mc, 
                                max_acpm, min_acpm, avg_acpm)
                VALUES ({})""").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            cur.execute(insert_query, values)
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Datos insertados en la tabla PostgreSQL: {table_name}")
    except Exception as e:
        logging.error(f"Error al insertar en PostgreSQL: {e}")

# Ejemplo de uso si se ejecuta directamente este archivo
if __name__ == "__main__":
    # Ejemplo de datos transformados y de resumen
    transformed_data = [
        {
            'date': '22-03-2025',
            'headers': ['No.', 'Ciudad', 'Gasolina MC ($/gal)', 'ACPM ($/gal)'],
            'data': [[1, 'Bogotá', 16259, 10842], [2, 'Medellín', 16100, 10750]]
        }
    ]
    
    year_data = [
        {
            'year': 2025,
            'gasolina_max': 16259,
            'gasolina_min': 15000,
            'gasolina_avg': 15600,
            'acpm_max': 10842,
            'acpm_min': 10000,
            'acpm_avg': 10400
        }
    ]

    # Guardar en CSV
    save_to_csv(transformed_data, year_data)

    # Configuración de la base de datos
    #config = get_db_config()

    # Guardar en PostgreSQL (Tabla de precios combustibles)
    #save_to_postgresql_combustibles(transformed_data, config)

    # Guardar los valores agregados por año en PostgreSQL (Tabla de resumen de combustibles)
    #save_to_postgresql_resumen_anual(year_data, config)
