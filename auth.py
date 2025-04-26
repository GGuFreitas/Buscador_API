import requests
import json
import time

CLIENT_ID = "5216409836889018"
CLIENT_SECRET = "5KqnZkwrEJXfNi5zGCx2I1CK3bx2Gpp8"

HISTORICO_ARQUIVO = "historico_buscas.json"
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Escopos para acessar Google Sheets e Drive
CLIENT_ID = "5216409836889018"
CLIENT_SECRET = "5KqnZkwrEJXfNi5zGCx2I1CK3bx2Gpp8"
HISTORICO_ARQUIVO = "historico_buscas.json"

# Configuração do Google Sheets
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

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
    print("Access Token Atual:", access_token)

except Exception as e:
    print(f"Erro ao acessar Google Sheets: {e}")
    print("Verifique:")
    print("1. Se o arquivo credenciais.json está correto")
    print("2. Se a planilha foi compartilhada com o e-mail do serviço")
    print("3. Se os escopos de permissão estão corretos")
    exit()


def renovar_token():
    url = "https://api.mercadolibre.com/oauth/token"

    # Busca o refresh_token do arquivo salvo
    refresh_token_atual = None
    try:
        with open("token.json", "r") as f:
            tokens_salvos = json.load(f)
            refresh_token_atual = tokens_salvos.get("refresh_token")
    except Exception as e:
        print("Erro ao ler token.json:", e)
        return None

    if not refresh_token_atual:
        print("Nenhum refresh_token encontrado para renovar o access_token.")
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token_atual
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json()
        data["created_at"] = int(time.time())
        with open("token.json", "w") as f:
            json.dump(data, f, indent=4)
        return data["access_token"]
    else:
        print("Erro ao renovar token:", response.status_code, response.text)
        return None


def obter_token_valido():
    """Carrega o token salvo e renova se necessário"""
    try:
        with open("token.json", "r") as f:
            content = f.read().strip()
            if not content:
                return renovar_token()
            tokens = json.loads(content)

        created_at = tokens.get("created_at", 0)
        expires_in = tokens.get("expires_in", 0)
        agora = int(time.time())

        # Se o token expirou (6h ou mais), renovar
        if agora > created_at + expires_in:
            return renovar_token()

        return tokens["access_token"]

    except (FileNotFoundError, json.JSONDecodeError):
        return renovar_token()


def testar_token(access_token):
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Token válido!")
    else:
        print(f"Token inválido ou expirado. Status Code: {response.status_code}")
        print(response.text)


