from db_utils import criar_tabelas, inserir_categorias, inserir_itens, adicionar_combo, listar_menu, listar_combos, visualizar_tabela, drop_tabela, resetar_banco, visualizar_banco, atualizar_item

#resetar_banco()
#criar_tabelas()
#inserir_categorias()

# Exemplo de como inserir combo: 
#adicionar_combo("Combo X-Boladao", 20.00, "X-Boladao", "Guaravita", "Batata pequena")

# Exemplo de como adicionar itens:
#inserir_itens('X-Boladao', '2 carnes, 2 ovos, bacon, calabresa, queijo, salada, batata palha, ketchup, maionese da casa e molho Billy Jack', 15.00, './assets/X-Boladão.png', 1)
#inserir_itens("Guaravita", "Suco de guaraná natural", 2.00, "guaravita.jpg", 2)
#inserir_itens("Batata pequena", "Porção de batata frita crocante", 3.00, "batata.jpg", 1)

visualizar_tabela("itens_cardapio")


#atualizar_item('X-Boladao Plus', nome='X-Boladao', preco=20.00)
