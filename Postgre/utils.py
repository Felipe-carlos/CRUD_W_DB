import tkinter as tk
from tkinter import messagebox,ttk
import psycopg2


def conectar():
    """
    Função para conectar ao servidor
    """
    try:
        conn = psycopg2.connect(
            database='crud_python',
            host ='localhost',
            user ='felipe',
            password='python_CRUD'
        )
        return conn
    except psycopg2.Error as err:
        messagebox.showinfo(f"Erro de conexão ao Postgre Server: {err}")


def desconectar(conn):
    """ 
    Função para desconectar do servidor.
    """
    if conn:
        conn.close()
    

def listar():
    """
    Função para listar os produtos
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    desconectar(conn)
    
    if produtos:  # Verifica se a lista de produtos não está vazia
        # Cria a janela de listagem
        listar_window = tk.Toplevel()
        listar_window.title("Lista de Produtos")

        # Cria a tabela
        tree = ttk.Treeview(listar_window, columns=("ID", "Produto", "Preço", "Estoque"), show='headings')

        # Definir os cabeçalhos
        tree.heading("ID", text="ID")
        tree.heading("Produto", text="Produto")
        tree.heading("Preço", text="Preço")
        tree.heading("Estoque", text="Estoque")

        # Adicionar as linhas
        for produto in produtos:
            tree.insert("", tk.END, values=produto)

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

        conn = conectar()
        cursor = conn.cursor()
        
        print(nome,preco,estoque)
        try:
            cursor.execute(f"INSERT INTO produtos (nome, preco, estoque) VALUES ('{nome}',{preco},{estoque})")
            conn.commit()
            inserir_window.destroy()
            messagebox.showinfo("Sucesso", "Produto inserido com sucesso")
        except psycopg2.Error as err:
            messagebox.showerror("Erro", f"Erro ao inserir produto: {err}")
            conn.rollback()
        
        desconectar(conn)

    btn_salvar = tk.Button(inserir_window, text="Salvar", command=salvar)
    btn_salvar.pack(pady=10)
    

def atualizar():
    """
    Função para atualizar um produto
    """
    conn = conectar()
    cursor = conn.cursor()

    atualizar_window = tk.Toplevel()
    atualizar_window.title("Atualização de Produtos")

    tk.Label(atualizar_window, text="id do Produto:").pack(pady=5)
    id_entry = tk.Entry(atualizar_window)
    id_entry.pack(pady=5)

    tk.Label(atualizar_window, text="Nome do Produto:").pack(pady=5)
    nome_entry = tk.Entry(atualizar_window)
    nome_entry.pack(pady=5)

    tk.Label(atualizar_window, text="Preço:").pack(pady=5)
    preco_entry = tk.Entry(atualizar_window)
    preco_entry.pack(pady=5)

    tk.Label(atualizar_window, text="Estoque:").pack(pady=5)
    estoque_entry = tk.Entry(atualizar_window)
    estoque_entry.pack(pady=5)

    def atualizar():
        produto_id = id_entry.get()
        nome = nome_entry.get()
        preco = preco_entry.get()
        estoque = estoque_entry.get()

        # Verifica se o ID foi preenchido
        if not produto_id:
            messagebox.showwarning("ID Vazio", "O ID do produto é obrigatório para a atualização.")
            return

        # Monta a query de atualização dinamicamente
        atualizacoes = []
        valores = []

        if nome:
            atualizacoes.append("nome = %s")
            valores.append(nome)

        if preco:
            try:
                preco = float(preco)
                atualizacoes.append("preco = %s")
                valores.append(preco)
            except ValueError:
                messagebox.showerror("Erro", "Preço deve ser um número decimal")
                return

        if estoque:
            try:
                estoque = int(estoque)
                atualizacoes.append("estoque = %s")
                valores.append(estoque)
            except ValueError:
                messagebox.showerror("Erro", "Estoque deve ser um número inteiro")
                return

        # Verifica se ao menos um campo foi preenchido
        if not atualizacoes:
            messagebox.showwarning("Campos vazios", "Pelo menos um campo deve ser preenchido para a atualização.")
            return

        valores.append(produto_id)  
        query = f"UPDATE produtos SET {', '.join(atualizacoes)} WHERE id = %s"

        try:
            cursor.execute(query, tuple(valores))
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso")
            atualizar_window.destroy()
        except psycopg2.Error as err:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {err}")
            conn.rollback()

        desconectar(conn)


    btn_salvar = tk.Button(atualizar_window, text="Atualizar", command=atualizar)
    btn_salvar.pack(pady=10)

def deletar():
    """
    Função para deletar um produto
    """  
    conn = conectar()
    cursor = conn.cursor()

    deletar_window = tk.Toplevel()
    deletar_window.title("Deletar Produto")

    tk.Label(deletar_window, text="id do Produto:").pack(pady=5)
    id_entry = tk.Entry(deletar_window)
    id_entry.pack(pady=5)
    
    def deletar():
        produto_id = id_entry.get()

        # Verifica se o ID foi preenchido
        if not produto_id:
            messagebox.showwarning("ID Vazio", "O ID do produto é obrigatório para a atualização.")
            return
        
        try:
            # Usando parâmetros SQL para evitar SQL injection
            cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
            if cursor.rowcount == 0:
                messagebox.showwarning("Erro", "Produto com esse ID não foi encontrado.")
            else:
                conn.commit()
                messagebox.showinfo("Sucesso", "Produto deletado com sucesso")
                deletar_window.destroy()  # Fecha a janela após a deleção
        except psycopg2.Error as err:
            messagebox.showerror("Erro", f"Erro ao deletar produto: {err}")
            conn.rollback()

    btn_salvar = tk.Button(deletar_window, text="deletar", command=deletar)
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
