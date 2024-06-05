import pandas
from src.sistemas_amortizacion import sistema_frances, sistema_aleman, sistema_americano, tasa_interes, sk
from shiny.express import input, render, ui
import plotly.graph_objects as go
from shinywidgets import render_widget
import faicons as fa
from pathlib import Path


ui.include_css(
    Path(__file__).parent / "styles.css"
)

# Asegúrate de que static_assets recibe una ruta absoluta
ui.page_opts()

# Agregar la cabecera con el título y la imagen
with ui.div(class_="header"):
    ui.img(src="https://univercimas.com/wp-content/uploads/2021/05/Logo-de-la-Escuela-Politecnica-Nacional-EPN.png", alt="Logo", class_="header-logo")
    with ui.div(style="flex-grow: 1; text-align: center;"):  
        ui.h1("Sistema de Amortización", class_="header-title")
    ui.img(src="https://cem.epn.edu.ec/imagenes/logos_institucionales/big_png/FACULTAD_CIENCIAS_big.png", alt="Ciencias", class_="header-logo-right")

# Barra de la izquierda
with ui.sidebar(class_='bg-primary lead'):
    ui.input_selectize("type", "Tipo de Amortización:", ["Frances", "Aleman", "Americano"])
    ui.input_selectize("frecuencia", "Frecuencia de pago:", ["Mensual","Trimestral","Semestral","Anual"])
    ui.input_numeric("K", "Monto solicitado en dólares:", None, min=0)
    ui.input_numeric("n", "Numero de periodos (plazo):", None, min = 0, step=1)
    ui.input_numeric("i", "Tasa anual efectiva (%):", None, min = 0)
    

# Iconos
ICONS = {
    "money": fa.icon_svg("money-bill"),
    "coins": fa.icon_svg("money-bill-trend-up"),
    "sack-dollar": fa.icon_svg("sack-dollar")
}

# Función para calcular las cuotas de interés
def calcular_cuotas_interes(i, frecuencia, n, K, tipo):
    tasa = tasa_interes(i, frecuencia)
    if tipo == 'Americano':
        return [ 0 if k==0 else round(K*tasa,2) for k in range(n+1)]
    cuotas = [round(sk(tasa, n, k, K, tipo), 2) for k in range(n + 1)]
    return cuotas

# Página 1
with ui.layout_column_wrap():
    with ui.value_box(showcase=ICONS["money"]):
        ui.HTML("<p class = 'black-text'> Monto solicitado (USD)</p>")
        @render.express
        def monto():
            if input.K() is not None and input.n() is not None and input.i() is not None:
                if input.K() < 0 or input.n() < 0 or input.i() < 0: None 
                else : ui.HTML(f"<p class='blue-text'>{input.K()}</p>")

    with ui.value_box(showcase=ICONS["coins"]):
        ui.HTML("<p class = 'black-text'> Total Intereses (USD)</p>")
        @render.express
        def intereses():
            if input.K() is not None and input.n() is not None and input.i() is not None:
                if input.K() < 0 or input.n() < 0 or input.i() < 0 : None 
                else: 
                    cuotas = calcular_cuotas_interes(float(input.i()), input.frecuencia(), 
                                                     int(input.n()), float(input.K()), input.type())
                    ui.HTML(f"<p class='blue-text'>{round(sum(cuotas),2)}</p>")

    with ui.value_box(showcase=ICONS["sack-dollar"]):
        ui.HTML("<p class = 'black-text'> Total a pagar (USD)</p>")
        @render.express
        def total_pagar():
            if input.K() is not None and input.n() is not None and input.i() is not None:
                if input.K() < 0 or input.n() < 0 or input.i() < 0: None 
                else:
                    K = float(input.K())
                    cuotas = calcular_cuotas_interes(float(input.i()), input.frecuencia(), 
                                                        int(input.n()), K, input.type())
                    ui.HTML(f"<p class='blue-text'>{round(K + sum(cuotas),2)}</p>")

with ui.layout_columns(col_widths=[6,6], fill = False):
    with ui.card():
        @render.ui
        def message_or_table():
            if input.K() is not None and input.n() is not None and input.i() is not None:
                try:
                    
                    K = float(input.K())
                    n = float(input.n())  
                    i = float(input.i())

                    if K < 0:
                        return ui.HTML(f'<div class="error_style">Por favor, el monto solicitado debe ser positivo.</div>')
                    elif n < 0 or n != int(n):
                        return ui.HTML(f'<div class="error_style">El número de periodos debe ser un entero positivo.</div>')
                    elif i < 0:
                        return ui.HTML(f'<div class="error_style">Por favor, ingrese una tasa anual efectiva no negativa.</div>')

                    # Si todos los valores son válidos, proceder con el cálculo y mostrar la tabla
                    tipo = input.type()
                    tasa = tasa_interes(i, input.frecuencia())
                    n = int(n)  # Ahora es seguro convertir a int
                    
                    if tipo == 'Frances':
                        df = sistema_frances(tasa, n, K)
                    elif tipo == 'Aleman':
                        df = sistema_aleman(tasa, n, K)
                    elif tipo == 'Americano':
                        df = sistema_americano(tasa, n, K)
                    
                    df = df.reset_index()
                    for col in df.columns:
                        if df[col].dtype in [int, float]:
                            df[col] = df[col].map(lambda x: f'{x:.2f}')
                    
                    # Convertir DataFrame a HTML
                    table_html = df.to_html(index=False, classes="table table-striped table-bordered")
                    
                    # Aplicar estilos CSS a la tabla
                    table_style = '''
                        <style>
                            .table { width: 100%; }
                            .table th { background-color: #132b60; color: white; text-align: left; }
                            .table td { background-color: #f5f5f5; text-align: left; }
                        </style>
                    '''
                    
                    return ui.HTML(table_style + table_html)
                except Exception as e:
                    print(f"Error: {e}")
                    return ui.HTML(f'<div class="error_style">Error: {e}</div>')
            else:
                return ui.HTML(f'<div class="aviso_datos"> Ingrese valores en el panel izquierdo </div>')
                
    with ui.card():
        with ui.card():
            @render_widget
            def plot_cuotas():
                if input.K() is not None and input.n() is not None and input.i() is not None:
                    try:
                        K = float(input.K())
                        n = int(input.n())  
                        i = float(input.i())

                        if K < 0 or n < 0 or i < 0:
                            return go.Figure()

                        tipo = input.type()
                        tasa = tasa_interes(i, input.frecuencia())

                        if tipo == 'Frances':
                            df = sistema_frances(tasa, n, K)
                        elif tipo == 'Aleman':
                            df = sistema_aleman(tasa, n, K)
                        elif tipo == 'Americano':
                            df = sistema_americano(tasa, n, K)

                        df = df.reset_index()

                        # Asegurarse de que 'Cuota (USD)' esté en el DataFrame
                        if 'Cuota (USD)' not in df.columns:
                            print("Error: La columna 'Cuota (USD)' no está en el DataFrame")
                            return go.Figure()

                        # Convertir columna a tipo numérico
                        df['Cuota (USD)'] = pandas.to_numeric(df['Cuota (USD)'], errors='coerce')

                        fig = go.Figure()
                        
                        # Trazar las barras para cada componente de la cuota
                        df['Amort. Capital (USD)'] = pandas.to_numeric(df['Amort. Capital (USD)'], errors='coerce')
                        df['Interes (USD)'] = pandas.to_numeric(df['Interes (USD)'], errors='coerce')
                        
                        fig.add_trace(go.Bar(x=df['Periodos'], y=df['Amort. Capital (USD)'], 
                                        name='Capital Amortizado', 
                                        marker_color='green'))
                        fig.add_trace(go.Bar(x=df['Periodos'], y=df['Interes (USD)'], 
                                        name='Intereses', 
                                        marker_color='blue'))

                        # Agregar una línea para la cuota total
                        fig.add_trace(go.Scatter(x=df['Periodos'], y=df['Cuota (USD)'], 
                                            name='Cuota Total', 
                                            mode='lines+markers', 
                                            line=dict(color='red', width=3)))

                        fig.update_layout(
                            title='Evolución de las Cuotas',
                            xaxis_title='Período',
                            yaxis_title='Valor (USD)',
                            template='plotly_white',
                            height=400,
                            barmode='stack',  # Apilar las barras
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )

                        return fig
                    except Exception as e:
                        print(f"Error: {e}")
                        return go.Figure()
                else:
                    return go.Figure()
                
        with ui.card():
            @render_widget
            def plot_interes():
                if input.K() is not None and input.n() is not None and input.i() is not None:
                    try:
                        K = float(input.K())
                        n = int(input.n())  
                        i = float(input.i())

                        if K < 0 or n < 0 or i < 0:
                            return go.Figure()

                        tipo = input.type()
                        tasa = tasa_interes(i, input.frecuencia())

                        if tipo == 'Frances':
                            df = sistema_frances(tasa, n, K)
                        elif tipo == 'Aleman':
                            df = sistema_aleman(tasa, n, K)
                        elif tipo == 'Americano':
                            df = sistema_americano(tasa, n, K)

                        df = df.reset_index()

                        # Asegurarse de que 'Interes (USD)' esté en el DataFrame
                        if 'Interes (USD)' not in df.columns:
                            print("Error: La columna 'Interes (USD)' no está en el DataFrame")
                            return go.Figure()

                        # Convertir columna a tipo numérico
                        df['Interes (USD)'] = pandas.to_numeric(df['Interes (USD)'], errors='coerce')

                        # Omitir el primer período si el interés es 0 (común en muchos sistemas)
                        if df.loc[0, 'Interes (USD)'] == 0:
                            df = df[1:]

                        fig = go.Figure()

                        # Trazar barras para mostrar el interés en cada período
                        fig.add_trace(go.Bar(x=df['Periodos'], y=df['Interes (USD)'], 
                                        name='Intereses por Período', 
                                        marker_color='blue',
                                        text=df['Interes (USD)'].apply(lambda x: f'{x:.2f}'),
                                        textposition='outside',
                                        hovertemplate='Período %{x}<br>Interés: $%{y:.2f}<extra></extra>'))

                        fig.update_layout(
                            title=f'Evolución de los Intereses por Período - {tipo}',                    xaxis_title='Período',
                            yaxis_title='Interés (USD)',
                            template='plotly_white',
                            height=400,
                            showlegend=False,  # No es necesario mostrar la leyenda ya que solo hay una serie
                            xaxis=dict(
                                tickmode='linear',  # Asegura que todos los períodos se muestren
                                dtick=1  # Un tick por cada período
                            ),
                            yaxis=dict(
                                title_standoff=15  # Un poco más de espacio para las etiquetas de texto
                            ),
                            margin=dict(
                                l=50, r=50, t=50, b=50  # Márgenes para asegurar que las etiquetas no se corten
                            ),
                            plot_bgcolor='rgba(240, 240, 240, 0.5)',  # Un fondo gris claro para mejor contraste
                            hoverlabel=dict(
                                bgcolor="white",
                                font_size=12,
                                font_family="Arial"
                            )
                        )

                        return fig
                    except Exception as e:
                        print(f"Error: {e}")
                        return go.Figure()
                else:
                    return go.Figure()
                
