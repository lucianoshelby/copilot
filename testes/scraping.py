from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configuração do Chrome com perfil do usuário
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/Gestão MX/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("profile-directory=Default")

# Inicializa o WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Dicionário para mapear tarefas às abas abertas
task_tabs = {}

try:
    # Criar um identificador único para a tarefa
    task_id = f"TASK_{int(time.time() * 1000)}"
    task_tabs[task_id] = []  # Inicializa o ID no dicionário

    os_input = input("Digite o número da OS (6 dígitos para COS ou 10 dígitos para GSPN): ").strip()

    def abrir_nova_aba(task_id, url):
        """Abre uma nova aba no navegador, adiciona um identificador na URL e vincula ao task_id."""
        url_com_id = f"{url}&TASK={task_id}" if "?" in url else f"{url}?TASK={task_id}"
        driver.execute_script(f"window.open('{url_com_id}', '_blank');")  # Abre nova aba diretamente com o URL modificado
        time.sleep(2)  # Aguarda um tempo para garantir que a aba seja criada
        encontrar_aba_por_url(task_id, url_com_id)  # Alterna para a aba correta

    def encontrar_aba_por_url(task_id, url_parcial):
        """Percorre todas as abas e encontra aquela que contém a URL com o task_id."""
        for aba in driver.window_handles:
            driver.switch_to.window(aba)
            if url_parcial in driver.current_url:  # Verifica se a URL contém o task_id
                task_tabs[task_id].append(aba)  # Associa a aba ao task_id
                return
        print(f"⚠️ Nenhuma aba encontrada para {task_id}")

    if len(os_input) == 6:
        url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_input}"
        abrir_nova_aba(task_id, url_cos)

        time.sleep(3)

        try:
            elemento_os = driver.find_element(By.ID, "OrdemServico").text
            partes = elemento_os.split(" / ")
            os_gspn = partes[1]  # Pegamos a OS do GSPN

            url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_gspn}#tabInfoHref"
            abrir_nova_aba(task_id, url_gspn)

            print(f"OS do COS {os_input} aberta! OS do GSPN correspondente {os_gspn} aberta em outra aba!")

        except Exception as e:
            print("Não foi possível encontrar a OS do GSPN no COS.")
            print("Erro:", e)

    elif len(os_input) == 10:
        url_busca_cos = "http://192.168.25.131:8080/COS_CSO/BuscarOrdemServico.jsp"
        abrir_nova_aba(task_id, url_busca_cos)

        time.sleep(3)

        driver.find_element(By.ID, "OSFabricante").send_keys(os_input)
        driver.find_element(By.ID, "BtnEditar").click()

        time.sleep(3)

        try:
            elemento_os = driver.find_element(By.ID, "OrdemServico").text
            partes = elemento_os.split(" / ")
            os_cos = partes[0]

            url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_cos}"
            abrir_nova_aba(task_id, url_cos)

            url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_input}#tabInfoHref"
            abrir_nova_aba(task_id, url_gspn)

            print(f"OS do GSPN {os_input} encontrada! OS do COS correspondente {os_cos} aberta em outra aba!")

        except Exception as e:
            print("Não foi possível encontrar a OS do COS no resultado da busca.")
            print("Erro:", e)

    else:
        print("Número de OS inválido. Digite 6 ou 10 dígitos.")

finally:
    input("Pressione ENTER para fechar as abas da tarefa...")

    # Fecha apenas as abas associadas a essa tarefa
    for aba in task_tabs.get(task_id, []):
        driver.switch_to.window(aba)
        driver.close()

    driver.quit()
