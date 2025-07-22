
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime
import calendar
import relatorio_pdf

st.set_page_config(layout="wide")
st.title("🌱 Painel Interativo - VigiSolo")

# Carregar dados
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4rNqe1-YHIaKxLgyEbhN0tNytQixaNJnVfcyI0PN6ajT0KXzIGlh_dBrWFs6R9QqCEJ_UTGp3KOmL/pub?gid=317759421&single=true&output=csv"
df = pd.read_csv(url)

# Ajuste de datas e colunas
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Data', 'Latitude', 'Longitude'])
df['Ano'] = df['Data'].dt.year
df['Mes'] = df['Data'].dt.month
df['MesNome'] = df['Mes'].apply(lambda x: calendar.month_abbr[int(x)].capitalize())

# Filtros
st.sidebar.title("🔍 Filtros")
ano_sel = st.sidebar.selectbox("Ano", ["Todos"] + sorted(df['Ano'].dropna().unique().astype(str)))
mes_sel = st.sidebar.selectbox("Mês", ["Todos"] + list(calendar.month_abbr[1:]))
mun_sel = st.sidebar.selectbox("Município", ["Todos"] + sorted(df['Município'].dropna().unique()))
solo_sel = st.sidebar.selectbox("Tipo de Solo", ["Todos"] + sorted(df['Tipo Solo'].dropna().unique()))

# Aplicar filtros
df_filt = df.copy()
if ano_sel != "Todos":
    df_filt = df_filt[df_filt['Ano'] == int(ano_sel)]
if mes_sel != "Todos":
    df_filt = df_filt[df_filt['MesNome'] == mes_sel]
if mun_sel != "Todos":
    df_filt = df_filt[df_filt['Município'] == mun_sel]
if solo_sel != "Todos":
    df_filt = df_filt[df_filt['Tipo Solo'] == solo_sel]

# Mapa
m = folium.Map(location=[-7.2, -44.2], zoom_start=6)
cluster = MarkerCluster().add_to(m)
for _, row in df_filt.iterrows():
    popup = f"<b>Localidade:</b> {row['Localidade']}<br><b>Município:</b> {row['Município']}<br>"
    popup += f"<b>Solo:</b> {row['Tipo Solo']}<br><b>Data:</b> {row['Data'].strftime('%d/%m/%Y')}<br>"
    popup += f"<b>Coordenadas:</b> ({row['Latitude']}, {row['Longitude']})"
    folium.Marker([row['Latitude'], row['Longitude']], popup=popup).add_to(cluster)

with st.container():
    st.markdown("### 🗺️ Mapa de Coletas com Cluster")
    st_folium(m, height=600, width=1000)

# Gráfico por localidade
st.markdown("### 📊 Coletas por Localidade")
st.bar_chart(df_filt['Localidade'].value_counts())

# Botão para gerar relatório
if st.button("📄 Gerar Relatório PDF"):
    caminho = relatorio_pdf.gerar_pdf_resumo(df_filt)
    with open(caminho, "rb") as f:
        st.download_button("📥 Baixar PDF", f, file_name="relatorio_vigisolo.pdf")
