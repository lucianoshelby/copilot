import os
import json
import random
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

MAIN_PROFILE_PATH = "C:/selenium-profile"
COOKIES_TEMP_PATH = "cookies_temp.json"
CHROME_PORT = "9222"  # Porta de depuração

# Configura ou conecta ao Chrome do perfil principal
def conectar_perfil_principal():
    """Conecta ao Chrome aberto ou abre uma nova instância se estiver fechado."""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    
    try:
        # Tenta conectar ao Chrome já aberto
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Conectado ao Chrome existente do perfil principal")
        return driver
    except Exception as e: print(f'Erro ao conectar ao chrome ja aberto: {e}')
    """except Exception as e:
        print(f"ℹ️ Chrome não está aberto na porta {CHROME_PORT}. Abrindo nova instância...")
        
        # Abre o Chrome com debugging se não estiver rodando
        chrome_cmd = [
            "chrome.exe",
            f"--remote-debugging-port={CHROME_PORT}",
            f"--user-data-dir={MAIN_PROFILE_PATH}",
            "--profile-directory=Default"
        ]
        subprocess.Popen(chrome_cmd, shell=True)  # Inicia o Chrome em background
        time.sleep(3)  # Aguarda o Chrome abrir (ajuste se necessário)
        input('pausa')
        # Tenta conectar novamente
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Nova instância do Chrome aberta e conectada")
            return driver
        except Exception as e:
            print(f"❌ Erro ao abrir ou conectar ao Chrome: {e}")
            return None"""

# Captura todos os cookies do perfil principal
def capturar_todos_cookies():
    driver = conectar_perfil_principal()
    if not driver:
        return
    
    try:
        cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})
        todos_cookies = cookies["cookies"]
        
        with open(COOKIES_TEMP_PATH, "w") as file:
            json.dump(todos_cookies, file, indent=4)
        print(f"✅ Todos os cookies capturados e salvos em {COOKIES_TEMP_PATH}")
        
    except Exception as e:
        print(f"⚠️ Erro ao capturar cookies: {e}")
    finally:
        driver.quit()  # Fecha a conexão, mas não o Chrome

# Configura drivers de produção
def configurar_driver_producao():
    chrome_options = Options()
    profile_id = random.randint(1000, 9999)
    temp_profile_path = f"C:/selenium-profile/temp-{profile_id}"
    os.makedirs(temp_profile_path, exist_ok=True)
    
    chrome_options.add_argument(f"user-data-dir={temp_profile_path}")
    chrome_options.add_argument("profile-directory=Default")
    driver = webdriver.Chrome(options=chrome_options)
    print(f"✅ Driver de produção temp-{profile_id} criado")
    carregar_todos_cookies(driver)
    return driver

# Carrega todos os cookies nas instâncias de produção
def carregar_todos_cookies(driver, caminho_arquivo=COOKIES_TEMP_PATH):
    if not os.path.exists(caminho_arquivo):
        capturar_todos_cookies()
        
    
    with open(caminho_arquivo, "r") as file:
        cookies = json.load(file)
    
    for cookie in cookies:
        try:
            driver.execute_cdp_cmd("Network.setCookie", cookie)
        except Exception as e:
            print(f"⚠️ Cookie {cookie.get('name')} ignorado: {e}")
    print("✅ Todos os cookies carregados na instância")

def save_received_cookies(cookies_data):
    """Salva a lista de dicionários de cookies recebida no arquivo JSON."""
    # Validação básica do formato esperado (lista de dicionários)
    if not isinstance(cookies_data, list):
        print("⚠️ Erro API: Formato de dados inválido. Esperava uma lista.")
        return False, "Formato de dados inválido: esperava uma lista."
    if cookies_data and not all(isinstance(c, dict) and 'name' in c for c in cookies_data):
         print("⚠️ Erro API: Estrutura de cookie inválida na lista.")
         return False, "Estrutura de cookie inválida na lista."

    try:
        # Garante que o diretório (se houver) existe
        dir_name = os.path.dirname(COOKIES_TEMP_PATH)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # Escreve a lista recebida no arquivo, substituindo o conteúdo anterior
        with open(COOKIES_TEMP_PATH, "w") as file:
            json.dump(cookies_data, file, indent=4)
        print(f"✅ Cookies recebidos via API e salvos em {COOKIES_TEMP_PATH}")
        return True, "Cookies atualizados com sucesso via API."
    except Exception as e:
        print(f"⚠️ Erro API: Falha ao salvar cookies recebidos: {e}")
        return False, f"Erro do servidor ao salvar cookies: {e}"

# Exemplo de uso
if __name__ == "__main__":
    # Passo 1: Conecta ou abre o Chrome e captura cookies
    capturar_todos_cookies()
    
    # Passo 2: Crie instâncias de produção
    drivers = []
    for i in range(1):
        driver = configurar_driver_producao()
        drivers.append(driver)
        driver.get("https://gspn6.samsungcsportal.com/main.jsp")
        print(f"Instância {i} acessou site1")
        driver.get("https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID=4172172477")
        print(f"Instância {i} acessou site2")
    
    for driver in drivers:
        driver.quit()