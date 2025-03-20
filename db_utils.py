import sqlite3

# 🔹 Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect("hamburgueria.db")

# 🔹 Função para criar tabelas no banco de dados
def criar_tabelas():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_cardapio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
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
        nome TEXT NOT NULL UNIQUE,
        preco REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS combo_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        combo_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        FOREIGN KEY (combo_id) REFERENCES combos (id),
        FOREIGN KEY (item_id) REFERENCES itens_cardapio (id)
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
def inserir_itens():
    conector = conectar()
    cursor = conector.cursor()
    itens_cardapio = [
        ('X-Boladão', '2 carnes, 2 ovos, bacon, calabresa, queijo, salada, batata palha, ketchup, maionese da casa e molho Billy Jack', 15.00, './assets/X-Boladão.png', 1),
        ('X-BBQ', 'Carne, queijo, onion, barbecue e molho Billy Jack', 9.00, './assets/Combo X-BBQ.jpeg', 1),
        ('Cachorro-quente', 'Salsicha, molho, milho, ervilha, batata palha, queijo ralado, ovo de codorna, ketchup e molho Billy Jack', 9.00, './assets/Cachorro-quente.jpg', 1),
        ('Guaravita', 'Suco de guaraná natural', 2.00, './assets/guaravita.jpg', 2),
        ('Batata pequena', 'Porção de batata frita crocante', 3.00, './assets/batata.jpg', 1)
    ]
    cursor.executemany("INSERT INTO itens_cardapio (nome, descricao, preco, foto, categoria_id) VALUES (?, ?, ?, ?, ?)", itens_cardapio)
    conector.commit()
    conector.close()

# 🔹 Função para obter o dicionário {nome_item: id}
def obter_itens_dict():
    conector = conectar()
    cursor = conector.cursor()
    cursor.execute("SELECT id, nome FROM itens_cardapio")
    itens_dict = {nome: id for id, nome in cursor.fetchall()}
    conector.close()
    return itens_dict

# 🔹 Função para adicionar combos
def adicionar_combo(nome_combo, preco, itens):
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("INSERT INTO combos (nome, preco) VALUES (?, ?)", (nome_combo, preco))
    id_combo = cursor.lastrowid  # Pega o ID do combo recém-criado

    itens_dict = obter_itens_dict()  # Obtém IDs dos itens
    combo_itens = [(id_combo, itens_dict[item]) for item in itens]

    cursor.executemany("INSERT INTO combo_itens (combo_id, item_id) VALUES (?, ?)", combo_itens)
    conector.commit()
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
    cursor.execute("""
        SELECT c.nome AS combo, i.nome AS item
        FROM combos c
        JOIN combo_itens ci ON c.id = ci.combo_id
        JOIN itens_cardapio i ON ci.item_id = i.id
        ORDER BY c.nome
    """)

    resultados = cursor.fetchall()
    
    combos_dict = {}  # Dicionário para armazenar combos sem repetir
    
    for combo, item in resultados:
        if combo not in combos_dict:
            combos_dict[combo] = []
        combos_dict[combo].append(item)
    
    for combo, itens in combos_dict.items():
        print(f"\n🛒 {combo}:")
        for item in itens:
            print(f" ➤ {item}")

    conector.close()


def visualizar_tabela(nome_tabela):
    conector = sqlite3.connect("hamburgueria.db")
    cursor = conector.cursor()

    cursor.execute(f"SELECT * FROM {nome_tabela}")
    linhas = cursor.fetchall()

    for linha in linhas:
        print(linha)

    conector.close()

def drop_tabela(nome_tabela):
    conector = sqlite3.connect("hamburgueria.db")
    cursor = conector.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
    conector.commit()
    conector.close()

    print(f"Tabela {nome_tabela} excluída com sucesso!")

def resetar_banco():
    conector = sqlite3.connect("hamburgueria.db")
    cursor = conector.cursor()

    cursor.execute("DROP TABLE IF EXISTS categorias")
    cursor.execute("DROP TABLE IF EXISTS itens_cardapio")
    cursor.execute("DROP TABLE IF EXISTS combos")
    cursor.execute("DROP TABLE IF EXISTS combo_itens")

    conector.commit()
    conector.close()
    print("Banco resetado!")

def visualizar_banco():
    conector = sqlite3.connect("hamburgueria.db")
    cursor = conector.cursor()

    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()

    for tabela in tabelas:
        print(f"\n📝 Estrutura da tabela {tabela[0]}:\n{tabela[1]}")

    
    conector.close()
    print("Banco visualizado!")

