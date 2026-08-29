import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import database as db

from utilitarios import formatar_brl

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

# db.inicializar_banco()

resumo = db.resumo_mes_atual()

col1, col2 = st.columns([1, 11], vertical_alignment="center")

with col1: 
    st.image("assets/dashboard.png")
with col2:
 st.title("Dashboard - Relatórios")

st.markdown(f"**Mês Atual:** {MESES_PT[date.today().month]}/{date.today().year}")
st.markdown("---")

col_mt1, col_mt2, col_mt3 = st.columns(3, gap="large", vertical_alignment="top")

with col_mt1:
    st.metric(
        label="🔼 Total Receitas",
        value= formatar_brl(resumo["receitas"]),
        border=True
    )
    
with col_mt2:
    st.metric(
        label="🔽 Total Despesas",
        value= formatar_brl(resumo["despesas"]),
        border=True       
    )
    
with col_mt3:
    saldo = resumo["saldo"]
    st.metric(
        label="⛃ Saldo Total",
        value= formatar_brl(resumo["saldo"]),
        border= True,
        delta= formatar_brl(saldo) if saldo != 0 else None,
        delta_color= "normal"
    )
    
st.markdown("---")

row_resume = st.container(vertical_alignment="center", gap="small", horizontal=True)

with row_resume:
    st.image("assets/statisctics.png") 
    st.subheader("Fluxo de Caixa - Ultimos 12 Meses")
    
fluxo = db.fluxo_mensal()

if not fluxo:
    st.info(":material/chat_info: Nenhuma movimentação encontrada! Adicione sua primeira movimentação em **:material/add_box: Nova Movimentação**")
else:
    df_fluxo = pd.DataFrame(fluxo)
    
    df_pivot = df_fluxo.pivot_table(
        index= "mes", columns= "tipo", values= "total", fill_value= 0
    ).reset_index()
    
    for col in ("Receita", "Despesa"):
        if col not in df_pivot.columns:
            df_pivot[col] = 0.0
    
    df_pivot = df_pivot.rename(columns= {
        "mes": "Mês",
        "Receita": "Receitas",
        "Despesa": "Despesas"
    })
    
    fig_fluxo= px.bar(
        df_pivot,
        x= "Mês",
        y= ["Receitas", "Despesas"],
        barmode= "group",
        color_discrete_map= {"Receitas": "#1565C0", "Despesas": "#ff8300"},
        labels= {"value": "R$ Valor", "variable": "Tipo"},
        title= "Receitas vs. Despesas Por Mês"
    )
    
    fig_fluxo.update_layout(
        legend_title_text= "",
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        paper_bgcolor= "rgba(0, 0, 0, 0)",
        yaxis_tickformat = ",.2f",
    )
    
    st.plotly_chart(fig_fluxo, use_container_width= True)
    
st.markdown("---")

row_resume = st.container(vertical_alignment="center", gap="small", horizontal=True)

with row_resume:
    st.image("assets/pie.png") 
    st.subheader("Despesas Por Categoria - Mês Atual")
    
desp_cat= db.despesas_por_categoria_mes_atual()

if not desp_cat:
    st.info(":material/chat_info: Nenhuma despesa cadastrada esse mês!")
else:
    df_cat = pd.DataFrame(desp_cat)
    my_custom_colors = ["#b73a28","#ff6200","#ff8300","#ffae00","#003865","#236192","#e2f0fb","#a8d600"]
    
    fig_pie= px.pie(
        df_cat,
        names= "categoria",
        values= "total",
        hole= 0.4,
        title= "Distribuição de Despesas Por Categoria",
        color_discrete_sequence= my_custom_colors
    )
    
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(
        showlegend= True,
        paper_bgcolor= "rgba(0,0,0,0)",
    )
    
    st.plotly_chart(fig_pie, use_container_width= True)