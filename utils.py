import json
import os
import time
import requests
import pandas as pd
from fpdf import FPDF
from auth import obter_token_valido
import webbrowser

def abrir_link(url):
    webbrowser.open(url)
    

def buscar_mercado_livre(produto, offset=0, limit=50):
    ACCESS_TOKEN = obter_token_valido()
    if not ACCESS_TOKEN:
        return []

    url = f'https://api.mercadolibre.com/sites/MLB/search?q={produto}&offset={offset}&limit={limit}'
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        resultados = response.json()["results"]
        salvar_historico(produto, resultados)
        return resultados
    else:
        print(f"Erro ao buscar dados: {response.status_code} - {response.text}")
        return []


HISTORICO_ARQUIVO = "historico_buscas.json"

def salvar_historico(produto, resultados):
    historico = carregar_historico()

    # Extrair dados essenciais de cada item
    resultados_essenciais = []
    for item in resultados:
        dados_essenciais = {
        "Nome": item["title"],
        "Vendedor": item["seller"]["nickname"],
        "Data": item.get("date", "N/A"),
        "Quantidade": item.get("available_quantity", "N/A"),
        "Endereço": item.get("address", {}).get("state_name", "N/A"),
        "Preço": item["price"],
        "Link": item["permalink"],
        "Domain ID": item.get("domain_id", "N/A"),
        "Imagem": item.get("thumbnail", "N/A")
    } 
        resultados_essenciais.append(dados_essenciais)
    
    # Adicionar ao histórico
    historico.append({"produto": produto, "data": time.strftime("%Y-%m-%d %H:%M:%S"), "resultados": resultados_essenciais})

    # Salvar o histórico atualizado no arquivo
    with open(HISTORICO_ARQUIVO, "w") as f:
        json.dump(historico, f, indent=4)

def carregar_historico():
    if os.path.exists(HISTORICO_ARQUIVO):
        with open(HISTORICO_ARQUIVO, "r") as f:
            return json.load(f)
    return []

def limpar_historico():
    """Remove todo o histórico de buscas do arquivo JSON."""
    if os.path.exists(HISTORICO_ARQUIVO):
        with open(HISTORICO_ARQUIVO, "w") as f:
            json.dump([], f, indent=4)  # Substitui o conteúdo por uma lista vazia
        return True
    return False

def gerar_relatorio_excel(produto, resultados):
    df = pd.DataFrame(resultados)
    df.to_excel(f"{produto}_relatorio.xlsx", index=False)

def gerar_relatorio_pdf(produto, resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Relatório de {produto}", ln=True, align='C')
    
    for item in resultados:
        pdf.cell(200, 10, txt=f"{item['title']} - R$ {item['price']}", ln=True)
    
    pdf.output(f"{produto}_relatorio.pdf")