import streamlit as st
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import export_to_excel, import_from_excel
import sqlite3

init_db()
apply_styles()

st.title("🛡️ Gestão de Turnos 22:00-07:00")

# MENU DROPDOWN SUPERIOR
menu = st.selectbox("NAVEGAÇÃO", 
    ["Início", "Elementos: Novo/Editar", "Escalas: Gerar/Consultar", "Registo de Presenças", "Arquivo & Importação", "Configurações"],
    label_visibility="collapsed")

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- LÓGICA DE PÁGINAS ---

if menu == "Início":
    st.subheader("Resumo Operacional")
    df = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Efetivo", len(df))
    c2.metric("Serviços Realizados (Mês)", df['servicos'].sum())
    c3.metric("Taxa de Assiduidade", f"{100 - (df['faltas'].sum()):.1f}%")

elif menu == "Elementos: Novo/Editar":
    st.subheader("Gestão de Efetivos")
    df = get_stats()
    st.data_editor(df, use_container_width=True, hide_index=True)

elif menu == "Registo de Presenças":
    st.subheader("🔄 Registo de Execução")
    with st.form("registo"):
        col1, col2, col3 = st.columns(3)
        data = col1.date_input("Data")
        ni = col2.text_input("Nº Interno")
        tipo = col3.selectbox("Tipo", ["Serviço", "Falta"])
        if st.form_submit_button("Submeter"):
            conn = sqlite3.connect('gestao_operacional.db')
            conn.execute("INSERT INTO presencas (data_servico, num_interno, tipo) VALUES (?,?,?)",
                         (str(data), ni, tipo))
            conn.commit()
            conn.close()
            st.success("Registo efetuado.")

elif menu == "Arquivo & Importação":
    st.subheader("📥 Importar / Exportar Dados")
    
    col_exp, col_imp = st.columns(2)
    with col_exp:
        st.write("Exportar base de dados completa (inclui Serviços/Faltas)")
        excel_data = export_to_excel()
        st.download_button("Descarregar Excel", excel_data, "dados_operacionais.xlsx")
        
    with col_imp:
        st.write("Importar elementos via Excel")
        file = st.file_uploader("Selecione o ficheiro", type=['xlsx'])
        if file and st.button("Confirmar Importação"):
            s, m = import_from_excel(file)
            if s: st.success(m)
            else: st.error(m)

elif menu == "Configurações":
    st.subheader("Definições do Sistema")
    if st.button("🔄 Gerar 60 Elementos DEMO"):
        seed_demo_data()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
