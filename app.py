import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db

st.set_page_config(
    page_title = 'CF Finanças Pessoais',
    page_icon = "assets/money-management.png",
    layout = 'wide',
    initial_sidebar_state = 'expanded'
)

db.inicializar_banco()

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# NAVEGAÇÃO LOCAL - SIDEBAR
# =================================================================================

st.logo(image="assets/cffinance.png", size="large")

page_dashboard = st.Page(
    page="views/dashboard.py",
    title= "Dashboard (Relatórios)",
    icon= ":material/bar_chart:",
    default=True,
)

page_new_transition = st.Page(
    page="views/transitions.py",
    title= "Nova Movimentação",
    icon= ":material/add_box:"  
)

page_transitions_historic = st.Page(
    page="views/history.py",
    title= "Histórico de Movimentações",
    icon= ":material/monitoring:"  
)

page_categories_manager = st.Page(
    page="views/categories.py",
    title= "Gerenciamento de Categorias",
    icon= ":material/category:"  
)
pg = st.navigation(pages=[page_dashboard, page_new_transition, page_transitions_historic, page_categories_manager])

st.sidebar.caption("*Sistema de Gestão Financeira Pessoal*")
pg.run()




