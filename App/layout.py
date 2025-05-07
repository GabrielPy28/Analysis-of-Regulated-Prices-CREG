import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dash_table.Format import Format, Symbol
import dash_bootstrap_components as dbc
from data_loader import load_data, load_annual_data, calcular_porcentaje

def create_layout():
    downloads_folder = "../Download"
    df = load_data(downloads_folder)
    resumen_file = "../Download/resumen_combustibles_anuales.csv"
    df_anual = load_annual_data(resumen_file)

    # Procesar datos para gráficos
    df_cities = df[['Ciudad', 'Gasolina MC ($/gal)', 'ACPM ($/gal)']].copy()
    df_cities.columns = ['Ciudad', 'Gasolina_MC', 'ACPM']
    
    # Obtener el último año y datos para KPIs
    ultimo_anio = df_anual['year'].max()
    datos_ultimo_anio = df_anual[df_anual['year'] == ultimo_anio].iloc[0]
    anio_anterior = ultimo_anio - 1
    datos_anterior = df_anual[df_anual['year'] == anio_anterior].iloc[0]

    # Calcular porcentajes para cada KPI
    porcentaje_max_gasolina = calcular_porcentaje(datos_ultimo_anio['gasolina_max'], datos_anterior['gasolina_max'])
    porcentaje_min_gasolina = calcular_porcentaje(datos_ultimo_anio['gasolina_min'], datos_anterior['gasolina_min'])
    porcentaje_avg_gasolina = calcular_porcentaje(datos_ultimo_anio['gasolina_avg'], datos_anterior['gasolina_avg'])
    porcentaje_avg_acpm = calcular_porcentaje(datos_ultimo_anio['acpm_avg'], datos_anterior['acpm_avg'])

    layout = dbc.Container(
        [
            html.H1("Análisis de Precios de Combustibles en Colombia", className="text-center my-4"),
            dbc.Row([
                create_kpi_card("Precio Máximo Gasolina MC", datos_ultimo_anio['gasolina_max'], porcentaje_max_gasolina),
                create_kpi_card("Precio Mínimo Gasolina MC", datos_ultimo_anio['gasolina_min'], porcentaje_min_gasolina),
                create_kpi_card("Precio Promedio Gasolina MC", datos_ultimo_anio['gasolina_avg'], porcentaje_avg_gasolina),
                create_kpi_card("Precio Promedio ACPM", datos_ultimo_anio['acpm_avg'], porcentaje_avg_acpm)
            ], justify="center"),
            
            # Segunda fila con DatePickerRange y gráficos
            dbc.Row([
                dbc.Col([
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date='2022-01-01',
                        end_date=pd.to_datetime('today').date(),
                        display_format='YYYY-MM-DD',
                        style={'margin-bottom': '20px'}
                    )
                ], width=12),
            ], justify="center"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='fig1-graph',
                        config={'displayModeBar': False}  # Opcional: Ocultar la barra de herramientas
                    )
                ], lg=6, md=12, sm=12, xs=12, style={'marginTop': '20px', 'marginBottom': '20px'}),  # Márgenes
                dbc.Col([
                    dcc.Graph(
                        id='fig2-graph',
                        config={'displayModeBar': False}  # Opcional: Ocultar la barra de herramientas
                    )
                ], lg=6, md=12, sm=12, xs=12, style={'marginTop': '20px', 'marginBottom': '20px'})  # Márgenes
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='fig3-graph',
                        config={'displayModeBar': False}  # Opcional: Ocultar la barra de herramientas
                    )
                ], lg=6, md=12, sm=12, xs=12, style={'marginTop': '20px', 'marginBottom': '20px'}),  # Márgenes
                dbc.Col([
                    dcc.Graph(
                        id='fig4-graph',
                        config={'displayModeBar': False}  # Opcional: Ocultar la barra de herramientas
                    )
                ], lg=6, md=12, sm=12, xs=12, style={'marginTop': '20px', 'marginBottom': '20px'})  # Márgenes
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    html.H2("Tabla de Precios de Combustibles por Ciudad y Año", style={'textAlign': 'center'}),
                    get_table()
                ], lg=12, md=12, sm=12, xs=12, style={'marginTop': '20px', 'marginBottom': '20px'}),  # Márgenes
            ], justify='center')
        ],
        fluid=True
    )

    return layout

def create_kpi_card(title, value, percentage):
    return dbc.Col([
        dbc.Card([
            dbc.CardHeader(title, className="card_title text-center"),
            dbc.CardBody([
                html.Div(
                    children=[
                        html.H5(f"${value:.2f}", className="card-title"),
                        html.H6(
                            (f"{'Subió' if percentage > 0 else 'Bajó'} un {abs(percentage):.2f}%", html.I(className="bi bi-graph-up-arrow icon_search text-success" if percentage > 0 else "bi bi-graph-down-arrow icon_search text-danger" , style={"margin-left": "4px"})), 
                            className="text-success" if percentage > 0 else "text-danger"),
        
                    ],
                    className="text-center"
                )
            ])
        ], className="kpi-card mb-4"),
    ], width=3, lg=3, md=6, sm=6, xs=12)

def get_table():
    
    downloads_folder = "../Download"
    df = load_data(downloads_folder)

    # Convertir la fecha al formato deseado y extraer el año
    df['year'] = pd.to_datetime(df['fecha']).dt.year
    df = df.sort_values(by='year', ascending=False)  # Ordenar desde el año actual hacia el menor

    return DataTable(
        columns=[
            {"name": "No. (Ranking de ese año)", "id": "No."},
            {"name": "Ciudad", "id": "Ciudad"},
            {"name": "Gasolina MC ($/gal)", "id": "Gasolina MC ($/gal)", "type": "numeric", 
            "format": Format(symbol=Symbol.yes, precision=2)},
            {"name": "ACPM ($/gal)", "id": "ACPM ($/gal)", "type": "numeric", 
            "format": Format(symbol=Symbol.yes, precision=2)},
            {"name": "Año", "id": "year"},
        ],
        data=df.to_dict('records'),
        filter_action='native',  # Permitir filtrado
        sort_action='native',     # Permitir ordenamiento
        page_action='native',     # Permitir paginación
        page_size=10,            # Número de filas por página
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'padding': '5px',
            'verticalAlign': 'middle',  # Alineación vertical en el medio
            'color': 'black',            # Color del texto
        },
        style_header={
            'backgroundColor': 'lightgrey',
            'textAlign': 'center',
            'fontWeight': 'bold',
            'verticalAlign': 'middle',  # Alineación vertical en el medio
            'color': 'black',            # Color del texto en el header
        },
    )