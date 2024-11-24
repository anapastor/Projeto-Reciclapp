import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import locale
import seaborn as sns
import unicodedata

arquivo = r'C:\Users\kalle\Desktop\Importante\Programação\Trabalho 4 º Semstre\Projeto-Reciclapp\projeto_back\graficos\amlurbcoletatiposresiduos2021.csv'

# Ler o arquivo mantendo a vírgula como separador decimal
data = pd.read_csv(arquivo, encoding='ISO-8859-1', delimiter=';', decimal=',')

# Remover espaços em branco nos nomes das colunas
data.columns = data.columns.str.strip()

# Normalizar os nomes das colunas (remover acentos e espaços extras)
data.columns = [unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8').strip() for col in data.columns]

# Renomear a coluna com erro de acentuação (ajustando para o nome correto)
data.rename(columns={'Tipo de RESADUO - Toneladas': 'TIPO DE RESIDUO'}, inplace=True)

# Filtrar dados onde a coluna 'TIPO DE RESIDUO' não é "(vazio)"
data = data[data['TIPO DE RESIDUO'] != '(vazio)']

# Filtrar dados onde a coluna 'TIPO DE RESIDUO' não é "(vazio)"
data = data[data['TIPO DE RESIDUO'] != '(vazio)']

# Ordenar o DataFrame com base no mês escolhido (exemplo: 'jan/13')
data_sorted = data.sort_values(by='jan', ascending=True)

# Função para formatar números grandes de maneira compacta (ex: 15,2t)
def formatar_numero(x):
    if x >= 1_000_000_000:
        return f'{x / 1_000_000_000:.0f}B'.replace('.', ',')  # Bilhões, sem casas decimais
    elif x >= 1_000_000:
        return f'{x / 1_000_000:.0f}M'.replace('.', ',')  # Milhões, sem casas decimais
    elif x >= 1_000:
        return f'{x / 1_000:.0f}K'.replace('.', ',')  # Milhares, sem casas decimais
    else:
        return f'{x:.0f}'.replace('.', ',')  # Menores que mil, sem casas decimais

# Gerar o gráfico com os dados ordenados
def gerar_grafico(mes):
    # (Tratamento de dados específico de 2021 permanece o mesmo)
    if mes not in data.columns:
        print(f"Mês '{mes}' não encontrado. Escolha entre: {data.columns[1:-1]}")
        return

    data[mes] = pd.to_numeric(data[mes], errors='coerce')
    data[mes].fillna(0, inplace=True)
    data_sorted = data.sort_values(by=mes, ascending=True)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(data_sorted['TIPO DE RESIDUO'], data_sorted[mes], color='#4E902B')
    plt.title(f'Resíduos por Tipo - {mes}')
    plt.xlabel('Tipos de Resíduo')
    plt.ylabel('Quantidade (toneladas)')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, formatar_numero(yval), ha='center', va='bottom', fontsize=10)

    plt.ylim(0, max(data_sorted[mes]) * 1.2)
    plt.xticks(rotation=45, ha='right')
    plt.gcf().set_facecolor('#D8E7CF')
    plt.tight_layout()

    # Retorna a figura para ser usada na API
    fig = plt.gcf()
    return fig