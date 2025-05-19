from selenium.webdriver.common.by import By
import time

def verificar_aba_correta(driver, os_numero):
    """Garante que o Selenium está na aba correta, baseada no número da OS."""
    for aba in driver.window_handles:
        driver.switch_to.window(aba)
        if os_numero in driver.current_url:
            print(f"✅ Aba correta encontrada para a OS {os_numero}.")
            return True

    print(f"⚠️ Nenhuma aba correta encontrada para a OS {os_numero}.")
    return False

def obter_os_correspondentes(driver, os_input):
    driver.switch_to.window(driver.window_handles[-1])
    """Obtém as OS do COS e do GSPN a partir de uma única entrada."""
    os_cos = None
    os_gspn = None

    if len(os_input) == 6:  # Se for OS do COS
        print(f"🔍 Buscando OS do GSPN para a OS do COS {os_input}...")
        
        url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_input}"
        driver.execute_script(f"window.open('{url_cos}', '_blank');")
        time.sleep(3)

        if verificar_aba_correta(driver, os_input):
            try:
                elemento_os = driver.find_element(By.ID, "OrdemServico").text
                partes = elemento_os.split(" / ")
                os_cos = os_input
                os_gspn = partes[1]
                print(f"✅ OS do GSPN encontrada: {os_gspn}")
            except:
                print("❌ Não foi possível encontrar a OS do GSPN no COS.")

    elif len(os_input) == 10:  # Se for OS do GSPN
        print(f"🔍 Buscando OS do COS para a OS do GSPN {os_input}...")
        
        url_busca_cos = "http://192.168.25.131:8080/COS_CSO/BuscarOrdemServico.jsp"
        driver.execute_script(f"window.open('{url_busca_cos}', '_blank');")
        time.sleep(3)

        if verificar_aba_correta(driver, os_input):
            try:
                driver.find_element(By.ID, "OSFabricante").send_keys(os_input)
                driver.find_element(By.ID, "BtnEditar").click()
                time.sleep(3)

                elemento_os = driver.find_element(By.ID, "OrdemServico").text
                partes = elemento_os.split(" / ")
                os_cos = partes[0]
                os_gspn = os_input
                print(f"✅ OS do COS encontrada: {os_cos}")
            except:
                print("❌ Não foi possível encontrar a OS do COS no resultado da busca.")
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    return os_cos, os_gspn
