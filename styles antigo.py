import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/gill-sans-mt');
        
        html, body, [class*="css"] {
            font-family: 'Gill Sans MT', sans-serif !important;
            background-color: #F8F9FA;
            color: #333333;
        }

        /* Menu Dropdown Superior */
        .stSelectbox div[data-baseweb="select"] {
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            background-color: white;
        }

        .main-card {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Estilo para st.table (Escala) */
        .stTable td {
            white-space: pre-wrap !important;
            font-size: 0.85rem !important;
            vertical-align: top !important;
            padding: 10px !important;
        }
        
        .stButton>button {
            border-radius: 4px;
            background-color: #4B5563;
            color: white;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
