# UTILITÁRIOS
# ========================================================================
def formatar_brl(valor: float) -> str:
    """
    Formata um valor no padrão monetário brasileiro.
    Ex. 1500.5 ==> "R$ 1.500,00"

    A lógica dos três replace() é necessária porque o Python utiliza vírgula como
    separador de milhar e ponto como decimal, o inverso do padrão pt-BR.
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Dicionário auxiliar para exibir a abreviação do nome dos meses em português.
# Usado nos filtros e no cabeçalho do Dashboard

# MESES_PT = {
#     1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
#     7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
# }