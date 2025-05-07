import os
from dash import Dash, Input, Output
import dash_bootstrap_components as dbc
from layout import create_layout
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
from data_loader import load_data
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


# Configuración de meta tags
tags = [
    {'charset': 'utf-8'},
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'}
]
# Estilos de la aplicación
styles = ['styles.css', dbc.icons.BOOTSTRAP, dbc.themes.SUPERHERO]

# Inicializa la aplicación Dash
app = Dash(
    __name__, title='Análisis de Precios Regulados (CREG)',
    update_title='Loading...', suppress_callback_exceptions=True, 
    prevent_initial_callbacks=False,
    meta_tags=tags,
    external_stylesheets=styles
)
# Cargar el layout
app.layout = create_layout()

@app.callback(
    [Output('fig1-graph', 'figure'),
     Output('fig2-graph', 'figure'),
     Output('fig3-graph', 'figure'),
     Output('fig4-graph', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):

    # Cargar datos
    downloads_folder = "../Download"
    df = load_data(downloads_folder)
    
    # Convertir las fechas de inicio y fin a datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar datos según el rango de fechas
    filtered_data = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]

    # Ordenar los datos por fecha en orden ascendente
    filtered_data = filtered_data.sort_values(by='fecha')

    # Gráfico 1: Gráfico de área para Gasolina
    fig1 = px.area(
        filtered_data,
        x='fecha',
        y='Gasolina MC ($/gal)',
        color='Ciudad',
        title='Evolución de Precios de Gasolina en Colombia',
        labels={'Gasolina MC ($/gal)': 'Precio ($/gal)', 'fecha': 'Fecha'},
        template='plotly_white'
    )

    # Gráfico 2: Gráfico de área para ACPM
    fig2 = px.area(
        filtered_data,
        x='fecha',
        y='ACPM ($/gal)',
        color='Ciudad',
        title='Evolución de Precios de ACPM en Colombia',
        labels={'ACPM ($/gal)': 'Precio ($/gal)', 'fecha': 'Fecha'},
        template='plotly_white'
    )

    # Gráfico 3: Comparación de promedios de ACPM y Gasolina MC
    avg_prices = filtered_data.groupby(filtered_data['fecha'].dt.year).agg(
        Promedio_Gasolina=('Gasolina MC ($/gal)', 'mean'),
        Promedio_ACPM=('ACPM ($/gal)', 'mean')
    ).reset_index()

    fig3 = go.Figure()
    # Agregar barras para el promedio de Gasolina
    fig3.add_trace(go.Bar(
        x=avg_prices['fecha'],  # Aquí ya no se usa .dt
        y=avg_prices['Promedio_Gasolina'],
        name='Promedio Gasolina MC',
        marker=dict(color='orange', opacity=0.7),
        width=0.4
    ))

    # Agregar barras para el promedio de ACPM
    fig3.add_trace(go.Scatter(
        x=avg_prices['fecha'],  # Aquí ya no se usa .dt
        y=avg_prices['Promedio_ACPM'],
        name='Promedio ACPM',
        marker=dict(color='blue', opacity=0.7)
    ))

    fig3.update_layout(
        title='Comparación de Promedios de Gasolina MC y ACPM por Año',
        xaxis_title='Año',
        yaxis_title='Precio Promedio ($/gal)',
        barmode='group',  # Agrupar las barras
        legend_title='Tipo',
        template='plotly_white',
        hovermode='x unified',
        bargap=0.15, 
        bargroupgap=0.1 
    )

    # Gráfico 4: Gráfico de burbujas para Gasolina MC por ciudad
    avg_gasolina_by_city = filtered_data.groupby('Ciudad')['Gasolina MC ($/gal)'].mean().reset_index()
    
    fig4 = px.scatter(
        avg_gasolina_by_city,
        x='Ciudad',  # Eje X: Ciudad
        y='Gasolina MC ($/gal)',  # Eje Y: Precio promedio de Gasolina
        size='Gasolina MC ($/gal)',  # Tamaño de la burbuja: Precio promedio
        animation_group='Ciudad', 
        title='Comparación de Precios de Gasolina MC por Ciudad',
        labels={'Gasolina MC ($/gal)': 'Precio Promedio ($/gal)', 'Ciudad': 'Ciudad'},
        template='plotly_white'
    )


    return fig1, fig2, fig3, fig4

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)