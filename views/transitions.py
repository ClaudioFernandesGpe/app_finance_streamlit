import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db
from utilitarios import formatar_brl

col1, col2 = st.columns([1, 11], vertical_alignment="center")

with col1: 
    st.image("assets/tab.png")
with col2:
 st.title("Nova Movimentação")
 
st.markdown("---")



col1, col2 = st.columns(2, gap= "large", vertical_alignment="center")

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
        
    opcoes_cat= {c["nome"]: c["id"] for c in categorias}


    if opcoes_cat:
        categoria_nome = st.selectbox("Categoria *", options= list(opcoes_cat.keys()))
    else:
        st.warning("nenhuma categoria disponível para este tipo. Adicione em **:material/category: Gerenciar Categorias**")
        categoria_nome = None
            
    descricao= st.text_input("Descrição *", placeholder= "Compras supermercado")
        
    valor= st.number_input(
            "Valor *",
            min_value= 0.01,
            format= "%.2f",
            placeholder= "0.00"
        )
        

    salvar= st.form_submit_button(":material/file_save: Salvar Movimentação", width= "content")
    
    if salvar:
        erros= []
        
        if not descricao.strip():
            erros.append("O campo descrição deve ser preenchido.")
        if not categoria_nome:
            erros.append("Selecione uma categoria válida.")
        if not valor or valor <= 0:
            erros.append("O valor deve ser preenchido com um valor maior que zero.")
            
        if erros:
            for e in erros:
                st.error(e)
                
        else:
            db.inserir_transacao(
                categoria_id= opcoes_cat[categoria_nome],
                descricao= descricao,
                valor= valor,
                data= data_movimentacao,
                tipo= tipo,
            )
            st.success(f"✅️ Movimentação registrada com sucesso! {tipo}: {formatar_brl(valor)}")
            
        
