import pandas as pd


# Funciones actuariales

def tasa_interes(i,frecuencia):
    i = i/100
    if frecuencia == 'Anual': return i
    if frecuencia == 'Semestral': return (1+i)**(1/2) - 1
    if frecuencia == 'Trimestral': return (1+i)**(1/4) - 1
    if frecuencia == 'Mensual': return (1+i)**(1/12) - 1


def annuity(i, n, type = 'immediate'):
    if i == 0: return n
    try:
        val = (1-(1+i)**(-n))/i
        if type == 'immediate':
            return val
        
        if type == 'due':
            return (1+i)*val
    except:
        print('Error')


def accumulate(i, n, type = 'immediate'):
    if i == 0: return n
    try:
        val = ((1+i)**n - 1)/i
        if type == 'immediate':
            return val
        if type == 'due':
            return (1+i)*val
    except:
        print('Error')


def ck(i, n, k, K, type = 'Frances'):
    try:
        if type == 'Frances':
            return round(K/annuity(i,n),2)
        
        if type == 'Aleman':
            if k == 1:
                return (K/n) + i*K
            return (K/n)*(1+i*(n-k+1))

    except:
        print('Error')

def vk(i, n, k, K, type = 'Frances'):
    c = ck(i,n,k,K,type)

    if k == 0: return 0
    
    try:
        if type == 'Frances':
            return c * (1+i)**(-n-1+k)
        
        if type == 'Aleman':
            return K/n
    except:
        print('Error')


def sk(i, n, k, K, type = 'Frances'):
    c = ck(i,n,k,K,type)
    
    if k == 0: return 0
    
    try:
        if type == 'Frances':
            return c * (1-(1+i)**(-n-1+k))
        
        if type == 'Aleman':
            return i * (n+1-k) * (K/n)
    except:
        print('Error')

# Sistemas de amortización

def sistema_frances(i,n,K):  
    amortizacion_real = [ round(vk(i, n, k, K),2) for k in range(n+1)]
    cuota_interes = [ round(sk(i, n, k, K),2) for k in range(n+1)]
    cuota = [round(amortizacion_real[k] + cuota_interes[k],2) for k in range(n+1)]
    saldo_adeudado = [round(K - sum(amortizacion_real[:k+1]),2) for k in range(n + 1)]
    df = pd.DataFrame({
        'Amort. Capital (USD)': amortizacion_real,
        'Interes (USD)': cuota_interes,
        'Cuota (USD)': cuota,
        'Saldo (USD)': saldo_adeudado
    })
    df.index.name = 'Periodos'
    return df


def sistema_aleman(i,n,K):
    amortizacion_real = [ round(vk(i, n, k, K, type = 'Aleman'),2) for k in range(n+1)]
    cuota_interes = [ round(sk(i, n, k, K, type = 'Aleman'),2) for k in range(n+1)]
    cuota = [round(amortizacion_real[k] + cuota_interes[k],2) for k in range(n+1)]
    saldo_adeudado = [round(K - sum(amortizacion_real[:k+1]),2) for k in range(n + 1)]
    df = pd.DataFrame({
        'Amort. Capital (USD)': amortizacion_real,
        'Interes (USD)': cuota_interes,
        'Cuota (USD)': cuota,
        'Saldo (USD)': saldo_adeudado
    })
    df.index.name = 'Periodos'
    return df


def sistema_americano(i, n, deuda):
    amortizacion_real = [ deuda if k == n else 0 for k in range(n+1)]
    cuota_interes = [ 0 if k==0 else round(deuda*i,2) for k in range(n+1)]
    cuota = [round(amortizacion_real[k] + cuota_interes[k],2) for k in range(n+1)]
    saldo_adeudado = [round(deuda - sum(amortizacion_real[:k+1]),2) for k in range(n + 1)]
    df = pd.DataFrame({
        'Amort. Capital (USD)': amortizacion_real,
        'Interes (USD)': cuota_interes,
        'Cuota (USD)': cuota,
        'Saldo (USD)': saldo_adeudado
    })
    df.index.name = 'Periodos'

    return df

