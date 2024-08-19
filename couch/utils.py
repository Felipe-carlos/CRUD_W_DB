import tkinter as tk
from tkinter import messagebox,ttk
import socket
import couchdb


def conectar():
    """
    Função para conectar ao servidor
    """

    conn = couchdb.Server('http://admin:admin@localhost:5984/')

    banco = 'crud_python'

    if banco in conn:
        db = conn[banco]
        return db
    else:
        try:
            db = conn.create(banco)
            return db
        except socket.gaierror as err:
             messagebox.showinfo("Erro ", f"{err}")
        except couchdb.http.Unauthorized as f:
            messagebox.showinfo("Erro ", f"{f}")
        except ConnectionRefusedError as g:
            messagebox.showinfo("Erro ", f"{g}")


def desconectar(conn):
    """ 
    Função para desconectar do servidor.
    """
    pass
    
def listar():
    """
    Função para listar os produtos
    """
    db = conectar()
    produtos ={}
    
    if db.info()['doc_count']> 0:
        for doc in db:
            _id = db[doc]['_id']
            produtos[_id] = {}
            produtos[_id]['nome'] = db[doc]['nome']
            produtos[_id]['preco'] = db[doc]['preco']
            produtos[_id]['estoque'] = db[doc]['estoque']
            produtos[_id]['Rev'] = db[doc]['_rev']
    else:
        messagebox.showinfo("Tabela Vazia", "Não existem produtos para serem visualizados")
        return  # Encerra a função se não houver produtos

    

    if produtos:  # Verifica se há produtos para listar
        # Cria a janela de listagem
        listar_window = tk.Toplevel()
        listar_window.title("Lista de Produtos")

        # Cria a tabela
        tree = ttk.Treeview(listar_window, columns=("ID","Rev", "Produto", "Preço", "Estoque"), show='headings')

        # Definir os cabeçalhos
        tree.heading("ID", text="ID")
        tree.heading("Rev", text="Rev")
        tree.heading("Produto", text="Produto")
        tree.heading("Preço", text="Preço")
        tree.heading("Estoque", text="Estoque")

        # Adicionar as linhas
        for produto in produtos:
            tree.insert("", tk.END, values=(str(produto), produtos[produto]['Rev'],produtos[produto]['nome'], produtos[produto]['preco'], produtos[produto]['estoque']))

        # Adicionar a tabela à janela
        tree.pack()
    else:
        messagebox.showinfo("Tabela Vazia", "Não existem produtos para serem visualizados")
    

def inserir():
    """
    Função para inserir um produto
    """  
    inserir_window = tk.Toplevel()
    inserir_window.title("Inserir Produto")

    tk.Label(inserir_window, text="Nome do Produto:").pack(pady=5)
    nome_entry = tk.Entry(inserir_window)
    nome_entry.pack(pady=5)

    tk.Label(inserir_window, text="Preço:").pack(pady=5)
    preco_entry = tk.Entry(inserir_window)
    preco_entry.pack(pady=5)

    tk.Label(inserir_window, text="Estoque:").pack(pady=5)
    estoque_entry = tk.Entry(inserir_window)
    estoque_entry.pack(pady=5)

    def salvar():
        nome = nome_entry.get()
        preco = preco_entry.get()
        estoque = estoque_entry.get()
        # Valida se os campos não estão vazios
        if not nome or not preco or not estoque:
            messagebox.showwarning("Campos vazios", "Todos os campos devem ser preenchidos")
            return

        try:
            preco = float(preco)
            estoque = int(estoque)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número decimal e estoque deve ser um número inteiro")
            return

        db = conectar()
                
        try:
            db.save({
                "nome": nome,
                "preco": preco,
                "estoque": estoque
                })
            inserir_window.destroy()
            messagebox.showinfo("Sucesso", "Produto inserido com sucesso")
        except socket.gaierror as err:
            messagebox.showerror("Erro", f"Erro ao inserir produto: {err}")
            

    btn_salvar = tk.Button(inserir_window, text="Salvar", command=salvar)
    btn_salvar.pack(pady=10)
    
def atualizar():
    """
    Função para atualizar um produto
    """
    db = conectar()

    atualizar_window = tk.Toplevel()
    atualizar_window.title("Atualização de Produtos")

    # Obter todos os IDs de produtos disponíveis no banco de dados
    try:
        produtos = [doc for doc in db]
        ids_produtos = [str(db[doc]['_id']) for doc in produtos]
    except Exception as err:
        messagebox.showerror("Erro", f"Erro ao acessar os produtos: {err}")
        return

    if len(ids_produtos) > 0:
        # Criar o dropdown (OptionMenu) para selecionar o ID
        tk.Label(atualizar_window, text="Selecione o ID do Produto:").pack(pady=5)
        selected_id = tk.StringVar(atualizar_window)
        selected_id.set(ids_produtos[0] if ids_produtos else "")  # Seleciona o primeiro ID por padrão

        id_menu = tk.OptionMenu(atualizar_window, selected_id, *ids_produtos)
        id_menu.pack(pady=5)

        # Campos para Nome, Preço e Estoque
        tk.Label(atualizar_window, text="Nome do Produto:").pack(pady=5)
        nome_entry = tk.Entry(atualizar_window)
        nome_entry.pack(pady=5)

        tk.Label(atualizar_window, text="Preço:").pack(pady=5)
        preco_entry = tk.Entry(atualizar_window)
        preco_entry.pack(pady=5)

        tk.Label(atualizar_window, text="Estoque:").pack(pady=5)
        estoque_entry = tk.Entry(atualizar_window)
        estoque_entry.pack(pady=5)
    else:
        messagebox.showerror("Database vazio", "Não existem dados para serem atualizados")
        return

    def realizar_atualizacao():
        produto_id = selected_id.get()  # Obter o ID selecionado no dropdown
        nome = nome_entry.get()
        preco = preco_entry.get()
        estoque = estoque_entry.get()

        # Verifica se o ID foi preenchido
        if not produto_id:
            messagebox.showwarning("ID Vazio", "O ID do produto é obrigatório para a atualização.")
            return

        # Monta o dicionário de atualização dinamicamente
        atualizacoes = {}

        if nome:
            atualizacoes["nome"] = nome

        if preco:
            try:
                preco = float(preco)
                atualizacoes["preco"] = preco
            except ValueError:
                messagebox.showerror("Erro", "Preço deve ser um número decimal")
                return

        if estoque:
            try:
                estoque = int(estoque)
                atualizacoes["estoque"] = estoque
            except ValueError:
                messagebox.showerror("Erro", "Estoque deve ser um número inteiro")
                return

        # Verifica se ao menos um campo foi preenchido
        if not atualizacoes:
            messagebox.showwarning("Campos vazios", "Pelo menos um campo deve ser preenchido para a atualização.")
            return

        try:
            # Busca o documento pelo ID
            produto = db[produto_id]

            # Atualiza os campos do documento
            produto.update(atualizacoes)

            # Salva as atualizações no CouchDB
            db.save(produto)
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso")
            atualizar_window.destroy()
        except Exception as err:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {err}")

    # Botão para salvar as alterações
    btn_salvar = tk.Button(atualizar_window, text="Atualizar", command=realizar_atualizacao)
    btn_salvar.pack(pady=10)

def deletar():
    """
    Função para deletar um produto
    """  
    db = conectar()

    deletar_window = tk.Toplevel()
    deletar_window.title("Deletar Produto")

    # Obter todos os produtos do banco de dados
    try:
        produtos = [doc for doc in db]
        nomes_produtos = [(doc, db[doc]['nome']) for doc in produtos]  # Lista de (id, nome)
    except Exception as err:
        messagebox.showerror("Erro", f"Erro ao acessar os produtos: {err}")
        return

    if not nomes_produtos:
        messagebox.showinfo("Tabela Vazia", "Não existem produtos para deletar.")
        deletar_window.destroy()
        return

    # Criar o dropdown (OptionMenu) para selecionar o produto
    tk.Label(deletar_window, text="Selecione o Produto:").pack(pady=5)
    selected_produto = tk.StringVar(deletar_window)
    selected_produto.set(nomes_produtos[0][1])  # Seleciona o primeiro produto por padrão

    produto_menu = tk.OptionMenu(deletar_window, selected_produto, *[produto[1] for produto in nomes_produtos])
    produto_menu.pack(pady=5)

    def realizar_delecao():
        # Encontra o ID correspondente ao nome selecionado
        nome_produto = selected_produto.get()
        produto_id = None
        for produto in nomes_produtos:
            if produto[1] == nome_produto:
                produto_id = produto[0]
                break

        if not produto_id:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        try:
            # Executa a deleção no CouchDB
            produto = db[produto_id]
            db.delete(produto)
            messagebox.showinfo("Sucesso", "Produto deletado com sucesso")
            deletar_window.destroy()
        except Exception as err:
            messagebox.showerror("Erro", f"Erro ao deletar produto: {err}")

    # Botão para deletar o produto
    btn_salvar = tk.Button(deletar_window, text="Deletar", command=realizar_delecao)
    btn_salvar.pack(pady=10)


def menu():
    """
    Função para gerar o menu inicial com interface gráfica
    """
    # Cria a janela principal
    root = tk.Tk()
    root.title("Gerenciamento de Produtos")

    # Cria o título do menu
    label = tk.Label(root, text="==============Gerenciamento de Produtos==============")
    label.pack(pady=10)

    # Cria o botão de listar produtos
    btn_listar = tk.Button(root, text="Listar produtos", command=listar)
    btn_listar.pack(pady=5)

    # Cria o botão de inserir produtos
    btn_inserir = tk.Button(root, text="Inserir produtos", command=inserir)
    btn_inserir.pack(pady=5)

    # Cria o botão de atualizar produtos
    btn_atualizar = tk.Button(root, text="Atualizar produto", command=atualizar)
    btn_atualizar.pack(pady=5)

    # Cria o botão de deletar produtos
    btn_deletar = tk.Button(root, text="Deletar produto", command=deletar)
    btn_deletar.pack(pady=5)

    # Inicia o loop da interface gráfica
    root.mainloop()
