import tkinter as tk
from tkinter import messagebox, ttk
from utils import buscar_mercado_livre, carregar_historico, limpar_historico
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from fpdf import FPDF
import pandas as pd
import numpy as np
import pyperclip
from utils import abrir_link
import requests

def buscar():
    produto = entrada.get()
    if not produto:
        messagebox.showwarning("Aviso", "Digite um nome de produto para buscar.")
        return
   
    global resultados
    resultados = buscar_mercado_livre(produto)
    if resultados:
        tree.delete(*tree.get_children())  # Limpar resultados anteriores
        
        # Convertendo os resultados para um DataFrame do Pandas
        df = pd.DataFrame(resultados)

        # Adicionando as informações na Treeview
        for item in resultados:
            tree.insert("", "end", values=(item["title"], f'R$ {item["price"]:.2f}', item["seller"]["nickname"], item["permalink"]))

        # Calculando as estatísticas com o Pandas
        if not df.empty:
            media = df["price"].mean()
            maior = df["price"].max()
            menor = df["price"].min()
            variancia_val = df["price"].var()

            # Atualizando os valores na interface
            media_preco.config(text=f"Média: R$ {media:.2f}")
            maior_preco.config(text=f"Maior: R$ {maior:.2f}")
            menor_preco.config(text=f"Menor: R$ {menor:.2f}")
            
    else:
        messagebox.showinfo("Resultado", "Nenhum produto encontrado.")
        
def ver_historico():
    historico = carregar_historico()
    if not historico:
        messagebox.showinfo("Histórico", "Nenhum histórico de buscas encontrado.")
        return
    historico_texto = "\n".join([f"{h['data']} - {h['produto']}" for h in historico])
    messagebox.showinfo("Histórico de Buscas", historico_texto)

def confirmar_limpeza():
    """Exibe uma janela de confirmação antes de limpar o histórico."""
    resposta = messagebox.askyesno("Confirmar", "Você tem certeza de que deseja limpar o histórico de buscas?")
    if resposta:
        sucesso = limpar_historico()
        if sucesso:
            messagebox.showinfo("Sucesso", "Histórico limpo com sucesso.")
        else:
            messagebox.showwarning("Aviso", "Erro ao limpar o histórico.")

def gerar_relatorio():
    if not resultados:
        messagebox.showwarning("Aviso", "Nenhum dado para gerar relatório.")
        return
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Relatório de Análise de Preços", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(60, 10, "Nome", border=1)
    pdf.cell(40, 10, "Preço", border=1)
    pdf.cell(60, 10, "Loja", border=1)
    pdf.ln()
    
    for item in resultados:
        pdf.cell(60, 10, item["title"][:30], border=1)
        pdf.cell(40, 10, f'R$ {item["price"]:.2f}', border=1)
        pdf.cell(60, 10, item["seller"]["nickname"][:30], border=1)
        pdf.ln()
    
    pdf.output("relatorio.pdf")
    messagebox.showinfo("Sucesso", "Relatório gerado como relatorio.pdf")
    
    
def exportar_excel():
    if not resultados:
        messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
        return
    
    dados_essenciais = [{
        "Nome": item["title"],
        "Vendedor": item["seller"]["nickname"],
        "Data": item.get("date", "N/A"),
        "Quantidade": item.get("available_quantity", "N/A"),
        "Endereço": item.get("address", {}).get("state_name", "N/A"),
        "Preço": item["price"],
        "Link": item["permalink"],
        "Domain ID": item.get("domain_id", "N/A"),
        "Imagem": item.get("thumbnail", "N/A")
    } for item in resultados]
    
    df = pd.DataFrame(dados_essenciais)
    df.to_excel("precos.xlsx", index=False)
    messagebox.showinfo("Sucesso", "Dados essenciais exportados para precos.xlsx")


# Interface gráfica
root = tk.Tk()
root.title("Analisador de Preços")
root.geometry("900x600")

# Paleta de cores
cor_fundo = "#f0f0f0"
cor_destaque = "#ffcccc"
cor_botao = "#4caf50"
cor_hover = "#45a049"

root.configure(bg=cor_fundo)

frame_esquerdo = tk.Frame(root, bg="#F8F8F8")
frame_esquerdo.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

frame_direito = tk.Frame(root, bg="#F8F8F8")
frame_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Adicionando o nome da aplicação acima da barra de busca
titulo_app = tk.Label(frame_esquerdo, text="Analisador de Preços", font=("Arial", 18, "bold"), bg=cor_fundo)
titulo_app.pack(pady=(10, 5), padx=10)  # Espaçamento superior

entrada = tk.Entry(frame_esquerdo, font=("Arial", 14))
entrada.pack(pady=5, padx=10, fill=tk.X)

frame_botoes = tk.Frame(frame_esquerdo, bg="#F8F8F8")
frame_botoes.pack(pady=10, padx=10, anchor="w")

botoes = [
    ("Buscar", buscar, cor_botao),
    ("Histórico", ver_historico, cor_botao),
    ("Exportar Excel", exportar_excel, cor_botao),
    ("Gerar Relatório PDF", gerar_relatorio, cor_botao),
    ("Limpar Histórico", confirmar_limpeza, cor_botao)
]

for texto, comando, cor in botoes:
    tk.Button(frame_botoes, text=texto, font=("Arial", 12), bg=cor, fg="white", relief=tk.FLAT, command=comando).pack(fill=tk.X, pady=5, ipadx=10, ipady=10)

# Criando frame para os dados estatísticos
frame_dados = tk.Frame(frame_direito, bg="#F8F8F8")
frame_dados.pack(fill=tk.X, pady=10)

# Criando um frame para centralizar a média
frame_media = tk.Frame(frame_dados, bg="#F8F8F8")
frame_media.pack(fill=tk.X)

# Label média
label_media = tk.Label(frame_media, text="Média", font=("Arial", 12, "bold"), bg="#F8F8F8")
label_media.pack()

# Valor  média
media_preco = tk.Label(frame_media, text="-", font=("Arial", 14, "bold"), bg="#F8F8F8", fg="blue")
media_preco.pack()

# Criando um frame para alinhar maior e menor preço
frame_maior_menor = tk.Frame(frame_dados, bg="#F8F8F8")
frame_maior_menor.pack(fill=tk.X, pady=5)

# Maior preço (esquerda)
frame_maior = tk.Frame(frame_maior_menor, bg="#F8F8F8")
frame_maior.pack(side=tk.LEFT, expand=True, padx=20)

label_maior = tk.Label(frame_maior, text="Maior", font=("Arial", 12, "bold"), bg="#F8F8F8")
label_maior.pack()

maior_preco = tk.Label(frame_maior, text="-", font=("Arial", 14, "bold"), bg="#F8F8F8", fg="green")
maior_preco.pack()

# Menor preço (direita)
frame_menor = tk.Frame(frame_maior_menor, bg="#F8F8F8")
frame_menor.pack(side=tk.RIGHT, expand=True, padx=20)

label_menor = tk.Label(frame_menor, text="Menor", font=("Arial", 12, "bold"), bg="#F8F8F8")
label_menor.pack()

menor_preco = tk.Label(frame_menor, text="-", font=("Arial", 14, "bold"), bg="#F8F8F8", fg="red")
menor_preco.pack()


# Criando treeviwe
colunas = ("Nome", "Preço", "Vendedor", "Link")

# Criando frame para treeview e rolagens
frame_tree = tk.Frame(frame_direito, bg="#F8F8F8")
frame_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Criando a barra de rolagem vertical
scrollbar_y = tk.Scrollbar(frame_tree, orient="vertical")
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

# Criando a barra de rolagem horizontal
scrollbar_x = tk.Scrollbar(frame_tree, orient="horizontal")
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Criando a Treeview com rolagem
tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", height=8, 
                     yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configurando as barras de rolagem
scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

# Ajustando as colunas
tree.heading("Nome", text="Nome")
tree.heading("Preço", text="Preço")
tree.heading("Vendedor", text="Vendedor")
tree.heading("Link", text="Link")

tree.column("Nome", width=300, anchor="center")
tree.column("Preço", width=100, anchor="center")
tree.column("Vendedor", width=150, anchor="center")
tree.column("Link", width=400, anchor="center")  # Aumentei para forçar a rolagem

def clicar_link(event):
    """Abre o link do produto no navegador ao clicar na coluna Link."""
    item_selecionado = tree.selection()
    if item_selecionado:
        item = tree.item(item_selecionado)
        link = item["values"][3]  # Pega o link do produto
        abrir_link(link)

# Função para copiar o link ao clicar com o botão direito
def copiar_link(event):
    """Copia o link do produto para a área de transferência."""
    item_selecionado = tree.selection()
    if item_selecionado:
        item = tree.item(item_selecionado)
        link = item["values"][3]
        pyperclip.copy(link)
        messagebox.showinfo("Copiado!", "O link foi copiado para a área de transferência.")


# Associar eventos
tree.bind("<Double-1>", clicar_link)  # Duplo clique abre o link
tree.bind("<Button-3>", copiar_link)  # Clique direito copia o link

root.mainloop()

