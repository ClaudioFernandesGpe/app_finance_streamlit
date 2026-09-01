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
 
st.markdown("---")

col_form, col_list = st.columns([1, 2])

with col_form:
    st.subheader("✚ Nova Categoria")
    with st.form("form_categoria", clear_on_submit= True):
        nome_cat= st.text_input("Nome da Categoria *")
        tipo_cat= st.radio("Tipo *", options= ["Receita", "Despesa"], horizontal= True)
        adicionar= st.form_submit_button("Salvar Categoria")
        
    if adicionar:
        if not nome_cat.strip():
            st.error("❗ O nome da categoria não pode estar em branco!")
        else:
            # Verifica duplicatas de forma case-insensitive antes de inserir.
            nomes_existentes= [c["nome"].lower() for c in db.listar_categorias()]
            if nome_cat.strip().lower() in nomes_existentes:
                st.warning(f'⚠ A Categoria "{nome_cat}" já existe!')
            else:
                db.inserir_categoria(nome_cat, tipo_cat)
                st.success(f'✅ A categoria "{nome_cat}" foi adicionada com sucesso!')
                st.rerun()
with col_list:
    st.subheader("📋 Categorias Cadastradas")
    categorias= db.listar_categorias()
    
    if not categorias:
        st.info("🛈︎ Nenhuma categoria cadastrada!")
    else:
        df_cat= pd.DataFrame(categorias).rename(columns= {
            "id": "ID",
            "nome": "Nome",
            "tipo": "Tipo"
        })
        st.dataframe(df_cat, width= "stretch", hide_index= True)
        
    st.markdown("---")
    st.caption("⚠ ***Excluir uma categoria exclui apenas ela. Movimentações vinculadas continuam salvas.***")
    
    col_cid, col_cbtn = st.columns([1, 2])
    with col_cid:
        id_cat_del= st.number_input("ID da Categoria", min_value= 1, step= 1, label_visibility= "collapsed", key= "del_cat")
    with col_cbtn:
        if st.button("Excluir", type= "primary", key="btn_del_cat"):
            ids_cat= df_cat["ID"].tolist()
            if int(id_cat_del) in ids_cat:
                db.deletar_categoria(int(id_cat_del))
                st.success(f"✅ Categoria #{int(id_cat_del)} removida!")
                st.rerun()
            else:
                st.error("❗ ID não encontrado!")