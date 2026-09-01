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

transacoes = db.listar_transacoes()

col1, col2 = st.columns([1, 11], vertical_alignment="center")

with col1: 
    st.image("assets/transaction.png")
with col2:
    st.title("Histórico de Movimentações")
st.markdown("---")

col1, col2, col3= st.columns(3, gap="xxlarge")
hoje= date.today()

with col1:
    anos_disponiveis= list(range(hoje.year, hoje.year - 5, -1))
    ano_sel= st.selectbox("**Filtrar por Ano**", options= ["Todos"] + [str(a) for a in anos_disponiveis])
    
with col2:
    # Constrói um dicionário {label_exibido: número do mês}
    # O operador '|' (Python 3.9+) une dois dicionários
    meses_opcoes= {"Todos": None} | {f"{v}/{k:02d}": k for k, v in MESES_PT.items()}
    mes_label= st.selectbox("**Filtrar por Mês**", options= list(meses_opcoes.keys()))
    mes_sel= meses_opcoes[mes_label]
    
with col3:
    tipo_sel= st.selectbox("**Filtrar por Tipo**", options=["Todos", "Receita", "Despesa"])
    
# Converte as seleções para os parâmetros esperados pela função do banco.
# None indica "sem filtro" para aquele campo.
mes_param= mes_sel if mes_label != "Todos" else None
ano_param= int(ano_sel) if ano_sel != "Todos" else None
tipo_param= tipo_sel if tipo_sel != "Todos" else None

# Lógica de consulta: a função do banco filtra por mês + ano juntos
# Se só o ano foi selecionado, filtramos manualmente em Python.
transacoes= db.listar_transacoes(
    mes= mes_param,
    ano= ano_param,
    tipo= tipo_param
)
    
st.markdown("---")

if not transacoes:
    st.info(":material/chat_info: Nenhuma movimentação encontrada com os filtros selecionados!")



# Tabela de movimentações
df = pd.DataFrame(transacoes)
# st.write(df.columns)

# Converte a string "YY-MM-DD" para o formato brasileiro "DD/MM/YYYY"
df["data"]= pd.to_datetime(df["data"]).dt.strftime("%d/%m/%Y")
df["valor_fmt"]= df["valor"].apply(formatar_brl)

df_exibir= df[["id", "data", "tipo", "categoria", "descricao", "valor_fmt"]].rename(columns= {
    "id": "ID",
    "data": "Data",
    "tipo": "Tipo",
    "categoria": "Categoria",
    "descricao": "Descrição",
    "valor_fmt": "Valor R$"
})

st.dataframe(df_exibir, width= "stretch", hide_index= True)

# Totais do Filtro
# Calcula usando a coluna numérica original (df["valor"]) e não a formatada (df["valor_fmt"])

total_receitas= df[df["tipo"] == "Receita"]["valor"].sum()
total_despesas= df[df["tipo"] == "Despesa"]["valor"].sum()

col_r, col_d, col_s = st.columns(3, gap= "xxlarge")
col_r.metric("🔼 Receitas (Filtro)", formatar_brl(total_receitas))
col_d.metric("🔽 Total Despesas", formatar_brl(total_despesas))
col_s.metric("🏦 Saldo Total", formatar_brl(total_receitas - total_despesas))


# Exclusão de Movimentação
st.markdown("---")
row_resume = st.container(vertical_alignment="center", gap="small", horizontal=True)

with row_resume:
    st.image("assets/trash.png") 
    st.subheader("Excluir Movimentação")
    
st.caption("*Informe o ID da movimentação que deseja excluir.*")

col_id, col_btn = st.columns([2, 1], gap= "medium")
with col_id:
    id_excluir= st.number_input("ID da Movimentação", min_value= 1, step=1, label_visibility= "collapsed")
with col_btn:
    if st.button("Excluir", type= "primary", width= "stretch"):
        ids_validos= df["id"].tolist()
        if id_excluir in ids_validos:
            db.deletar_transacao(int(id_excluir))
            st.success(f"✅ Movimentação #{int(id_excluir)} removida com sucesso!")
            st.rerun()
        else:
            st.error("❗ ID não encontrado nas movimentações exibidas!")
            