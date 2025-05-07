# extract_data.py
import requests
from bs4 import BeautifulSoup
import logging
import os
import re

# Crear el directorio de logs si no existe
os.makedirs('Logs', exist_ok=True)

# Configuración de logging en UTF-8 y en español
logging.basicConfig(
    filename='Logs/extraction_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def extract_date_from_caption(caption_text):
    logging.info(f"Procesando caption para extraer fecha: {caption_text}")
    
    # Eliminar caracteres especiales invisibles y normalizar espacios
    caption_text = ' '.join(caption_text.split())

    # Expresiones regulares comunes de fechas en español
    patterns = [
        r'Vigencia\s*de\s*(\d{1,2})\s*(?:de|del)\s*([a-zA-Z]+)\s*(?:de|del)\s*(\d{4})',
        r'Vigencia\s*(\d{1,2})\s*(?:de|del)\s*([a-zA-Z]+)\s*(?:de|del)\s*(\d{4})',
        r'a partir del\s*(\d{1,2})\s*(?:de|del)\s*([a-zA-Z]+)\s*(?:de|del)\s*(\d{4})',
        r'Vigencia\s*de\s*([a-zA-Z]+)\s*(?:de|del)\s*(\d{4})'
    ]


    for pattern in patterns:
        match = re.search(pattern, caption_text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3:
                    day, month, year = groups
                elif len(groups) == 2:
                    day = '01'
                    month, year = groups
                else:
                    continue

                # Mapeo de nombres de meses a números
                month_map = {
                    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                    'septiembre': '09', 'setiembre': '09', 'octubre': '10',
                    'noviembre': '11', 'diciembre': '12'
                }

                month = month.lower()
                if month in month_map:
                    month_num = month_map[month]
                    return f"{year}-{month_num}-{day.zfill(2)}"
            except Exception as e:
                logging.error(f"Error procesando fecha: {e}")
    
    logging.error(f"No se pudo extraer la fecha correctamente desde el caption: {caption_text}")
    return None

def extract_data(url):
    try:
        logging.info("Iniciando la extracción de datos desde la URL: %s", url)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        logging.info(f"Código de estado HTTP: {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table')
        logging.info(f"Se encontraron {len(tables)} tablas.")
        if not tables:
            raise ValueError("No se encontraron tablas en la página web.")

        raw_data = []

        for table in tables:
            caption = table.find('caption')
            if not caption:
                continue

            caption_text = caption.get_text().strip()
            logging.info(f"Texto del caption: {caption_text}")

            # Usar la función mejorada para extraer la fecha
            date = extract_date_from_caption(caption_text)
            if not date:
                continue

            headers = [th.text.strip() for th in table.find_all('th')]

            data = []
            for row in table.find('tbody').find_all('tr'):
                cols = [td.text.strip() for td in row.find_all('td')]
                logging.info(f"Fila de datos: {cols}")

                if len(cols) > 1 and "Promedio PVP precio" in cols[1]:
                    logging.info(f"Fila eliminada debido a 'Promedio PVP precio': {cols}")
                    continue

                if cols:
                    data.append(cols)

            raw_data.append({
                'date': date,
                'headers': headers,
                'data': data
            })

        logging.info("Datos extraídos exitosamente.")
        return raw_data

    except Exception as e:
        logging.error("Error en la extracción de datos: %s", str(e))
        return None

if __name__ == "__main__":
    url = 'https://creg.gov.co/publicaciones/15565/precios-de-combustibles-liquidos/'
    raw_data = extract_data(url)
    
    if raw_data is not None:
        logging.info("Muestra de los datos crudos extraídos: \n%s", raw_data[:2])
        print("Datos crudos extraídos:")
        print(raw_data[:2])
    else:
        logging.error("No se pudieron obtener los datos crudos.")
