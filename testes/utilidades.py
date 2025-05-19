from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
def fechar_popups(driver, timeout=120):
    """
    Aguarda até 2 minutos para que um popup (interno ou do navegador) apareça e o fecha.
    Retorna True se um popup foi fechado, False se nenhum popup apareceu.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: EC.alert_is_present()(d) or 
                      d.find_elements(By.XPATH, "//td[@class='pop_title']/span[@id='divPop_title']")

        )
        time.sleep(3)

        # Verificar se o popup do navegador apareceu primeiro
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())  # Confirma que há um alert antes de manipular
            alert = driver.switch_to.alert
            print("⚠️ Popup do navegador detectado. Fechando...")
            alert.accept()
            print("✅ Popup do navegador fechado com sucesso.")
            return True

        except TimeoutException:
            # Caso contrário, verificar o popup interno
            print("⚠️ Popup interno detectado. Clicando em 'Salvar'...")
            botao_salvar = driver.find_element(By.XPATH, "//div[@id='divConfirmNotice']//a[@onclick=\"saveServiceOrder('WARNING_SKIP');return false;\"]")
            botao_salvar.click()
            return True

    except TimeoutException:
        print("❌ Nenhum popup detectado após 2 minutos. O salvamento pode não ter sido concluído!")
        return False
def esperar_elemento_visivel(driver, xpath, timeout=10):
    """Aguarda até que um elemento esteja visível na página."""
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        return False

def esperar_elemento_clicavel(driver, xpath, timeout=10):
    """Aguarda até que um elemento esteja visível e clicável na página."""
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        return True
    except TimeoutException:
        return False

def esperar_popup(driver, timeout=5):
    """Aguarda e fecha todos os popups que aparecerem."""
    try:
        while True:
            WebDriverWait(driver, timeout).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print("🔴 Fechando popup do navegador...")
            alert.accept()
            time.sleep(1)  # Pequena pausa para verificar se há mais popups
    except TimeoutException:
        print("✅ Nenhum novo popup detectado. Continuando...")
