import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db

col1, col2 = st.columns([1, 11], vertical_alignment="center")

with col1: 
    st.image("assets/tab.png")
with col2:
 st.title("Nova Movimentação")
 
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    tipo= st.radio(
        "Tipo *",
        options= ["Receita", "Despesa"],
        horizontal= True,
    )
    
categorias = db.listar_categorias(tipo= tipo)

with st.form("form_movimentacao", clear_on_submit= True):
    with col2:
        data_movimentacao= st.date_input("Data *", value=date.today())
        
    
