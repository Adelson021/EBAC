# Imports
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

# Configuração de tema personalizado do Seaborn para melhorar a estética dos gráficos
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para carregar dados com cache
@st.cache_data
def load_data(file_data):
    try:
        # Tenta carregar arquivo CSV
        data = pd.read_csv(file_data, sep=';')
        st.write('Arquivo CSV carregado com sucesso!')
        return data
    except:
        try:
            # Tenta carregar arquivo Excel
            data = pd.read_excel(file_data)
            st.write('Arquivo Excel carregado com sucesso!')
            return data
        except:
            # Exibe erro se falhar
            st.error('Erro ao carregar o arquivo.')
            return pd.DataFrame()

# Função para aplicar filtro com base em seleção múltipla
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter DataFrame para CSV
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter DataFrame para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Função para criar botão de download
def create_download_button(data, col, title, file_name):
    df_xlsx = to_excel(data)
    col.write(f'### {title}')
    col.write(data)
    col.download_button(label=f'📥 Download {title}',
                        data=df_xlsx,
                        file_name=file_name)

# Função para desenhar os gráficos de barra ou pizza
def plot_graphs(data, ax, graph_type, title):
    if graph_type == 'Barras':
        # Adiciona a paleta de cores personalizada para as barras
        bar_plot = sns.barplot(x=data.index, y=data['proportion'], palette="muted", ax=ax)
        # Adiciona os valores em cima de cada barra
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f%%')
    else:
        data.plot(kind='pie', autopct='%.2f%%', y='proportion', ax=ax)
    ax.set_title(title, fontweight="bold")

# Função principal da aplicação
def main():
    # Configuração da página com título e layout
    st.set_page_config(page_title='Telemarketing Analysis', layout="wide")
    st.write('# Telemarketing Analysis')
    st.markdown("---")

    # Tentativa de carregar imagem na barra lateral
    try:
        image = Image.open("../img/Bank-Branding.jpg")
        st.sidebar.image(image)
    except Exception as e:
        st.error(f'Erro ao carregar imagem: {e}')

    # Botão para carregar arquivo na barra lateral
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Se o arquivo for carregado, inicia a análise
    if data_file_1:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())  # Exibe os primeiros dados antes de aplicar os filtros

        # Criação de formulário na barra lateral para selecionar filtros
        with st.sidebar.form(key='my_form'):
            # Seleção do tipo de gráfico
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            # Filtro por idade
            if 'age' in bank.columns:
                max_age = int(bank.age.max())
                min_age = int(bank.age.min())
                idades = st.slider(label='Idade', 
                                   min_value=min_age, 
                                   max_value=max_age, 
                                   value=(min_age, max_age), 
                                   step=1)
            else:
                st.error('Coluna "age" não encontrada.')

            # Filtro por profissão
            jobs_list = bank.job.unique().tolist() + ['all']
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

            # Filtro por estado civil
            marital_list = bank.marital.unique().tolist() + ['all']
            marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

            # Filtro por default
            default_list = bank.default.unique().tolist() + ['all']
            default_selected = st.multiselect("Default", default_list, ['all'])

            # Filtro por financiamento imobiliário
            housing_list = bank.housing.unique().tolist() + ['all']
            housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # Filtro por empréstimo
            loan_list = bank.loan.unique().tolist() + ['all']
            loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

            # Filtro por meio de contato
            contact_list = bank.contact.unique().tolist() + ['all']
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # Filtro por mês do contato
            month_list = bank.month.unique().tolist() + ['all']
            month_selected = st.multiselect("Mês do contato", month_list, ['all'])

            # Filtro por dia da semana
            day_of_week_list = bank.day_of_week.unique().tolist() + ['all']
            day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # Aplicação dos filtros encadeados
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )

            submit_button = st.form_submit_button(label='Aplicar')

        # Exibe dados após a aplicação dos filtros
        st.write('## Após os filtros')
        st.write(bank.head())

        # Botão de download para os dados filtrados
        create_download_button(bank, st, 'Tabela Filtrada', 'bank_filtered.xlsx')
        st.markdown("---")

        # Geração de gráficos
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))  # Tamanho maior para melhor visualização

        # Cálculo das proporções dos dados brutos e filtrados
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame(name='proportion') * 100
        bank_target_perc = bank.y.value_counts(normalize=True).to_frame(name='proportion') * 100

        # Botões de download para as proporções
        col1, col2 = st.columns(2)
        create_download_button(bank_raw_target_perc, col1, 'Proporção original', 'bank_raw_y.xlsx')
        create_download_button(bank_target_perc, col2, 'Proporção filtrada', 'bank_y.xlsx')

        st.write('## Proporção de aceite')

        # Desenho dos gráficos (barras ou pizza)
        plot_graphs(bank_raw_target_perc, ax[0], graph_type, 'Dados brutos')
        plot_graphs(bank_target_perc, ax[1], graph_type, 'Dados filtrados')

        # Exibe os gráficos
        st.pyplot(plt)

if __name__ == '__main__':
    main()