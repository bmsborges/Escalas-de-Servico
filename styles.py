import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/gill-sans-mt');
        
        /* Configuração Global */
        html, body, [class*="css"] {
            font-family: 'Gill Sans MT', sans-serif !important;
            background-color: #F0F2F5; /* Cinza claro de fundo */
            color: #1F2937;
        }

        /* Container Principal (Efeito de App Móvel/Card) */
        .block-container {
            padding: 2rem 1rem !important;
            max-width: 800px !important; /* Estreitar para parecer uma app */
        }

        /* Estilo dos Cartões (Cards) */
        .main-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 24px; /* Cantos bem arredondados como na imagem */
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: none;
        }

        /* Menu Dropdown Estilizado */
        div[data-baseweb="select"] {
            border-radius: 16px !important;
            border: 2px solid #E5E7EB !important;
            background-color: #FFFFFF !important;
            padding: 4px;
        }

        /* Botões Estilo Taxi App (Arredondados e Vibrantes) */
        .stButton>button {
            border-radius: 16px !important;
            background-color: #1F2937 !important; /* Escuro Profissional */
            color: #FFFFFF !important;
            font-weight: 600 !important;
            height: 54px !important;
            border: none !important;
            width: 100% !important;
            transition: transform 0.2s;
        }
        
        .stButton>button:hover {
            transform: scale(1.02);
            background-color: #374151 !important;
        }

        /* Inputs e Calendário */
        input {
            border-radius: 12px !important;
            border: 1px solid #D1D5DB !important;
            padding: 12px !important;
        }

        /* Badges e Status */
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            background-color: #E5E7EB;
        }
        </style>
    """, unsafe_allow_html=True)
