from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

def mudar_status_ag_custo_reparo(driver):
    """Altera o status da OS para 'Aguardando confirmação do consumidor' no GSPN."""

    print("\n🔄 Mudando status para 'AG CUSTO DE REPARO'...")

    # 🟢 1. Expandir a tabela "Informações gerais"
    try:
        tabela_geral = driver.find_element(By.XPATH, "//tr[@onclick=\"javascript: toggleTable('Main');\"]")
        tabela_geral.click()
        time.sleep(1)
        print("✅ Tabela 'Informações gerais' expandida.")
    except NoSuchElementException:
        print("⚠️ Tabela 'Informações gerais' não encontrada.")

    # 🟢 2. Expandir a tabela "Informações do produto"
    try:
        tabela_produto = driver.find_element(By.XPATH, "//tr[@onclick=\"javascript: initProductTab();\"]")
        tabela_produto.click()
        time.sleep(1)
        print("✅ Tabela 'Informações do produto' expandida.")
    except NoSuchElementException:
        print("⚠️ Tabela 'Informações do produto' não encontrada.")

    # 🟢 3. Verificar o "Status da Garantia"
    try:
        status_garantia = driver.find_element(By.ID, "IN_OUT_WTY").get_attribute("value").strip()
        print(f"📌 Status da Garantia: {status_garantia}")

        if status_garantia == "LP":
            print("⚠️ Garantia LP detectada. Aplicando VOID3...")

            # Selecionar VOID3 na lista de exceções
            select_void = Select(driver.find_element(By.ID, "WTY_EXCEPTION"))
            select_void.select_by_value("VOID3")

            # Clicar no botão "Verificar garantia"
            driver.find_element(By.ID, "wtyCheckBtn").click()

            # 🟢 Fechar todos os popups que surgirem
            for _ in range(5):  # Tenta fechar popups até 5 vezes
                time.sleep(1)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    print("🔴 Fechando popup de verificação...")
                except:
                    break  # Se não houver popup, sai do loop

            print("✅ VOID aplicado com sucesso.")

    except NoSuchElementException:
        print("❌ Não foi possível verificar o status da garantia.")

    # 🟢 4. Verificar o "Status da OS no GSPN"
    try:
        select_status = Select(driver.find_element(By.ID, "STATUS"))
        status_atual = select_status.first_selected_option.text.strip()

        print(f"📌 Status da OS no GSPN: {status_atual}")

        if status_atual != "Pendente":
            print("⚠️ Status não está 'Pendente'. Alterando para 'Pendente'...")
            select_status.select_by_visible_text("Pendente")
            time.sleep(1)

    except NoSuchElementException:
        print("❌ Não foi possível verificar o status da OS.")

    # 🟢 5. Mudar o "Motivo da Pendência"
    try:
        select_motivo = Select(driver.find_element(By.ID, "REASON"))

        # Procurar a opção "Aguardando confirmação do consumidor"
        opcoes = [option.text.strip() for option in select_motivo.options]

        if "Aguardando confirmação do consumidor" in opcoes:
            select_motivo.select_by_visible_text("Aguardando confirmação do consumidor [HP030]")
            print("✅ Motivo da pendência alterado para 'Aguardando confirmação do consumidor'.")
        else:
            print("⚠️ Opção 'Aguardando confirmação do consumidor' não encontrada. Aplicando solução alternativa...")

            # Alterar Status para "Técnico designado" e depois voltar para "Pendente"
            select_status.select_by_visible_text("Técnico designado")
            time.sleep(1)
            select_status.select_by_visible_text("Pendente")
            time.sleep(1)

            # Tentar novamente selecionar o motivo da pendência
            select_motivo.select_by_visible_text("Aguardando confirmação do consumidor [HP030]")
            print("✅ Ajuste feito com sucesso.")

    except NoSuchElementException:
        print("❌ Não foi possível alterar o motivo da pendência.")

    # 🟢 6. Clicar no botão relógio
    try:
        botao_relogio = driver.find_element(By.XPATH, "//img[@src='/img/ico_time.gif']")
        botao_relogio.click()
        time.sleep(1)
        print("✅ Data e hora atualizadas usando o botão relógio.")
    except NoSuchElementException:
        print("⚠️ Botão relógio não encontrado.")

    # 🟢 7. Clicar no botão "Salvar"
    try:
        driver.find_element(By.ID, "btnSave").click()
        print("💾 Salvando alterações...")

        # 🟢 WebDriverWait para aguardar o popup "Confirm Notice"
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//td[@class='pop_title']/span[@id='divPop_title']"))
            )
            print("⚠️ Popup de confirmação detectado. Clicando em 'Salvar'...")
            
            # Clicar no botão "Salvar" dentro do popup
            driver.find_element(By.XPATH, "//a[@onclick=\"saveServiceOrder('WARNING_SKIP');return false;\"]").click()
            print("✅ Popup fechado e OS salva com sucesso.")

        except TimeoutException:
            print("✅ Nenhum popup de confirmação detectado. Salvamento concluído.")

        print("✅ OS atualizada com sucesso.")

    except NoSuchElementException:
        print("❌ Não foi possível salvar as alterações.")
        return

chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/Gestão MX/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("profile-directory=Default")
chrome_options.add_argument("--disable-sync")

# Inicializa o WebDriver
driver = webdriver.Chrome(options=chrome_options)


while True:
    os_input = input("Digite o número da OS do GSPN (10 dígitos): ").strip()
        
        # URL da OS no GSPN
    url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_input}#tabInfoHref"
    driver.get(url_gspn)
        
    time.sleep(5)  # Aguarda carregamento da página
    mudar_status_ag_custo_reparo(driver)