from fpdf import FPDF
from src.sistemas_amortizacion import sistema_frances, tasa_interes, sistema_americano,sistema_aleman
import io

def create_dataframe(tipo, frecuencia, n, K, i ):
    tasa = tasa_interes(i, frecuencia)
    if tipo == 'Frances': df = sistema_frances(tasa, n, K)
    elif tipo == 'Aleman': df = sistema_aleman(tasa, n, K)
    else: df = sistema_americano(tasa, n, K)
    df = df.reset_index()
    df.iloc[-1,-1] = 0
    return df


def create_pdf(tipo, frecuencia, n, K, i):
    df = create_dataframe(tipo, frecuencia, n, K, i)
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    github = 'https://github.com/Pepool17?tab=repositories'
    pdf.image("https://univercimas.com/wp-content/uploads/2021/05/Logo-de-la-Escuela-Politecnica-Nacional-EPN.png", 
              x=165, y=25, w=30, link=github)

    pdf.set_font('Times', 'B', 18)
    pdf.text(x=18, y=30, txt='Simulador de crédito')

    pdf.set_font('Times', '', 14)
    pdf.text(x=18, y=40, txt=f'Tipo de amortización: {tipo}')
    pdf.text(x=18, y=50, txt=f'Frecuencia de pago: {frecuencia}')
    pdf.text(x=18, y=60, txt=f'Monto solicitado: {K}')
    pdf.text(x=18, y=70, txt=f'Plazo (periodos): {n}')
    pdf.text(x=18, y=80, txt=f'Tasa anual efectiva: {i}%')

    pdf.set_font('Times', 'B', 14)
    pdf.text(x=18, y=95, txt='Tabla de Amortización para el Tipo Francés')

    start_x = 18
    start_y = 100
    column_widths = {
        'Periodos': 20,
        'Amort. Capital (USD)': 45,
        'Interes (USD)': 35,
        'Cuota (USD)': 35,
        'Saldo (USD)': 38
    }
    cell_height = 9
    pdf.set_xy(start_x, start_y)
    pdf.set_font('Times', 'B', 12)
    for column in df.columns:
        pdf.cell(column_widths[column], cell_height, column, 1, 0, 'C')
    pdf.ln(cell_height)
    pdf.set_font('Times', '', 12)
    for index, row in df.iterrows():
        pdf.set_x(start_x)
        for column in df.columns:
            value = row[column]
            if column == 'Periodos':
                value = f'{int(value)}'
            else:
                value = f'{value:,.2f}'
            pdf.cell(column_widths[column], cell_height, value, 1, 0, 'C')
        pdf.ln(cell_height)

    buffer = io.BytesIO()
    pdf.output(dest='S').encode('latin1')
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)
    return buffer