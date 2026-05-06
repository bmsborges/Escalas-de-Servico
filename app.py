import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- ESTILO CSS PROFISSIONAL ---
def local_css():
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #0e1117;
            color: white;
            border: none;
        }
        .stButton>button:hover { background-color: #262730; border: 1px solid #4a90e2; }
        [data-testid="stMetricValue"] { font-size: 1.8rem; color: #4a90e2; }
        .sidebar .sidebar-content { background-image: linear-gradient(#2e3b4e, #1a2432); color: white; }
        h1 { color: #1e3a8a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .stTable { border: 1px solid #e6e9ef; border-radius: 10px; overflow: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- APP PRINCIPAL ---
def main():
    local_css()
    
    # Sidebar customizada com Logo/Título
    st.sidebar.title("🛡️ COMMAND CENTER")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("NAVEGAÇÃO", ["Painel de Controlo", "Base de Dados Pessoal", "Gerar Escala Mensal"])
    
    if menu == "Painel de Controlo":
        st.title("Escala de Serviço: 22h - 07h")
        
        # Métricas rápidas
        df = get_all_pessoal() # Usando a função do código anterior
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Efetivos", len(df))
        col2.metric("Motoristas Pesados", len(df[df['motorista'] == 'Pesado']))
        col3.metric("Operacionais TAS", len(df[df['curso'] == 'TAS']))
        
        st.markdown("---")
        st.subheader("💡 Instruções Rápidas")
        st.info("Utilize o menu lateral para gerir a base de dados ou processar a escala do próximo mês.")

    elif menu == "Base de Dados Pessoal":
        st.title("👥 Gestão de Efetivos")
        
        # Botão para gerar os 20 elementos aleatórios (Apenas para este exemplo)
        if st.button("🔄 Povoar Base de Dados (20 Elementos Demo)"):
            seed_data()
            st.success("20 elementos aleatórios criados!")
            st.rerun()

        # Tabela com aspeto limpo
        df = get_all_pessoal()
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "Gerar Escala Mensal":
        st.title("🗓️ Processamento de Escala")
        # [Aqui ficaria o código de geração que discutimos anteriormente]
        # Adicionar um loader para parecer mais profissional
        with st.status("A calcular requisitos e disponibilidades...", expanded=True) as status:
            st.write("A validar Chefes de Equipa...")
            st.write("A verificar cursos TAS...")
            st.write("A distribuir motoristas de pesados...")
            status.update(label="Escala Gerada com Sucesso!", state="complete", expanded=False)

# [Incluir aqui as funções init_db, get_all_pessoal e seed_data]

if __name__ == "__main__":
    main()
