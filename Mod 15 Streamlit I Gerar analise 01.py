import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

sns.set_theme()

# Função para filtrar valores não numéricos
def convert_to_numeric(series):
    return pd.to_numeric(series, errors='coerce')

# Função para plotar tabelas pivot
def plota_pivot_table(df, value, index, func, ylabel, xlabel, opcao='nada'):
    fig, ax = plt.subplots(figsize=[15, 5])
    
    # Convertendo para numérico se necessário
    df[value] = convert_to_numeric(df[value])
    
    pivot = pd.pivot_table(df, values=value, index=index, aggfunc=func)
    
    if opcao == 'sort':
        pivot = pivot.sort_values(value)
    elif opcao == 'unstack':
        pivot = pivot.unstack()

    pivot.plot(ax=ax)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    st.pyplot(fig)

# Configurações iniciais da página
st.set_page_config(page_title='SINASC RONDÔNIA', 
                   page_icon='https://upload.wikimedia.org/wikipedia/commons/e/ea/Flag_map_of_Rondonia.png',
                   layout='wide')

# Adicionando barra de progresso no início da página
st.markdown("### Progresso do Carregamento")
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)

# Título e descrição
st.title("Análise dos Dados do SINASC em Rondônia - 2019")
st.markdown("""
Esta aplicação permite que você explore e visualize dados de nascimentos ocorridos no estado de Rondônia em 2019.
Use os filtros laterais para ajustar as visualizações e os gráficos de acordo com suas necessidades.
""")

# Carregamento dos dados
st.sidebar.markdown("### Carregue os dados")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    sinasc = pd.read_csv(uploaded_file)
else:
    st.warning("Por favor, carregue um arquivo CSV.")
    st.stop()

# Convertendo a coluna de datas
sinasc['DTNASC'] = pd.to_datetime(sinasc['DTNASC'])

# Exibir os dados brutos
if st.checkbox('Mostrar dados brutos'):
    st.subheader('Dados Brutos')
    st.dataframe(sinasc)

# Intervalo de datas
min_data = sinasc['DTNASC'].min()
max_data = sinasc['DTNASC'].max()

data_inicial = st.sidebar.date_input('Data inicial', value=min_data, min_value=min_data, max_value=max_data)
data_final = st.sidebar.date_input('Data final', value=max_data, min_value=min_data, max_value=max_data)

# Filtrando os dados por data
sinasc = sinasc[(sinasc['DTNASC'] >= pd.to_datetime(data_inicial)) & (sinasc['DTNASC'] <= pd.to_datetime(data_final))]

# Seletor de tipo de gráfico
st.sidebar.markdown("### Selecione o tipo de gráfico")
tipo_grafico = st.sidebar.selectbox("Escolha o tipo de gráfico", ["Quantidade de Nascimentos", "Média da Idade da Mãe", "Média do Peso do Bebê", "Peso Mediano", "Média do APGAR1", "Média do APGAR5"])

# Gráficos
st.markdown("### Gráficos de Análise")

if tipo_grafico == "Quantidade de Nascimentos":
    plota_pivot_table(sinasc, 'IDADEMAE', 'DTNASC', 'count', 'Quantidade de Nascimentos', 'Data de Nascimento')
elif tipo_grafico == "Média da Idade da Mãe":
    plota_pivot_table(sinasc, 'IDADEMAE', ['DTNASC', 'SEXO'], 'mean', 'Média da Idade da Mãe', 'Data de Nascimento', 'unstack')
elif tipo_grafico == "Média do Peso do Bebê":
    plota_pivot_table(sinasc, 'PESO', ['DTNASC', 'SEXO'], 'mean', 'Média do Peso do Bebê', 'Data de Nascimento', 'unstack')
elif tipo_grafico == "Peso Mediano":
    plota_pivot_table(sinasc, 'PESO', 'ESCMAE', 'median', 'Peso Mediano', 'Escolaridade da Mãe', 'sort')
elif tipo_grafico == "Média do APGAR1":
    plota_pivot_table(sinasc, 'APGAR1', 'GESTACAO', 'mean', 'Média do APGAR1', 'Tipo de Gestação', 'sort')
elif tipo_grafico == "Média do APGAR5":
    plota_pivot_table(sinasc, 'APGAR5', 'GESTACAO', 'mean', 'Média do APGAR5', 'Tipo de Gestação', 'sort')

# Gráfico de dispersão (scatter plot)
st.markdown("### Gráfico de Dispersão")
fig, ax = plt.subplots()
sns.scatterplot(data=sinasc, x='IDADEMAE', y='PESO', hue='SEXO', ax=ax)
st.pyplot(fig)

# Expansores
with st.expander("Ver Código"):
    st.code("""
    def plota_pivot_table(df, value, index, func, ylabel, xlabel, opcao='nada'):
        fig, ax = plt.subplots(figsize=[15, 5])
        pivot = pd.pivot_table(df, values=value, index=index, aggfunc=func)
        
        if opcao == 'sort':
            pivot = pivot.sort_values(value)
        elif opcao == 'unstack':
            pivot = pivot.unstack()

        pivot.plot(ax=ax)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        st.pyplot(fig)
    """, language='python')

# Download dos dados processados
st.markdown("### Baixe os Dados Processados")
csv = sinasc.to_csv(index=False)
st.download_button(label="Download dos Dados Filtrados", data=csv, file_name='sinasc_filtrado.csv', mime='text/csv')

# Imagem ilustrativa
st.markdown("### Imagem Relacionada")
st.image('https://upload.wikimedia.org/wikipedia/commons/e/ea/Flag_map_of_Rondonia.png', caption='Mapa de Rondônia')