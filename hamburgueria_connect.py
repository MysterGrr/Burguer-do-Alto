from db_utils import criar_tabelas, inserir_categorias, inserir_itens, adicionar_combo, listar_menu, listar_combos, visualizar_tabela, drop_tabela, resetar_banco, visualizar_banco, atualizar_item, deletar_itens

#resetar_banco()
#criar_tabelas()
#inserir_categorias()


# Exemplo de como adicionar itens:
#inserir_itens('X-Boladao', '2 carnes, 2 ovos, bacon, calabresa, queijo, salada, batata palha, ketchup, maionese da casa e molho Billy Jack', 15.00, './assets/X-Boladão.png', 1)
inserir_itens("Guaravita", "Suco de guaraná natural", 2.00, "guaravita.jpg", 2)
#inserir_itens("Batata pequena", "Porção de batata frita crocante", 3.00, "batata.jpg", 4)

# Exemplo de como inserir combo: 
#adicionar_combo("Combo X-Boladao", "X-Boladao", "Guaravita", "Batata pequena", "burguer-do-alto/Burguer-do-Alto/assets/Combo x-boladão.jpeg")



#atualizar_item('guaraviton', nome='guaravita', preco=2.00)



deletar_itens("Guaravita")

#visualizar_tabela("categorias")
listar_menu()
