import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db

col1, col2 = st.columns([1, 11], vertical_alignment="center")

with col1: 
    st.image("assets/menu.png")
with col2:
 st.title("Gerenciamento de Categorias")