from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from fpdf import FPDF
from datetime import date
import tempfile

secrets = st.secrets["postgres"]
engine = create_engine(
    f"postgresql://{secrets.user}:{secrets.password}@{secrets.host}:{secrets.port}/{secrets.database}"
)

df = pd.read_sql("SELECT * FROM editor02.combates_2024", engine)
df.to_csv("dados/combates_2024.csv", index=False)


st.title("Reporte de Incêndios Florestais")

tab1, tab2 = st.tabs([
    "Frentes de Combate",
    "ROI"
    # "Queima Prescrita",
    # "Queima Controlada",
    # "Ações Educativas
])

with tab1:
    st.header("Frentes de Combate")
    regioes = df['regiao_ibge'].dropna().unique()
    opcoes_regiao = ['Selecione uma região'] + list(regioes)
    regiao = st.selectbox('REGIÕES', options=opcoes_regiao)


    if regiao == 'Selecione uma região':
        df_regiao = df
        st.subheader("Brasil")
    else:
        df_regiao = df[df['regiao_ibge'] == regiao] 

    total_sem_combate = df_regiao[df_regiao['satatus'] == 'sem combate'].shape[0]
    total_extinto = df_regiao[df_regiao['satatus'] == 'extinto'].shape[0]
    total_combate = df_regiao[df_regiao['satatus'] == 'em combate'].shape[0]
    total_controlado = df_regiao[df_regiao['satatus'] == 'controlado'].shape[0]

    status_esperados = ['sem combate', 'em combate', 'controlado', 'extinto']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sem Combate", total_sem_combate)
    with col2: 
        st.metric("Em Combate", total_combate)
    with col3: 
        st.metric("Controlado", total_controlado)
    with col4: 
        st.metric("Extinto", total_extinto)

    tabela_municipios = (
        df_regiao
        .groupby(['municipio_ibge', 'satatus'])
        .size()
        .reset_index(name='Quantidade')
        .pivot(index='municipio_ibge', columns='satatus', values='Quantidade')
        .reindex(columns=status_esperados, fill_value=0)
        .astype(int)
        .reset_index()
        .sort_values(by='extinto', ascending=False)
    )

    tabela_municipios = tabela_municipios.rename(columns={
    'municipio_ibge': 'Município',
    'sem combate': 'Sem Combate',
    'em combate': 'Em Combate',
    'controlado': 'Controlado',
    'extinto': 'Extinto'
    })

    st.dataframe(tabela_municipios, use_container_width=True, hide_index=True)


tabela = tabela_municipios.copy()
tabela.reset_index(drop=True, inplace=True)









# Cria PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, "Relatório de Frentes de Combate", ln=True, align="C")

pdf.set_font("Arial", '', 10)
pdf.cell(0, 10, f"Data: {date.today().strftime('%d/%m/%Y')}", ln=True)

# Espaço
pdf.ln(5)

# Cabeçalhos da tabela
pdf.set_font("Arial", 'B', 9)
for col in tabela.columns:
    pdf.cell(30, 8, str(col), border=1)
pdf.ln()

# Dados
pdf.set_font("Arial", '', 9)
for index, row in tabela.iterrows():
    for col in tabela.columns:
        pdf.cell(30, 8, str(row[col]), border=1)
    pdf.ln()

# Salva em arquivo temporário
tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
pdf.output(tmp_path)

# Download no Streamlit
with open(tmp_path, "rb") as file:
    st.download_button(
        label="📄 Baixar PDF do Relatório",
        data=file,
        file_name=f"relatorio_frentes_combate_{date.today()}.pdf",
        mime="application/pdf"
    )