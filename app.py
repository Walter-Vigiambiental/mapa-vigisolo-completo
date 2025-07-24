import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import calendar

st.set_page_config(page_title="Mapa VIGISOLO", layout="wide")
st.title("📍 Mapa Interativo do VIGISOLO")

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4rNqe1-YHIaKxLgyEbhN0tNytQixaNJnVfcyI0PN6ajT0KXzIGlh_dBrWFs6R9QqCEJ_UTGp3KOmL/pub?gid=317759421&single=true&output=csv"

@st.cache_data(ttl=600)
def carregar_dados():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.lower()
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    return df

df = carregar_dados()

st.sidebar.header("Filtros")

anos = sorted(df['ano'].dropna().unique())
ano_selecionado = st.sidebar.selectbox("Ano", options=["Todos"] + anos, index=0)

meses_numeros = sorted([int(m) for m in df['mes'].dropna().unique() if 1 <= int(m) <= 12])
meses_nome = {num: calendar.month_abbr[num].capitalize() for num in meses_numeros}
mes_nome_opcoes = ["Todos"] + list(meses_nome.values())
mes_nome_selecionado = st.sidebar.selectbox("Mês", options=mes_nome_opcoes, index=0)

bairros_disponiveis = sorted(df['bairro'].dropna().unique())
bairro_selecionado = st.sidebar.multiselect("Bairro", options=bairros_disponiveis)

# Diagnóstico - Mostrar dados e opções disponíveis
st.sidebar.write("Anos disponíveis:", anos)
st.sidebar.write("Meses disponíveis:", meses_nome)
st.sidebar.write("Bairros disponíveis:", bairros_disponiveis)

st.write(f"Total de dados originais: {len(df)}")

df_filtrado = df.copy()

if ano_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['ano'] == ano_selecionado]

if mes_nome_selecionado != "Todos":
    mes_num = list(meses_nome.keys())[list(meses_nome.values()).index(mes_nome_selecionado)]
    df_filtrado = df_filtrado[df_filtrado['mes'] == mes_num]

if bairro_selecionado:
    df_filtrado = df_filtrado[df_filtrado['bairro'].isin(bairro_selecionado)]

# Remove dados sem latitude/longitude válidos
df_filtrado = df_filtrado.dropna(subset=['latitude', 'longitude'])

st.write(f"Total de dados após filtro: {len(df_filtrado)}")

if not df_filtrado.empty:
    m = folium.Map(location=[df_filtrado['latitude'].mean(), df_filtrado['longitude'].mean()], zoom_start=10)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtrado.iterrows():
        popup = f"""
        <b>Bairro:</b> {row['bairro']}<br>
        <b>Data:</b> {row['data'].date()}<br>
        <b>Tipo de Solo:</b> {row.get('tipo de solo', 'N/A')}<br>
        <b>Latitude:</b> {row['latitude']}<br>
        <b>Longitude:</b> {row['longitude']}
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup, max_width=300),
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(marker_cluster)

    folium_static(m, width=1200, height=700)
else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
