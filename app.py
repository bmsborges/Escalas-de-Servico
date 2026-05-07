import streamlit as st
from datetime import datetime, date
import sqlite3
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal

# 1. Configurações e Inicialização de Estado
st.set_page_config(page_title="Ops Manager", layout="wide")
init_db()
apply_styles()

if 'calendario_visivel' not in st.session_state:
    st.session_state.calendario_visivel = False

# --- TOPO ESTILO APP ---
st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h2 style='margin:0;'>🛡️ COMMAND CENTER</h2>
        <p style='color: #6B7280; font-size: 0.9rem;'>Gestão de Efetivos e Escalas</p>
    </div>
""", unsafe_allow_html=True)

menu = st.selectbox("MENU", ["🏠 Dashboard", "👤 Elementos", "📅 Escalas", "⚙️ Configuração"], label_visibility="collapsed")

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if menu == "🏠 Dashboard":
    df = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos", len(df))
    c2.metric("Serviços", df['servicos'].sum())
    c3.metric("Faltas", df['faltas'].sum())

elif menu == "👤 Elementos":
    aba1, aba2 = st.tabs(["📋 Lista de Efetivos", "➕ Novo Registo"])
    
    with aba1:
        st.data_editor(get_stats(), use_container_width=True, hide_index=True)
    
    with aba2:
        # Campos básicos
        n = st.text_input("Nome")
        ni = st.text_input("Nº Interno")
        
        col_a, col_b = st.columns(2)
        pst = col_a.selectbox("Posto", ["B1", "B2", "SCH", "CHF", "CMD"])
        crs = col_b.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
        mot = st.radio("Motorista", ["Ligeiro", "Pesado"], horizontal=True)
        
        st.markdown("---")
        st.write("📅 **Disponibilidade**")
        tipo_d = st.radio("Tipo de Escala", ["Fixo", "Pontual"], horizontal=True)
        
        detalhe_final = ""

        if tipo_d == "Fixo":
            d_fixos = st.multiselect("Dias da Semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
            detalhe_final = ", ".join(d_fixos)
        
        else:
            # No ficheiro app.py, dentro da lógica de disponibilidade "Pontual"
        if tipo_d == "Pontual":
            # O uso de value=() ativa a seleção múltipla de datas individuais
            datas_selecionadas = st.date_input(
                "Selecione os dias (pode clicar em 1 ou em vários dias isolados):",
                value=(), 
                format="DD/MM/YYYY",
                help="Cada clique num dia adiciona-o à lista. Clique novamente para remover."
            )
        
            if datas_selecionadas:
                # Exibe as datas selecionadas para confirmação do utilizador
                st.write(f"📅 **Datas Escolhidas:** {len(datas_selecionadas)}")
                
                # Converte a lista de objetos 'date' para a string formatada guardada na BD
                # Exemplo: "2026-05-10, 2026-05-15, 2026-05-16"
                detalhe_final = ", ".join([d.strftime("%Y-%m-%d") for d in datas_selecionadas])
                st.markdown("---")
                # Botão final de guardar (Este sim, processa tudo)
        if st.button("💾 GUARDAR OPERACIONAL"):
            if n and ni and detalhe_final:
                conn = sqlite3.connect('gestao_operacional.db')
                try:
                    conn.execute("""
                        INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) 
                        VALUES (?,?,?,?,?,?,?)""",
                        (n, ni, pst, mot, crs, tipo_d, detalhe_final))[cite: 1]
                    conn.commit()
                    st.success(f"Sucesso! {n} registado.")
                    st.session_state.calendario_visivel = False
                except:
                    st.error("Erro: Número interno já existe.")
                finally:
                    conn.close()
            else:
                st.warning("Preencha todos os campos e selecione os dias.")

elif menu == "📅 Escalas":
    # Lógica de geração de escala (conforme os requisitos de Chefe, Pesado e TAS)
    c1, c2 = st.columns(2)
    m = c1.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    a = c2.number_input("Ano", value=2026)
    if st.button("🚀 GERAR ESCALA MENSAL"):
        df_esc, msg = gerar_escala_mensal(m, a)
        if df_esc is not None:
            st.table(df_esc)[cite: 1]

elif menu == "⚙️ Configuração":
    if st.button("🔄 REPOR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
