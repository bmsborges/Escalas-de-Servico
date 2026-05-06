import streamlit as st
from datetime import datetime, date
import sqlite3
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal, export_to_excel

st.set_page_config(page_title="Gestão Operacional", layout="wide")
init_db()
apply_styles()

st.markdown("<h1 style='text-align: center;'>SISTEMA OPERACIONAL</h1>", unsafe_allow_html=True)

menu = st.selectbox("NAVEGAÇÃO", 
    ["🏠 Dashboard", "👤 Elementos", "📅 Escalas", "🔄 Presenças", "📥 Arquivo", "⚙️ Configuração"],
    label_visibility="collapsed")

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if menu == "🏠 Dashboard":
    df = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos", len(df))
    c2.metric("Serviços", df['servicos'].sum())
    c3.metric("Faltas", df['faltas'].sum())

elif menu == "👤 Elementos":
    aba1, aba2 = st.tabs(["Lista", "Novo"])
    with aba1:
        st.data_editor(get_stats(), use_container_width=True, hide_index=True)
    with aba2:
        with st.form("novo"):
            n = st.text_input("Nome")
            ni = st.text_input("Nº Interno")
            pst = st.selectbox("Posto", ["Est", "B1", "B2", "B3", "SCH", "CHF"])
            mot = st.radio("Motorista", ["Ligeiro", "Pesado"], horizontal=True)
            crs = st.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
            tipo_d = st.radio("Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            
            if tipo_d == "Fixo":
                det = st.multiselect("Dias Semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
                detalhe_final = ", ".join(det)
            else:
                # Este é o bloco que faz aparecer o calendário
                datas = st.date_input("Selecione os dias no calendário", value=[],  # Isto obriga a versão múltipla format="DD/MM/YYYY")
                detalhe_final = ", ".join([str(d) for d in datas])

            if st.form_submit_button("GUARDAR"):
                conn = sqlite3.connect('gestao_operacional.db')
                conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                             (n, ni, pst, mot, crs, tipo_d, detalhe_final))
                conn.commit()
                conn.close()
                st.success("Registo efetuado.")

elif menu == "📅 Escalas":
    c_m, c_a = st.columns(2)
    m = c_m.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    a = c_a.number_input("Ano", value=2026)
    if st.button("🚀 GERAR ESCALA"):
        df_esc, msg = gerar_escala_mensal(m, a)
        if df_esc is not None:
            st.table(df_esc)
            st.download_button("Exportar CSV", df_esc.to_csv(index=False).encode('utf-8'), "escala.csv")
        else: st.error(msg)

elif menu == "🔄 Presenças":
    with st.form("pres"):
        d = st.date_input("Data")
        num = st.text_input("Nº Interno")
        t = st.selectbox("Tipo", ["Serviço", "Falta"])
        if st.form_submit_button("REGISTAR"):
            conn = sqlite3.connect('gestao_operacional.db')
            conn.execute("INSERT INTO presencas (data_servico, num_interno, tipo) VALUES (?,?,?)", (str(d), num, t))
            conn.commit()
            conn.close()
            st.success("Ok.")

elif menu == "⚙️ Configuração":
    if st.button("🔄 POVOAR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.success("Povoado.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
