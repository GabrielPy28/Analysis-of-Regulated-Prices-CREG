import logging
from extract import extract_data
from transform import transform_data
from load import save_to_csv, save_to_postgresql_combustibles, save_to_postgresql_resumen_anual
from config import get_db_config

# Configuración básica de logging
logging.basicConfig(
    filename='Logs/main_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def main():
    # URL desde la cual se extraerán los datos
    url = 'https://creg.gov.co/publicaciones/15565/precios-de-combustibles-liquidos/'  # URL real de ejemplo
    
    # Paso 1: Extracción de datos
    logging.info("Iniciando el proceso de extracción de datos.")
    raw_data = extract_data(url)
    
    if raw_data is None:
        logging.error("No se pudieron extraer los datos.")
        return
    
    logging.info("Datos extraídos correctamente.")
    
    # Paso 2: Transformación de los datos
    logging.info("Iniciando el proceso de transformación de datos.")
    transformed_data, year_data = transform_data(raw_data)
    
    if transformed_data is None:
        logging.error("No se pudieron transformar los datos.")
        return
    
    logging.info("Datos transformados correctamente.")
    
    # Paso 3: Guardar los datos en archivos CSV
    logging.info("Guardando los datos transformados y el resumen anual en archivos CSV.")
    save_to_csv(transformed_data, year_data)  # Asegúrate de pasar year_data aquí
    
    # Paso 4: Cargar los datos en la base de datos
    config = get_db_config()  # Obtén la configuración de la base de datos
    
    logging.info("Cargando los datos transformados en la base de datos.")
    save_to_postgresql_combustibles(transformed_data, config)
    
    logging.info("Cargando el resumen anual en la base de datos.")
    save_to_postgresql_resumen_anual(year_data, config)  # Asegúrate de pasar year_data aquí
    
    logging.info("Proceso ETL completado exitosamente.")

if __name__ == "__main__":
    main()