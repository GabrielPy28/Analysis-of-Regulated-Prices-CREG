from datetime import datetime
import logging
from collections import defaultdict
from extract import extract_data

# Configuración de logging en UTF-8 y en español
logging.basicConfig(
    filename='Logs/transform_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def convert_date(date_str: str):
    # Separar la fecha en partes
    parts = date_str.split('-')
    
    # Verificar que la longitud de parts sea la esperada
    if len(parts) != 3:
        raise ValueError(f"Formato de fecha inesperado: {date_str}")
    
    year = parts[0]  # Año
    month = parts[1]  # Mes
    day = parts[2]  # Día
    
    # Formatear la fecha
    formatted_date = f"{day}-{month}-{year}"
    return formatted_date

def transform_data(raw_data):
    logging.info(f"Datos obtenidos: {raw_data}")
    try:
        transformed_data = {}  # Diccionario en lugar de lista
        year_summary = defaultdict(lambda: {
            'gasolina_max': float('-inf'),
            'gasolina_min': float('inf'),
            'gasolina_avg': 0,
            'acpm_max': float('-inf'),
            'acpm_min': float('inf'),
            'acpm_avg': 0,
            'count': 0
        })
        
        for table_data in raw_data:
            # Limpiar la fecha
            date_str = table_data['date'].replace('\xa0', ' ')
            logging.info(f"Fecha limpia: {date_str}")
            
            # Convertir la fecha al formato de base de datos (DD-MM-YYYY)
            try:
                formatted_date = convert_date(date_str)
                table_data['date'] = formatted_date  # Actualizar la fecha transformada
                logging.info(f"Fecha transformada: {formatted_date}")
            except ValueError as e:
                logging.error(f"Error al transformar la fecha: {date_str} con el error: {e}")
                continue

            # Procesar las filas de datos
            for row in table_data['data']:
                try:
                    if len(row) >= 4:
                        gasolina_mc = row[2]
                        acpm = row[3]
                        year = formatted_date.split('-')[2]

                        # Actualizar los valores resumen
                        year_summary[year]['gasolina_max'] = max(year_summary[year]['gasolina_max'], float(gasolina_mc))
                        year_summary[year]['gasolina_min'] = min(year_summary[year]['gasolina_min'], float(gasolina_mc))
                        year_summary[year]['acpm_max'] = max(year_summary[year]['acpm_max'], float(acpm))
                        year_summary[year]['acpm_min'] = min(year_summary[year]['acpm_min'], float(acpm))
                        year_summary[year]['gasolina_avg'] += float(gasolina_mc)
                        year_summary[year]['acpm_avg'] += float(acpm)
                        year_summary[year]['count'] += 1
                    else:
                        logging.warning(f"Fila con datos incompletos: {row}. Se omite esta fila.")
                        continue

                except IndexError as e:
                    logging.error(f"Error al acceder a los datos de la fila: {row}, con el error: {e}")
                    continue

            # Agregar la fecha a los datos transformados
            transformed_data[formatted_date] = {
                'date': formatted_date,  # Asegúrate de que la fecha esté aquí
                'headers': table_data['headers'],
                'data': table_data['data']
            }

        # Calcular promedios
        for year, values in year_summary.items():
            if values['count'] > 0:
                values['gasolina_avg'] /= values['count']
                values['acpm_avg'] /= values['count']
            else:
                values['gasolina_avg'] = 0
                values['acpm_avg'] = 0

        # Crear un resumen por año
        year_data = []
        for year, values in year_summary.items():
            year_data.append({
                'year': year,
                'gasolina_max': values['gasolina_max'],
                'gasolina_min': values['gasolina_min'],
                'gasolina_avg': values['gasolina_avg'],
                'acpm_max': values['acpm_max'],
                'acpm_min': values['acpm_min'],
                'acpm_avg': values['acpm_avg']
            })

        logging.info("Transformación de datos completada exitosamente.")
        return transformed_data, year_data  # Devuelve el diccionario y la lista de resumen
    
    except Exception as e:
        logging.error(f"Error en la transformación de datos: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Ejemplo de raw_data (debería provenir del proceso de extracción)
    raw_data = extract_data('https://creg.gov.co/publicaciones/15565/precios-de-combustibles-liquidos/')
    
    # Intentar transformar los datos
    transformed_data, year_data = transform_data(raw_data)
    
    if transformed_data is not None and year_data is not None:
        logging.info(f"Primeros datos transformados: {transformed_data}")
        logging.info(f"Resumen por año: {year_data}")
        print("Datos transformados:")
        print(transformed_data)  # Muestra los datos transformados
        print("Resumen por año:")
        print(year_data)  # Muestra el resumen por año
    else:
        logging.error("No se pudieron transformar los datos.")
