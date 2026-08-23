import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent/"finance.db"

# Dados iniciais (SEED)
CATEGORIAS_PADRAO = [
    ("Salário", "Receita"),
    ("Freelance", "Receita"),
    ("Rendimentos", "Receita"),
    ("Alimentação", "Despesa"),
    ("Moradia", "Despesa"),
    ("Transporte", "Despesa"),
    ("Saúde", "Despesa"),
    ("Pets", "Despesa"),
    ("Lazer", "Despesa"),
    ("Cartão de Crédito", "Despesa")
]

# Conexão
def _conectar() -> sqlite3.Connection:
    '''
    Abre e retorna uma conexão com o banco de dados.

    O prefixo _ indica que é uma função interna (privada) deste módulo -
    apenas as funções daqui devem chamá-la diretamente.
    '''
    conn= sqlite3.connect(DB_PATH)

    # row_factory = sqlite3.Row faz com que cada linha retornada pelo banco de dados
    # se comporte como um dicionário: row['nome'] ao invés de row[0].
    conn.row_factory= sqlite3.Row

    # Habilita a verificação de chaves estrangeiras no SQLite.
    # Por padrão, o SQLite ignora contraints de FK - esse PRAGMA ativa a checagem.
    conn.execute("PRAGMA foreign_keys=ON")

    return conn

# Inicialização do Banco de Dados
def inicializar_banco() -> None:
    '''
    Cria as tabelas (se não existirem) e popula as categorias padrão.
    Chamada uma vez no início do app.py.
    ''' 

    # O bloco "with" garante que a conexão seja fechada e o commit seja feito
    # automaticamente ao final, mesmo se ocorrerem erros.
    with _conectar() as conn:

        # executescript permite rodar múltiplos comandos SQL de uma vez.
        # CREATE TABLE IF NOT EXISTS  evita erro caso as tabelas já existam.
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS categorias (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Receita', 'Despesa'))
            );

            CREATE TABLE IF NOT EXISTS transacoes (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria_id INTEGER NOT NULL REFERENCES categorias(id),
                descricao    TEXT NOT NULL,
                valor        REAL NOT NULL CHECK (VALOR > 0),
                data         DATE NOT NULL,
                tipo         TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa'))
            );
        """)

        # Só insere o SEED se a tabela de categorias estiver vazia.
        # Isso evita duplicar os dados a cada reinicialização do APP.
        qtd = conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
        if qtd == 0:
            # executemany é eficiente: executa o mesmo INSERT para cada 
            # tupla da lista em uma única operação de banco.
            conn.executemany(
                "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
                CATEGORIAS_PADRAO,
            )

# CRUD - CATEGORIAS
# ==========================================================================
def listar_categorias(tipo: str | None = None ) -> list[dict]:
    """
    Retorna todas as categorias. Se "tipo" for informado ("Receita" ou "Despesa),
    filtra apenas as daquele tipo.

    Retorna uma lista de dicionários para fácil consumo pelo Streamlit/Pandas
    """

    # Começamos com uma query base e adicionamos cláusulas dinamicamente
    sql = "SELECT * FROM categorias"
    params: tuple = ()

    if tipo:
        sql += " WHERE tipo = ?"
        # O '?' é um placeholder parametrizado - protege contra SQL Injection
        params = (tipo,)
    sql += " ORDER BY tipo, nome DESC" 

    with _conectar() as conn:
        # O dict(r) converte cada sqlite3.Row em um dicionário Python puro.
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def inserir_categoria(nome: str, tipo: str) -> None:
    """ Insere uma nova categoria no banco """
    with _conectar() as conn:
        conn.execute(
            "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
            # strip() remove espaços acidentais antes/depois do texto digitado
            (nome.strip(), tipo) 
        )

def deletar_categoria(categoria_id: int) -> None:
    """ Remove uma categoria pelo seu ID """
    with _conectar as conn:
        conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))

# CRUD - TRANSAÇÕES
# ===========================================================================
def inserir_transacao(categoria_id: int,descricao: str, valor: float, data: date, tipo: str) -> None:
    """ Insere uma nova transação financeira no banco. """
    with _conectar() as conn:
        conn.execute(
            """INSERT INTO transacoes (categoria_id, descricao, valor, data, tipo) VALUES (?, ?, ?, ?, ?)""",
            (categoria_id, descricao.strip(), valor, data.isoformat(), tipo)
        )

def listar_transacoes(mes: int | None = None, ano: int | None = None, tipo: str | None = None) -> list[dict]:
    # WHERE 1 =1 é um truque clássico: permite encadear cláusulas AND
    # dinamicamente sem se preocupar se é a primeira condição ou não.

    sql = """
        SELECT t.id, t.data, t.tipo, c.nome AS categoria, t.descricao, t.valor
        FROM transacoes AS t,
        JOIN categorias c ON c.id = t.id_categoria,
        WHERE 1 = 1
    """
    params: list = []

    if mes and ano:
        sql += " AND strftime('%m', t.data) = ? AND strftime('%Y', t.data) = ?"
        params += [f"{mes:02d}", str(ano)]

    if tipo:
        sql += " AND t.tipo = ?"
        params.append(tipo)

    # Ordena pela data mais recente primeiro: em caso de empate pelo ID maior primeiro
    sql += " ORDER BY t.data DESC, t.id DESC"

    with _conectar() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def deletar_transacao(transacao_id: int) -> None:
    with _conectar() as conn:
        conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id))

# CONSULTAS ANÁLITICAS - DASHBOARDS
# ============================================================================
def resumo_mes_atual() -> dict:
    hoje = date.today()
    mes = f"{hoje.month:02d}"
    ano = str(hoje.year)

    with _conectar() as conn:
        # COALESCE retorna o segundo argumento 0 se SUM for NULL,
        # o que acontece quando não há nenhuma transação no período.

        receitas = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) FROM transacoes
                WHERE tipo = 'Receita'
                    AND strftime('%m', data) = ?
                    AND strftime('%Y', data) = ?""",
            (mes, ano),
        ).fetchone()[0]

        despesas = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) FROM transacoes
                WHERE tipo = 'Despesa'
                    AND strftime('%m', data) = ?
                    AND strftime('%Y', data) = ?""",
            (mes, ano),
        ).fetchone()[0]

    return {
        "receitas": receitas,
        "despesas": despesas,
        # Saldo pode ser negativo - a UI trata a exibição corretamente.
        "saldo": receitas - despesas,
    }

def fluxo_mensal() -> list[dict]:
    """
    Retorna receitas e despesas agrupadas por mês nos últimos 12 meses.
    Usado para o gráfico de barras do Dashboard.
    """

    with _conectar() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m', data) AS mes, tipo, SUM(valor) AS total
            FROM transacoes
            WHERE data >= date('now', '-12 months') 
            GROUP BY mes, tipo
            ORDER BY mes
        """).fetchall()
    return [dict(r) for r in rows]

def despesas_por_categoria_mes_atual() -> list[dict]:
    """
    Retorna o total de despesas do mês atual agrupado por categorias.
    Usado para o gráfico de pizza/rosca do Dashboard.
    """

    hoje = date.today()
    mes = f"{hoje.month:02d}"
    ano = str(hoje.year)

    with _conectar() as conn:
        rows = conn.execute(
            """SELECT c.nome AS categoria, SUM(t.valor) AS total
                FROM transacoes t
                JOIN categorias c ON c.id = t.categoria_id
                WHERE t.tipo = 'Despesa'
                    AND strftime('%m', t.data) = ?
                    AND strftime('%Y', t.data) = ?
                GROUP BY c.nome
                ORDER BY total DESC""",
            (mes, ano)
            ).fetchall()
    return [dict(r) for r in rows]

