import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

# Configuração do Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def obter_token_da_planilha():
    """Obtém o access token da planilha do Google Sheets"""
    try:
        # Autenticação
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
        client = gspread.authorize(creds)

        # Abrir a planilha pelo ID
        spreadsheet = client.open_by_key('1lO1n2GBNeXKX7KiLRbwKGT3YjSevNuxq-R3LTXeu-Lo')
        
        # Acessar a aba "access"
        page_access = spreadsheet.worksheet('access')
        
        # Pegar o Access Token da célula B2
        access_token = page_access.acell('B2').value
        print("Access Token obtido da planilha com sucesso!")
        return access_token

    except Exception as e:
        print(f"Erro ao obter token da planilha: {e}")
        return None