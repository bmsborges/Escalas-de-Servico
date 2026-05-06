import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Operacional de Escalas", layout="wide", page_icon="🚒")

# --- CSS CUSTOMIZADO (ASPECTO GRÁFICO) ---
def apply_theme():
    st.markdown("""
        <style>
        /* Estilo do Menu Lateral */
        [data-testid="stSidebar"] { background-color: #111827; }
        [data-testid="stSidebar"] * { color: #f3f4f6 !important; }
        
        /* Estilo dos Cards e Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { 
            height: 50px; white-space: pre-wrap; background-color: #f9fafb; 
            border-radius: 5px 5px 0 0; padding: 10px;
        }
        
        /* Botões */
        .stButton>button {
            border-radius: 6px; height: 3em; background-color: #2563eb; color: white;
            border: none; width: 100%; transition: 0.3s;
        }
        .stButton>button:hover { background-color: #1d4ed8; box-shadow: 0 4px 12px rgba(37,99,235,0.2); }
        </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE NAVEGAÇÃO ---
def main():
    apply_theme()
    
    # --- SIDEBAR ESTRUTURADO ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2306/2306221.png", width=60)
        st.title("Sistema de Escalas")
        st.markdown("---")
        
        # Categoria: Elementos
        with st.expander("👤 ELEMENTOS", expanded=True):
            sub_elementos = st.radio("Ações:", ["Novo", "Editar"], key="ele")
            
        # Categoria: Escalas
        with st.expander("📅 ESCALAS", expanded=True):
            sub_escalas = st.radio("Ações:", ["Gerar", "Consultar"], key="esc")
            
        # Categoria: Arquivo
        if st.button("📁 ARQUIVO HISTÓRICO"):
            st.session_state.menu = "Arquivo"
            
        st.markdown("---")
        # Categoria: Configuração
        with st.expander("⚙️ CONFIGURAÇÃO"):
            sub_config = st.radio("Opções:", ["Campos Elementos", "Constituição Equipas", "Aspecto Gráfico"], key="conf")

    # --- LÓGICA DE EXIBIÇÃO DE CONTEÚDO ---
    
    # Identificar qual o menu ativo (Este é um exemplo da estrutura)
    
    # 1. ELEMENTOS -> NOVO
    if "ele" in st.session_state and sub_elementos == "Novo":
        render_novo_elemento()
        
    # 2. ELEMENTOS -> EDITAR
    elif "ele" in st.session_state and sub_elementos == "Editar":
        st.header("👤 Editar Elementos Exatentes")
        st.info("Selecione um elemento da lista para modificar os dados.")
        # Tabela com botão de edição...

    # 3. ESCALAS -> GERAR
    elif "esc" in st.session_state and sub_escalas == "Gerar":
        render_gerar_escala()

    # 4. CONFIGURAÇÃO -> CONSTITUIÇÃO EQUIPAS
    elif "conf" in st.session_state and sub_config == "Constituição Equipas":
        st.header("🛠️ Definição de Regras da Equipa")
        col1, col2 = st.columns(2)
        col1.number_input("Mínimo de Chefes", value=1)
        col1.number_input("Mínimo de Motoristas Pesados", value=1)
        col2.number_input("Mínimo de Elementos TAS", value=1)
        col2.number_input("Total de Elementos por Turno", value=6)
        st.button("Atualizar Regras Operacionais")

# --- COMPONENTES DE INTERFACE ---

def render_novo_elemento():
    st.header("➕ Cadastrar Novo Elemento")
    with st.form("novo_elemento"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Profissional")
        num = c2.text_input("Número Interno")
        
        c3, c4, c5 = st.columns(3)
        posto = c3.selectbox("Posto", ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1"])
        mot = c4.selectbox("Tipo Motorista", ["Pesado", "Ligeiro", "N/A"])
        curso = c5.selectbox("Curso Principal", ["TAS", "TAT", "TS", "Nenhum"])
        
        st.markdown("### Disponibilidade Padrão")
        disp_tipo = st.radio("Tipo", ["Fixo (Semanal)", "Pontual (Datas Específicas)"], horizontal=True)
        
        if st.form_submit_button("💾 Guardar na Base de Dados"):
            st.success(f"Elemento {nome} adicionado com sucesso!")

def render_gerar_escala():
    st.header("📅 Gerar Nova Escala Mensal")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.date_input("Mês de Referência", value=datetime(2026, 6, 1))
        st.multiselect("Filtrar por Disponibilidade", ["Fixo", "Pontual"], default=["Fixo", "Pontual"])
        if st.button("🚀 Iniciar Algoritmo de Distribuição"):
            st.toast("A processar escala...")
    
    with col2:
        st.markdown("#### Pré-visualização")
        st.caption("A escala gerada aparecerá aqui para validação antes de ser arquivada.")

if __name__ == "__main__":
    main()
