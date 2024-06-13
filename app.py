import pandas
from src.sistemas_amortizacion import sistema_frances, sistema_aleman, sistema_americano, tasa_interes, sk
from shiny.express import input, render, ui
from shiny.types import ImgData
import plotly.graph_objects as go
from shinywidgets import render_widget
import faicons as fa
from pathlib import Path

# Iconos
ICONS = {
    "money": fa.icon_svg("money-bill"),
    "coins": fa.icon_svg("money-bill-trend-up"),
    "sack-dollar": fa.icon_svg("sack-dollar")
}

# Banderas
FLAGS = {
    "Frances": "img/france.svg",
    "Aleman": "img/germany.svg",
    "Americano": "img/usa.svg"
}

# PAGINA WEB

ui.include_css(
    Path(__file__).parent / "styles.css"
)

# Asegúrate de que static_assets recibe una ruta absoluta
ui.page_opts(static_assets=str(Path(__file__).parent))

# Agregar la cabecera con el título y la imagen
with ui.div(class_="header"):
    #ui.img(src="https://univercimas.com/wp-content/uploads/2021/05/Logo-de-la-Escuela-Politecnica-Nacional-EPN.png", alt="Logo", class_="header-logo")
    with ui.div(style="flex-grow: 1; text-align: center;"):  
        ui.h1("SISTEMAS DE AMORTIZACIÓN", class_="header-title")
    ui.img(src="https://cem.epn.edu.ec/imagenes/logos_institucionales/big_png/FACULTAD_CIENCIAS_big.png", alt="Ciencias", class_="header-logo-right")

def read_svg(filename):
    with open(filename, 'r') as f:
        svg_content = f.read()
    svg_content = svg_content.replace('<svg', '<svg class="center-image"')
    return svg_content
    
# Barra de la izquierda
with ui.sidebar(class_='bg-primary lead'):
    @render.ui
    def flag_svg():
        tipo = input.type()
        if tipo not in FLAGS:
            tipo = 'Frances'
        svg_content = read_svg(FLAGS[tipo])
        return ui.HTML(svg_content)
    ui.input_selectize("type", "Tipo de Amortización:", ["Frances", "Aleman", "Americano"])
    ui.input_selectize("frecuencia", "Frecuencia de pago:", ["Mensual", "Trimestral", "Semestral", "Anual"])
    ui.input_numeric("K", "Monto solicitado en dólares:", None, min=0)
    ui.input_numeric("n", "Numero de periodos (plazo):", None, min=0, step=1)
    ui.input_numeric("i", "Tasa anual efectiva (%):", None, min=0)
    
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


with ui.card(full_screen=True,min_height= 200):
    
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
                n = int(n) 
                
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
    @render_widget
    def plot_cuotas():
        if input.K() is not None and input.n() is not None and input.i() is not None:
            try:
                K = float(input.K())
                n = int(input.n())  
                i = float(input.i())

                if K < 0 or n < 0 or i < 0:
                    return None

                tipo = input.type()
                tasa = tasa_interes(i, input.frecuencia())

                if tipo == 'Frances':
                    df = sistema_frances(tasa, n, K)
                elif tipo == 'Aleman':
                    df = sistema_aleman(tasa, n, K)
                elif tipo == 'Americano':
                    df = sistema_americano(tasa, n, K)

                df = df.reset_index()
                df.drop(0, axis = 0, inplace=True)

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
                                marker_color='#132b60'))
                fig.add_trace(go.Bar(x=df['Periodos'], y=df['Interes (USD)'], 
                                name='Intereses', 
                                marker_color='#ff7373'))

                # Agregar una línea para la cuota total
                fig.add_trace(go.Scatter(x=df['Periodos'], y=df['Cuota (USD)'], 
                                    name='Cuota Total', 
                                    mode='lines', 
                                    line=dict(color='#58534c', width=1, dash = 'dot')))

                fig.update_layout(
                    title={
                    'text': 'Evolución de las Cuotas',
                    'y':0.95,  
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                    },
                    xaxis_title='Período',
                    yaxis_title='Valor (USD)',
                    template='plotly_white',
                    height=400,
                    barmode='stack',  # Apilar las barras
                    margin = dict(t=100),
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
            return None
                

                
