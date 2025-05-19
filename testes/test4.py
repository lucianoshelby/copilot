from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
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
    os_input = input("Digite o número da OS do GSPN (10 dígitos): ").strip()
    
    # URL da OS no GSPN
    url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_input}#tabInfoHref"
    driver.get(url_gspn)
    
    time.sleep(5)  # Aguarda carregamento da página

    # 🟢 Expandir a primeira tabela ("Informações gerais")
    try:
        botao_expandir_geral = driver.find_element(By.XPATH, "//tr[@onclick=\"javascript: toggleTable('Main');\"]")
        botao_expandir_geral.click()
        time.sleep(2)
    except:
        print("⚠️ Não foi possível expandir a tabela de Informações gerais.")

    # 🟢 Expandir a segunda tabela ("Informações do produto")
    try:
        botao_expandir_produto = driver.find_element(By.XPATH, "//tr[@onclick=\"javascript: initProductTab();\"]")
        botao_expandir_produto.click()
        time.sleep(2)
    except:
        print("⚠️ Não foi possível expandir a tabela de Informações do produto.")

    # 🟢 Capturar a data de compra
    try:
        data_compra = driver.find_element(By.ID, "PURCHASE_DATE").get_attribute("value")
    except:
        data_compra = "Não encontrado"

    # 🟢 Capturar o status da garantia
    try:
        status_garantia = driver.find_element(By.ID, "IN_OUT_WTY").get_attribute("value")
    except:
        status_garantia = "Não encontrado"

    # 🟢 Capturar a data de fim da garantia calculada pelo GSPN
    try:
        data_fim_garantia = driver.find_element(By.ID, "NEW_LABOR_WT_D").get_attribute("value")
    except:
        data_fim_garantia = "Não encontrado"

    # 🟢 Capturar o número da OS interna
    try:
        os_interna = driver.find_element(By.ID, "ASC_JOB_NO").get_attribute("value")
    except:
        os_interna = "Não encontrado"

    # 🟢 Capturar o status da OS no GSPN
    try:
        select_status = Select(driver.find_element(By.ID, "STATUS"))
        status_gspn = select_status.first_selected_option.text.strip()
    except:
        status_gspn = "Não encontrado"

    # 🟢 Capturar o motivo da pendência
    try:
        select_motivo = Select(driver.find_element(By.ID, "REASON"))
        motivo_pendencia = select_motivo.first_selected_option.text.strip()
    except:
        motivo_pendencia = "Não encontrado"

    # 🟢 Capturar peças inseridas no GSPN
    pecas_gspn = []
    try:
        linhas_pecas = driver.find_elements(By.XPATH, "//tbody[@id='partsTableBody']/tr")
        for linha in linhas_pecas:
            try:
                codigo_peca = linha.find_element(By.ID, "PARTS_CODE").get_attribute("value")
                num_pedido = linha.find_element(By.ID, "PO_NO").get_attribute("value") if linha.find_element(By.ID, "PO_NO").get_attribute("value") else "Não existe"
                num_entrega = linha.find_element(By.ID, "INVOICE_NO").get_attribute("value") if linha.find_element(By.ID, "INVOICE_NO").get_attribute("value") else "Não existe"
                pecas_gspn.append({"codigo": codigo_peca, "pedido": num_pedido, "entrega": num_entrega})
            except:
                continue
    except:
        pecas_gspn = "Não encontrado"

    # 🟢 Capturar a data do GI
    try:
        data_gi = driver.find_element(By.XPATH, "//td[@class='td_ac']").text.strip()
    except:
        data_gi = "Não encontrado"

    # 🟢 Expandir e capturar anexos
    anexos = []
    try:
        botao_expandir_anexos = driver.find_element(By.XPATH, "//tr[@onclick=\"javascript: toggleTable('Attach');\"]")
        botao_expandir_anexos.click()
        time.sleep(2)

        anexos_elementos = driver.find_elements(By.XPATH, "//td[@class='td_ac']/input[@id='docTypeCode']")
        for anexo in anexos_elementos:
            anexos.append(anexo.get_attribute("value"))

        if not anexos:
            anexos = "Nenhum anexo encontrado"
    except:
        anexos = "Erro ao capturar anexos"

    # 🟢 Exibir as informações no console
    print("\n🔹 **Informações da OS no GSPN**")
    print(f"📌 Data de Compra: {data_compra}")
    print(f"📌 Status da Garantia: {status_garantia}")
    print(f"📌 Fim da Garantia (GSPN): {data_fim_garantia}")
    print(f"📌 Número da OS Interna: {os_interna}")
    print(f"📌 Status da OS no GSPN: {status_gspn}")
    print(f"📌 Motivo da Pendência: {motivo_pendencia}")
    print(f"📌 Peças inseridas no GSPN: {pecas_gspn}")
    print(f"📌 Data do GI: {data_gi}")
    print(f"📌 Anexos: {anexos}")

finally:
    input("\nPressione ENTER para fechar o navegador...")
    driver.quit()
