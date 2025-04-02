import sqlite3
from unidecode import unidecode  


#  Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect("hamburgueria.db")

def normalizar_texto(texto):
    return unidecode(texto.strip().lower())

#  Função para criar tabelas no banco de dados
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
    CREATE TABLE IF NOT EXISTS itens (
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
    hamburguer TEXT NOT NULL,
    bebida TEXT,
    complemento TEXT,
    preco REAL NOT NULL,
    foto TEXT NOT NULL,
    FOREIGN KEY (hamburguer) REFERENCES itens(nome),
    FOREIGN KEY (bebida) REFERENCES itens(nome),
    FOREIGN KEY (complemento) REFERENCES itens(nome)
)
    """)

    conector.commit()
    conector.close()

#  Função para inserir categorias (se não existirem)
def inserir_categorias():
    conector = conectar()
    cursor = conector.cursor()
    categorias = [
        ('Menu',),
        ('Bebidas',),
        ('Combos',),
        ('acompanhamentos',),
    ]
    cursor.executemany("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", categorias)
    conector.commit()
    conector.close()

#  Função para adicionar itens ao cardápio
def inserir_itens(nome, descricao, preco, foto, categoria_id):
    conector = conectar()
    cursor = conector.cursor()

    # Normaliza o nome do item para garantir que maiúsculas/minúsculas e acentos não façam diferença
    nome_normalizado = normalizar_texto(nome)

    # Verifica se o nome normalizado já existe no banco
    cursor.execute("SELECT 1 FROM itens WHERE LOWER(nome) = ?", (nome_normalizado,))
    if cursor.fetchone():  # Se encontrar o item, retorna e não insere
        print(f"❌ Erro: O item '{nome}' já existe no cardápio!")
        conector.close()
        return

    # Insere o item com o nome original (mantém acentos e formatação para exibição)
    try:
        cursor.execute(
            "INSERT INTO itens (nome, descricao, preco, foto, categoria_id) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, foto, categoria_id)
        )
        conector.commit()
        print(f"✅ Item '{nome}' adicionado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O item '{nome}' já existe no cardápio!")
    finally:
        conector.close()

#  Função para adicionar combos referenciando pelos nomes dos itens
def adicionar_combo(nome_combo, hamburguer, bebida, complemento, foto):
    conector = conectar()
    cursor = conector.cursor()

    itens_requeridos = {hamburguer, bebida, complemento}
    cursor.execute("SELECT nome FROM itens WHERE nome IN (?, ?, ?)", (hamburguer, bebida, complemento))
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
        "SELECT SUM(preco) FROM itens WHERE nome IN (?, ?, ?)",
        (hamburguer, bebida, complemento)
    )
    preco_total = cursor.fetchone()[0]
    if preco_total is None:
        print("❌ Erro: Não foi possível calcular o preço do combo!")
        conector.close()
        return

    cursor.execute(
        "INSERT INTO combos (nome, hamburguer, bebida, complemento, preco, foto) VALUES (?, ?, ?, ?, ?, ?)",
        (nome_combo, hamburguer, bebida, complemento, preco_total, foto)
    )

    conector.commit()
    conector.close()
    print(f"✅ Combo '{nome_combo}' cadastrado com sucesso! Preço: R${preco_total:.2f}")

#  Atualiza um item no cardápio pelo ID ou nome. Apenas os campos fornecidos serão atualizados.
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
    cursor.execute(f"SELECT id, nome FROM itens WHERE {campo_busca} = ?", (valor_busca,))  # Tuple com vírgula
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
            "SELECT 1 FROM itens WHERE nome != ? AND nome = ?",
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
    query = f"UPDATE itens SET {', '.join(campos)} WHERE id = ?"
    try:
        cursor.execute(query, valores)
        conector.commit()
        print(f"✅ Item '{nome_atual}' atualizado com sucesso!")  # Corrige aspas
        # Se o nome ou o preco foi alterado, atualiza os combos
        if nome is not None or preco is not None:
            novo_nome = nome if nome is not None else nome_atual
            atualizar_combos(nome_atual, novo_nome)
    except sqlite3.IntegrityError as e:
        print(f"❌ Erro ao atualizar o item: {e}")

    conector.close()

# Função para atualizar os combos
def atualizar_combos(nome_antigo, novo_nome):
    """
    Atualiza os campos hamburguer, bebida e complemento na tabela combos
    quando o nome de um item em itens é alterado.
    
    Parâmetros:
    - nome_antigo: Nome original do item em itens.
    - novo_nome: Novo nome do item em itens.
    """

    conector = conectar()
    cursor = conector.cursor()

    try:
        cursor.execute(
            "UPDATE combos SET hamburguer = ? WHERE hamburguer = ?",
            (novo_nome, nome_antigo)
        )
        cursor.execute(
            "UPDATE combos SET bebida = ? WHERE bebida = ?",
            (novo_nome, nome_antigo)
        )
        cursor.execute(
            "UPDATE combos SET complemento = ? WHERE complemento = ?",
            (novo_nome, nome_antigo)
        )
        # Atualiza o nome do combo onde o nome contém o nome_antigo
        cursor.execute(
            "UPDATE combos SET nome = REPLACE(nome, ?, ?) WHERE nome LIKE ?",
            (nome_antigo, novo_nome, f'%{nome_antigo}%')
        )

        # Recalcula o preço de todos os combos que usam o item atualizado
        cursor.execute(
            "SELECT nome, hamburguer, bebida, complemento FROM combos WHERE hamburguer = ? OR bebida = ? OR complemento = ?",
            (novo_nome, novo_nome, novo_nome)
        )
        combos_afetados = cursor.fetchall()  
        for combo in combos_afetados:
            nome_combo, hamburguer, bebida, complemento = combo
            cursor.execute(
                "SELECT SUM(preco) FROM itens WHERE nome IN (?, ?, ?)",
                (hamburguer, bebida, complemento)
            )
            novo_preco = cursor.fetchone()[0]
            if novo_preco is not None:
                cursor.execute(
                    "UPDATE combos SET preco = ? WHERE nome = ?",
                    (novo_preco, nome_combo)
                )

        conector.commit()

        if combos_afetados:
            print(f"ℹ️ Combos atualizados com o novo nome '{novo_nome}' e preços recalculados!")
    except sqlite3.IntegrityError as e:
        print(f"❌ Erro ao atualizar combos: {e}")

    conector.close()

# Função para deletar itens
def deletar_itens(id_ou_nome):
    """
    Deleta um item da tabela itens. Se o item for um hamburguer usado em um combo,
    o combo correspondente também será deletado.
    
    Parâmetros:
    - id_ou_nome: ID (int) ou nome (str) do item a ser deletado.
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
        print("❌ Erro: Identificador deve ser o ID ou o NOME!")
        conector.close()
        return
    
    # Verifica se o item existe e pega sua categoria
    cursor.execute(f"SELECT id, nome, categoria_id FROM itens WHERE {campo_busca} = ?", (valor_busca,))
    item = cursor.fetchone()
    if not item:
        print(f"❌ Erro: Item com {campo_busca} '{valor_busca}' não encontrado!")
        conector.close()
        return
    
    item_id, nome_item, categoria_id = item

    try:
        # Se o item é da categoria 'Menu' (hamburguer, categoria_id = 1), verifica combos
        if categoria_id == 1:
            cursor.execute("SELECT nome FROM combos WHERE hamburguer = ?", (nome_item,))
            combos_afetados = cursor.fetchall()
            if combos_afetados:
                for combo in combos_afetados:
                    nome_combo = combo[0]
                    cursor.execute("DELETE FROM combos WHERE nome = ?", (nome_combo,))
                    print(f"ℹ️ Combo '{nome_combo}' deletado porque usava o hambúrguer '{nome_item}'.")
         # Se for bebida (categoria_id = 2), seta bebida como NULL e recalcula preço
        elif categoria_id == 2:
            cursor.execute("SELECT nome, hamburguer, complemento FROM combos WHERE bebida = ?", (nome_item,))
            combos_afetados = cursor.fetchall()
            if combos_afetados:
                for combo in combos_afetados:
                    nome_combo, hamburguer, complemento = combo
                    cursor.execute("UPDATE combos SET bebida = NULL WHERE nome = ?", (nome_combo,))
                    cursor.execute(
                        "SELECT SUM(preco) FROM itens WHERE nome in (?, ?, ?) AND nome IS NOT NULL",
                        (hamburguer, None, complemento)
                    )
                    novo_preco = cursor.fetchone()[0] or 0
                    cursor.execute("UPDATE combos SET preco = ? WHERE nome = ?", (novo_preco, nome_combo))
                    print(f"ℹ️ Bebida '{nome_item}' removida do combo '{nome_combo}'. Novo preço: R${novo_preco:.2f}")

        # Se for complemento (categoria_id = 4), seta complemento como NULL e recalcula preço
        elif categoria_id == 4:
            cursor.execute("SELECT nome, hamburguer, bebida FROM combos WHERE complemento = ?", (nome_item,))
            combos_afetados = cursor.fetchall()
            if combos_afetados:
                for combo in combos_afetados:
                    nome_combo, hamburguer, bebida = combo
                    cursor.execute("UPDATE combos SET complemento = NULL WHERE nome = ?", (nome_combo,))
                    cursor.execute(
                        "SELECT SUM(preco) FROM itens WHERE nome in (?, ?, ?) AND nome IS NOT NULL",
                        (hamburguer, bebida, "")
                    )
                    novo_preco = cursor.fetchone()[0] or 0
                    cursor.execute("UPDATE combos SET preco = ? WHERE nome = ?", (novo_preco, nome_combo))
                    print(f"ℹ️ complemento '{nome_item}' removida do combo '{nome_combo}'. Novo preço: R${novo_preco:.2f}")

        # Deleta o item da tabela itens
        cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
        conector.commit()
        print(f"✅ Item '{nome_item}' deletado com sucesso!")

    except sqlite3.IntegrityError as e:
        print(f"❌ Erro ao deletar o item: {e}")

    conector.close()

#  Função para listar o menu (junto dos combos e bebidas)
def listar_menu():
    conector = conectar()
    cursor = conector.cursor()

    print("\n📌 Lista do Menu: ")
    cursor.execute("SELECT DISTINCT nome, descricao, preco FROM itens WHERE categoria_id = 1")

    for row in cursor.fetchall():
        print(f"➤ {row[0]} - {row[1]} - R${row[2]:.2f}")

    listar_bebidas()
    listar_combos()
    listar_acompanhamentos()
    conector.close()

#  Função para listar combos
def listar_combos():
    conector = conectar()
    cursor = conector.cursor()

    print("\n🍔🥤 Combos Disponíveis:")
    cursor.execute("SELECT nome, hamburguer, bebida, complemento, preco FROM combos")

    for combo in cursor.fetchall():
        print(f"🛒 {combo[0]}: {combo[1]} + {combo[2]} + {combo[3]} - R${combo[4]:.2f}")

    conector.close()

#  Função para listar bebidas
def listar_bebidas():
    conector = conectar()
    cursor = conector.cursor()

    print("\n🥤 Lista de Bebidas:")
    cursor.execute("SELECT nome, descricao, preco FROM itens WHERE categoria_id = 2")
    for row in cursor.fetchall():
        print(f"➤ {row[0]} - {row[1]} - R${row[2]:.2f}")

    conector.close()

#  Função para listar acompanhamentos
def listar_acompanhamentos():
    conector = conectar()
    cursor = conector.cursor()

    print("\n🍟 Lista de Acompanhamentos: ")
    cursor.execute("SELECT nome, descricao, preco FROM itens WHERE categoria_id = 4")
    for row in cursor.fetchall():
        print(f"➤ {row[0]} - {row[1]} - R${row[2]:.2f}")
    
    conector.close()

#  Função para visualizar a estrutura do banco de dados
def visualizar_banco():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()

    for tabela in tabelas:
        print(f"\n📝 Estrutura da tabela {tabela[0]}:\n{tabela[1]}")

    conector.close()
    print("Banco visualizado!")

#  Função para visualizar os dados de uma tabela específica
def visualizar_tabela(nome_tabela):
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute(f"SELECT * FROM {nome_tabela}")
    linhas = cursor.fetchall()

    for linha in linhas:
        print(linha)

    conector.close()

#  Função para excluir uma tabela
def drop_tabela(nome_tabela):
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
    conector.commit()
    conector.close()

    print(f"Tabela {nome_tabela} excluída com sucesso!")

#  Função para resetar o banco de dados
def resetar_banco():
    conector = conectar()
    cursor = conector.cursor()

    cursor.execute("DROP TABLE IF EXISTS categorias")
    cursor.execute("DROP TABLE IF EXISTS itens")
    cursor.execute("DROP TABLE IF EXISTS combos")

    conector.commit()
    conector.close()
    print("Banco resetado!")


