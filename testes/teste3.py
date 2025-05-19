from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configuração do Chrome com perfil do usuário
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/Gestão MX/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("profile-directory=Default")
chrome_options.add_argument("--disable-sync")

# Inicializa o WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Solicita a OS no console
    os_input = input("Digite o número da OS do COS (6 dígitos): ").strip()
    
    # URL da OS no COS
    url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_input}"
    driver.get(url_cos)
    
    time.sleep(3)  # Aguarda carregamento da página

    # 🟢 Capturar o status da OS
    try:
        status_os = driver.find_element(By.ID, "StatusAtual").text.strip()
    except:
        status_os = "Não encontrado"
    
    # 🟢 Capturar o tipo de atendimento
    try:
        tipo_atendimento = driver.find_element(By.ID, "Atendimento").text.strip()
    except:
        tipo_atendimento = "Não encontrado"

    # 🟢 Capturar as peças pedidas no GSPN
    pecas_gspn = []
    try:
        tabela_pecas = driver.find_element(By.ID, "tbPecaPedidaGSPN")
        linhas_pecas = tabela_pecas.find_elements(By.TAG_NAME, "tr")
        
        todas_entregues = True
        for linha in linhas_pecas:
            try:
                codigo_peca = linha.find_element(By.ID, "CodigoPeca").text.strip()
                status_peca = linha.find_element(By.ID, "Status").text.strip()

                if status_peca.lower() != "entregue":
                    todas_entregues = False
                    pecas_gspn.append({"codigo": codigo_peca, "status": status_peca})
            except:
                continue

        if todas_entregues:
            pecas_gspn = "Todas as peças foram entregues"

    except:
        pecas_gspn = "Não encontrado"

    # 🟢 Clicar no botão que expande a tabela de peças requisitadas
    try:
        botao_expandir = driver.find_element(By.XPATH, "//td[@onclick='BuscarDadosRequisicaoEstoquePorOS()']")
        botao_expandir.click()
        time.sleep(2)  # Espera para a tabela expandir
    except:
        print("⚠️ Botão para expandir a tabela de peças requisitadas não encontrado.")

    # 🟢 Capturar os códigos das peças requisitadas
    pecas_requisitadas = []
    try:
        codigos_pecas = driver.find_elements(By.ID, "CodigoPeca")
        for peca in codigos_pecas:
            codigo_texto = peca.text.strip()
            if "|" in codigo_texto:
                codigo_peca = codigo_texto.split("|")[0].strip()  # Pega só o código da peça
                pecas_requisitadas.append(codigo_peca)
    except:
        pecas_requisitadas = "Não encontrado"

    # 🟢 Exibir as informações no console
    print("\n🔹 **Informações da OS**")
    print(f"📌 Status da OS: {status_os}")
    print(f"📌 Tipo de Atendimento: {tipo_atendimento}")
    print(f"📌 Peças pedidas no GSPN: {pecas_gspn}")
    print(f"📌 Peças requisitadas ao estoque: {pecas_requisitadas}")

finally:
    input("\nPressione ENTER para fechar o navegador...")
    driver.quit()
