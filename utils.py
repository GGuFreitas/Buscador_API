import json
import os
import time
import requests
import pandas as pd
from fpdf import FPDF
from auth import obter_token_da_planilha
import webbrowser

HISTORICO_ARQUIVO = "historico_buscas.json"

def abrir_link(url):
    webbrowser.open(url)
    
def testar_token(access_token):
    """Testa se o token é válido"""
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Token válido!")
            return True
        else:
            print(f"❌ Token inválido. Status: {response.status_code}")
            print("Resposta:", response.text)
            return False
    except Exception as e:
        print(f"Erro ao testar token: {e}")
        return False
    
def buscar_mercado_livre(produto, offset=0, limit=50):
    access_token = obter_token_da_planilha()
    if not access_token:
        return []
    
    if not testar_token(access_token):
        print("Token inválido, não é possível fazer a busca")
        return []

    url = f'https://api.mercadolibre.com/sites/MLB/search'
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": produto,
        "offset": offset,
        "limit": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        resultados = response.json().get("results", [])
        salvar_historico(produto, resultados)
        return resultados
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na busca: {e}")
        return []

def salvar_historico(produto, resultados):
    """Salva a busca no histórico"""
    historico = carregar_historico()
    
    dados_busca = {
        "produto": produto,
        "data": time.strftime("%Y-%m-%d %H:%M:%S"),
        "resultados": []
    }
    
    # Extrair informações relevantes de cada resultado
    for item in resultados:
        dados_item = {
            "title": item.get("title", ""),
            "price": item.get("price", 0),
            "seller": item.get("seller", {}).get("nickname", ""),
            "permalink": item.get("permalink", ""),
            "thumbnail": item.get("thumbnail", ""),
            "available_quantity": item.get("available_quantity", 0),
            "condition": item.get("condition", ""),
            "address": item.get("address", {}).get("state_name", "N/A")
        }
        dados_busca["resultados"].append(dados_item)
    
    historico.append(dados_busca)
    
    try:
        with open(HISTORICO_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Erro ao salvar histórico: {e}")

def carregar_historico():
    """Carrega o histórico de buscas"""
    if os.path.exists(HISTORICO_ARQUIVO):
        try:
            with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def limpar_historico():
    """Remove todo o histórico de buscas"""
    try:
        with open(HISTORICO_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return True
    except IOError:
        return False

def gerar_relatorio_excel(produto, resultados):
    """Gera relatório em Excel"""
    try:
        df = pd.DataFrame([{
            "Nome": item["title"],
            "Preço": item["price"],
            "Vendedor": item["seller"]["nickname"],
            "Link": item["permalink"],
            "Quantidade": item.get("available_quantity", "N/A"),
            "Condição": item.get("condition", "N/A"),
            "Localização": item.get("address", {}).get("state_name", "N/A")
        } for item in resultados])
        
        df.to_excel(f"{produto}_relatorio.xlsx", index=False)
        return True
    except Exception as e:
        print(f"Erro ao gerar Excel: {e}")
        return False

def gerar_relatorio_pdf(produto, resultados):
    """Gera relatório em PDF"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Relatório de {produto}", ln=True, align='C')
        
        for item in resultados:
            pdf.cell(200, 10, txt=f"{item['title']} - R$ {item['price']:.2f}", ln=True)
        
        pdf.output(f"{produto}_relatorio.pdf")
        return True
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return False