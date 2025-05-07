# Analysis of Regulated Prices CREG

# Backend

Este proyecto incluye un flujo ETL (Extracción, Transformación y Carga) implementado en Python. Utiliza bibliotecas como `BeautifulSoup`, `Requests` y `Pandas` para extraer, transformar y cargar datos sobre precios de combustibles desde una página web.

## Estructura del Proyecto

La carpeta del backend contiene los siguientes archivos:

- **`extract.py`**: Contiene la lógica para extraer datos de la página web. Utiliza `BeautifulSoup` para analizar el HTML y `Requests` para realizar solicitudes HTTP.
- **`transform.py`**: Se encarga de transformar los datos extraídos, incluyendo la limpieza y el cálculo de estadísticas.
- **`load.py`**: Implementa la lógica para guardar los datos transformados en archivos CSV y en una base de datos PostgreSQL (opcional).
- **`config.py`**: Maneja la configuración de la base de datos utilizando variables de entorno.
- **`main.py`**: Orquesta el flujo ETL, llamando a las funciones de extracción, transformación y carga.

## Flujo ETL

1. **Extracción**: Se extraen los datos de la URL especificada utilizando la función `extract_data()`.
2. **Transformación**: Los datos extraídos se transforman mediante la función `transform_data()`, que limpia y organiza los datos, además de calcular estadísticas anuales.
3. **Carga**: Los datos transformados se guardan en archivos CSV y, opcionalmente, se pueden cargar en una base de datos PostgreSQL.

## Ejecución

Para ejecutar el flujo ETL, simplemente ejecuta el archivo `main.py`:
```bash
python main.py
```

> [!IMPORTANT]
> Asegúrate de tener las dependencias necesarias instaladas. Puedes instalar las dependencias utilizando el archivo **`requirements.txt`**:
```bash
pip install -r requirements.txt
```

---

## Frontend

La carpeta del frontend se llama `App` y contiene los siguientes archivos:

- **`app.py`**: Este archivo es el punto de entrada de la aplicación Dash. Configura la aplicación, define los callbacks para actualizar los gráficos y carga los datos necesarios para la visualización.
- **`data_loader.py`**: Contiene funciones para cargar los datos desde los archivos CSV generados por el proceso ETL. Incluye la función `load_data()` que combina los archivos de precios de combustibles y convierte las fechas al formato adecuado.
- **`layout.py`**: Define el diseño de la aplicación, incluyendo la estructura de los gráficos y los KPI (Indicadores Clave de Desempeño). También incluye la tabla que muestra los precios de combustibles por ciudad y año.

### Funcionamiento

1. **Carga de Datos**: La aplicación carga los datos de precios de combustibles desde la carpeta `../Download`, donde se espera que se encuentren los archivos CSV generados por el proceso ETL. Es importante que el proceso ETL se haya ejecutado previamente para que los datos estén disponibles.

2. **Visualización**: La aplicación presenta varios gráficos interactivos que muestran la evolución de los precios de gasolina y ACPM en Colombia, así como comparaciones de promedios por año y ciudad. Los gráficos se actualizan dinámicamente según el rango de fechas seleccionado por el usuario.

3. **KPIs**: Se muestran indicadores clave de desempeño que reflejan los precios máximos, mínimos y promedios de gasolina y ACPM, junto con el porcentaje de cambio respecto al año anterior.

4. **Tabla de Datos**: La aplicación incluye una tabla que permite a los usuarios ver los precios de combustibles por ciudad y año, con opciones para filtrar y ordenar los datos.

### Ejecución

Para ejecutar la aplicación, asegúrate de que el proceso ETL se haya completado y que los archivos CSV estén disponibles en la carpeta `../Download`. Luego, ejecuta el archivo `app.py`:

```bash
python app.py
```

La aplicación se ejecutará en [localhost](http://127.0.0.1:8000) y podrás interactuar con los gráficos y la tabla de datos.

> [!IMPORTANT]
> Asegúrate de tener las dependencias necesarias instaladas. Puedes instalar las dependencias utilizando el archivo **`requirements.txt`**:
```bash
pip install -r requirements.txt
```

---

## Diseño Teórico de la Base de Datos

Para almacenar los datos transformados sobre precios de combustibles, se propone el siguiente diseño de base de datos. Este diseño incluye dos tablas: una para los precios de combustibles y otra para el resumen anual de combustibles.

### 1. Tabla `precios_combustibles`

Esta tabla almacenará los datos de precios de combustibles por fecha y ciudad.

```sql
CREATE TABLE precios_combustibles (
    id SERIAL PRIMARY KEY,  -- Identificador único para cada registro
    fecha DATE NOT NULL,     -- Fecha del registro
    ciudad VARCHAR(100) NOT NULL,  -- Ciudad donde se registró el precio
    gasolina_mc DECIMAL(10, 2) NOT NULL,  -- Precio de Gasolina MC
    acpm DECIMAL(10, 2) NOT NULL,  -- Precio de ACPM
    CONSTRAINT uq_fecha_ciudad UNIQUE (fecha, ciudad)  -- Restricción de unicidad
);
```

### Índices
Para mejorar el rendimiento de las consultas, se pueden crear índices en las columnas más consultadas:
```sql
CREATE INDEX idx_fecha ON precios_combustibles(fecha);
CREATE INDEX idx_ciudad ON precios_combustibles(ciudad);
```

### 2. Tabla resumen_combustibles_anuales
Esta tabla almacenará un resumen anual de los precios de combustibles.
```sql
CREATE TABLE resumen_combustibles_anuales (
    year INT PRIMARY KEY,  -- Año del resumen
    max_gasolina_mc DECIMAL(10, 2) NOT NULL,  -- Precio máximo de Gasolina MC
    min_gasolina_mc DECIMAL(10, 2) NOT NULL,  -- Precio mínimo de Gasolina MC
    avg_gasolina_mc DECIMAL(10, 2) NOT NULL,  -- Precio promedio de Gasolina MC
    max_acpm DECIMAL(10, 2) NOT NULL,  -- Precio máximo de ACPM
    min_acpm DECIMAL(10, 2) NOT NULL,  -- Precio mínimo de ACPM
    avg_acpm DECIMAL(10, 2) NOT NULL   -- Precio promedio de ACPM
);
```

> [!NOTE] Consideraciones
> Restricciones: Se han definido restricciones de unicidad en la tabla precios_combustibles para evitar duplicados de registros por fecha y ciudad.
> Tipos de datos: Se han utilizado tipos de datos adecuados para cada columna, asegurando que los precios se almacenen con precisión.
> Índices: Los índices propuestos mejorarán el rendimiento de las consultas, especialmente en tablas con un gran volumen de datos.

Este diseño de base de datos proporciona una estructura sólida para almacenar y consultar datos sobre precios de combustibles, facilitando el análisis y la generación de reportes.
