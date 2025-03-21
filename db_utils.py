import sqlite3
from unidecode import unidecode  

# 🔹 Função para conectar ao banco de dados
import sqlite3

# 🔹 Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect("hamburgueria.db")

def normalizar_texto(texto):
    return unidecode(texto.strip().lower())

# 🔹 Função para criar tabelas no banco de dados
def criar_tabelas():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE COLLATE NOCASE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_cardapio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
        descricao TEXT NOT NULL,
        preco REAL NOT NULL,
        foto TEXT NOT NULL,
        categoria_id INTEGER NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS combos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
    preco REAL NOT NULL,
    hamburguer TEXT NOT NULL,
    bebida TEXT NOT NULL,
    batata TEXT NOT NULL,
    FOREIGN KEY (hamburguer) REFERENCES itens_cardapio(nome),
    FOREIGN KEY (bebida) REFERENCES itens_cardapio(nome),
    FOREIGN KEY (batata) REFERENCES itens_cardapio(nome)
)
    """)

    conector.commit()
    conector.close()

# 🔹 Função para inserir categorias (se não existirem)
def inserir_categorias():
    conector = conectar()
    cursor = conector.cursor()
    categorias = [
        ('Menu',),
        ('Bebidas',),
        ('Combos',),
    ]
    cursor.executemany("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", categorias)
    conector.commit()
    conector.close()

# 🔹 Função para adicionar itens ao cardápio
def inserir_itens(nome, descricao, preco, foto, categoria_id):
    conector = conectar()
    cursor = conector.cursor()

    # Normaliza o nome do item para garantir que maiúsculas/minúsculas e acentos não façam diferença
    nome_normalizado = normalizar_texto(nome).strip().lower()

    # Verifica se o nome normalizado já existe no banco
    cursor.execute("SELECT 1 FROM itens_cardapio WHERE LOWER(nome) = ?", (nome_normalizado,))
    if cursor.fetchone():  # Se encontrar o item, retorna e não insere
        print(f"❌ Erro: O item '{nome}' já existe no cardápio!")
        conector.close()
        return

    # Insere o item com o nome original (mantém acentos e formatação para exibição)
    try:
        cursor.execute(
            "INSERT INTO itens_cardapio (nome, descricao, preco, foto, categoria_id) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, foto, categoria_id)
        )
        conector.commit()
        print(f"✅ Item '{nome}' adicionado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O item '{nome}' já existe no cardápio!")
    finally:
        conector.close()

# 🔹 Função para adicionar combos referenciando pelos nomes dos itens
def adicionar_combo(nome_combo, preco, hamburguer, bebida, batata):
    conector = conectar()
    cursor = conector.cursor()

    itens_requeridos = {hamburguer, bebida, batata}
    cursor.execute("SELECT nome FROM itens_cardapio WHERE nome IN (?, ?, ?)", (hamburguer, bebida, batata))
    itens_encontrados = {row[0] for row in cursor.fetchall()}

    if not itens_requeridos.issubset(itens_encontrados):
        itens_faltando = itens_requeridos - itens_encontrados
        print(f"❌ Erro: Os seguintes itens não existem no menu: {', '.join(itens_faltando)}")
        conector.close()
        return

    cursor.execute("SELECT 1 FROM combos WHERE nome = ?", (nome_combo,))
    if cursor.fetchone():
        print(f"❌ Erro: O combo '{nome_combo}' já existe!")
        conector.close()
        return

    cursor.execute(
        "INSERT INTO combos (nome, preco, hamburguer, bebida, batata) VALUES (?, ?, ?, ?, ?)",
        (nome_combo, preco, hamburguer, bebida, batata)
    )

    conector.commit()
    conector.close()
    print(f"✅ Combo '{nome_combo}' cadastrado com sucesso!")

# 🔹 Atualiza um item no cardápio pelo ID ou nome. Apenas os campos fornecidos serão atualizados.
def atualizar_item(id_ou_nome, nome=None, descricao=None, preco=None, foto=None, categoria_id=None):
    """
    Parâmetros:
    - id_ou_nome: ID (int) ou nome (str) do item a ser atualizado.
    - nome: Novo nome do item (opcional).
    - descricao: Nova descrição (opcional).
    - preco: Novo preço (opcional).
    - foto: Novo caminho da foto (opcional).
    - categoria_id: Novo ID da categoria (opcional).
    """
    conector = conectar()
    cursor = conector.cursor()

    # Determina se o identificador é ID ou nome
    if isinstance(id_ou_nome, int):
        campo_busca = "id"
        valor_busca = id_ou_nome
    elif isinstance(id_ou_nome, str):
        campo_busca = "nome"
        valor_busca = id_ou_nome
    else:
        print("❌ Erro: Identificador deve ser o ID ou o NOME! ")
        return
    
    # Verifica se o item existe
    cursor.execute(f"SELECT id, nome FROM itens_cardapio WHERE {campo_busca} = ?", (valor_busca,))  # Tuple com vírgula
    item = cursor.fetchone()
    if not item:
        print(f"❌ Erro: Item com {campo_busca} '{valor_busca}' não encontrado!")
        conector.close()
        return
    
    item_id, nome_atual = item

    # Monta a query de atualização dinamicamente com base nos campos fornecidos
    campos = []
    valores = []

    if nome is not None:
        nome_normalizado = normalizar_texto(nome)
        # Verifica se o novo nome já existe (exceto para o próprio item)
        cursor.execute(
            "SELECT 1 FROM itens_cardapio WHERE nome != ? AND nome = ?",
            (nome_atual, nome)
        )
        if cursor.fetchone():
            print(f"❌ Erro: O nome '{nome}' já existe no cardápio!")
            conector.close()
            return
        campos.append("nome = ?")
        valores.append(nome)

    if descricao is not None:
        campos.append("descricao = ?")
        valores.append(descricao)

    if preco is not None:
        campos.append("preco = ?")
        valores.append(preco)

    if foto is not None:
        campos.append("foto = ?")
        valores.append(foto)

    if categoria_id is not None:
        # Verifica se a categoria existe
        cursor.execute("SELECT 1 FROM categorias WHERE id = ?", (categoria_id,))
        if not cursor.fetchone():
            print(f"❌ Erro: Categoria com ID {categoria_id} não existe!")
            conector.close()
            return
        campos.append("categoria_id = ?")
        valores.append(categoria_id)

    # Se nenhum campo foi fornecido para atualização, não faz sentido prosseguir
    if not campos:
        print("❌ Erro: Nenhum campo fornecido para atualização!")
        conector.close()
        return
    
    # Adiciona o ID do item como último valor para a cláusula WHERE
    valores.append(item_id)

    # Monta e executa a query
    query = f"UPDATE itens_cardapio SET {', '.join(campos)} WHERE id = ?"
    try:
        cursor.execute(query, valores)
        conector.commit()
        print(f"✅ Item '{nome_atual}' atualizado com sucesso!")  # Corrige aspas
    except sqlite3.IntegrityError as e:
        print(f"❌ Erro ao atualizar o item: {e}")

    conector.close()

# 🔹 Função para listar o menu
def listar_menu():
    conector = conectar()
    cursor = conector.cursor()

    print("\n📌 Lista do Menu: ")
    cursor.execute("SELECT DISTINCT nome, descricao, preco FROM itens_cardapio WHERE categoria_id = 1")

    for row in cursor.fetchall():
        print(f"➤ {row[0]} - {row[1]} - R${row[2]:.2f}")

    conector.close()

# 🔹 Função para listar combos
def listar_combos():
    conector = conectar()
    cursor = conector.cursor()

    print("\n🍔🥤 Combos Disponíveis:")
    cursor.execute("SELECT nome, hamburguer, bebida, batata, preco FROM combos")

    for combo in cursor.fetchall():
        print(f"\n🛒 {combo[0]}: {combo[1]} + {combo[2]} + {combo[3]} - R${combo[4]:.2f}")

    conector.close()

# 🔹 Função para visualizar a estrutura do banco de dados
def visualizar_banco():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()

    for tabela in tabelas:
        print(f"\n📝 Estrutura da tabela {tabela[0]}:\n{tabela[1]}")

    conector.close()
    print("Banco visualizado!")

# 🔹 Função para visualizar os dados de uma tabela específica
def visualizar_tabela(nome_tabela):
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute(f"SELECT * FROM {nome_tabela}")
    linhas = cursor.fetchall()

    for linha in linhas:
        print(linha)

    conector.close()

# 🔹 Função para excluir uma tabela
def drop_tabela(nome_tabela):
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
    conector.commit()
    conector.close()

    print(f"Tabela {nome_tabela} excluída com sucesso!")

# 🔹 Função para resetar o banco de dados
def resetar_banco():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("DROP TABLE IF EXISTS categorias")
    cursor.execute("DROP TABLE IF EXISTS itens_cardapio")
    cursor.execute("DROP TABLE IF EXISTS combos")

    conector.commit()
    conector.close()
    print("Banco resetado!")


