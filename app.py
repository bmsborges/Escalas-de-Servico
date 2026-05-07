import streamlit as st
from datetime import datetime, date
import sqlite3
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal

# Inicialização
st.set_page_config(page_title="Ops Manager", layout="centered") # Centrado para look mobile
init_db()
apply_styles()

# Área de Perfil/Topo (Simulando App Taxi)
st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
        <div>
            <p style='margin:0; color: #6B7280; font-size: 0.9rem;'>Bom dia,</p>
            <h2 style='margin:0; font-weight: 800;'>Comando Operacional</h2>
        </div>
        <div style='width: 45px; height: 45px; background: #1F2937; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white;'>
            CO
        </div>
    </div>
""", unsafe_allow_html=True)

# Navegação Centralizada (Dropdown Minimalista)
opcoes = ["🏠 Início", "👤 Gestão de Efetivos", "📅 Gerar Escala", "🔄 Trocas & Faltas", "⚙️ Configurações"]
menu = st.selectbox("Escolha o módulo", opcoes, label_visibility="collapsed")

# --- CONTEÚDO DENTRO DE CARDS ---

if "Início" in menu:
    df = get_stats()
    st.markdown(f"""
        <div class='main-card'>
            <p style='color: #6B7280; margin-bottom: 5px;'>Efetivos Ativos</p>
            <h1 style='margin:0;'>{len(df)} <span style='font-size: 1rem; color: #10B981;'>● Online</span></h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='main-card' style='text-align: center;'><h4>Turnos</h4><h2>124</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='main-card' style='text-align: center;'><h4>Faltas</h4><h2 style='color: #EF4444;'>2</h2></div>", unsafe_allow_html=True)

elif "Efetivos" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Registo de Pessoal")
    # Baseado na estrutura do template
    aba1, aba2 = st.tabs(["Lista", "Novo"])

st.markdown("---")
st.write("📅 **Disponibilidade Operacional**")

# Layout em colunas para colocar o botão à frente das opções
col_opcoes, col_botao = st.columns([2, 1])

with col_opcoes:
    # Seleção do tipo de disponibilidade
    tipo_d = st.radio("Tipo de Escala", ["Fixo", "Pontual"], horizontal=True, label_visibility="collapsed")

detalhe_final = ""

if tipo_d == "Fixo":
    # Campo para disponibilidade fixa semanal
    dias_fixos = st.multiselect("Selecione os dias da semana:", 
                                ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
    detalhe_final = ", ".join(dias_fixos)

elif tipo_d == "Pontual":
    with col_botao:
        # Botão que aparece apenas quando "Pontual" é selecionado
        if st.button("📅 Abrir Calendário"):
            st.session_state.mostrar_calendario = True

    # Se o botão for clicado, o widget de data aparece
    if st.session_state.get('mostrar_calendario', False):
        st.markdown("<div style='padding: 10px; background: #f9fafb; border-radius: 12px; border: 1px dashed #d1d5db;'>", unsafe_allow_html=True)
        
        # Widget de data para seleção múltipla de dias específicos[cite: 1]
        datas_selecionadas = st.date_input(
            "Selecione os dias de serviço:",
            value=(), 
            format="DD/MM/YYYY",
            help="Pode selecionar vários dias individuais clicando neles."
        )
        
        if datas_selecionadas:
            # Armazenar detalhe da disponibilidade conforme o formato do sistema[cite: 1]
            detalhe_final = ", ".join([d.strftime("%Y-%m-%d") for d in datas_selecionadas])
        
        st.markdown("</div>", unsafe_allow_html=True)

# O botão de submissão do formulário utiliza os dados recolhidos
if st.form_submit_button("REGISTAR ELEMENTO"):
    if nome and num_interno and detalhe_final: # Verificação de campos obrigatórios[cite: 1]
        # Lógica de gravação na base de dados...
        st.success(f"Registo de {nome} (ID: {num_interno}) concluído com sucesso!")
        st.session_state.mostrar_calendario = False # Reset do calendário após sucesso
    else:
        st.warning("Por favor, preencha todos os dados e selecione as datas.")
             if st.form_submit_button("💾 GUARDAR ELEMENTO"):
                if nome and num and detalhe_final:
                    conn = sqlite3.connect('gestao_operacional.db')
                    try:
                        conn.execute("""INSERT INTO pessoal 
                                     (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) 
                                     VALUES (?,?,?,?,?,?,?)""",
                                     (nome, num, posto, mot, curso, tipo_d, detalhe_final))
                        conn.commit()
                        st.success(f"Elemento {nome} guardado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: Verifique se o Nº Interno já existe. ({e})")
                    finally:
                        conn.close()
                else:
                    st.warning("Preencha todos os campos e selecione os dias no calendário.")    
   
elif "Gerar Escala" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Planear Próximo Mês")
    m = st.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    a = st.number_input("Ano", value=2026)
    
    if st.button("🚀 GERAR ESCALA AGORA"):
        df_esc, msg = gerar_escala_mensal(m, a)
        if df_esc is not None:
            st.table(df_esc)
        else:
            st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

elif "Configurações" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.write("Ações de Administrador")
    if st.button("🔄 REPOR DADOS DEMO (60 ELEM)"):
        seed_demo_data()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>Ops Manager v3.0 • 2026</p>", unsafe_allow_html=True)
