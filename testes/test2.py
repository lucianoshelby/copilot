from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configuração do Chrome com perfil do usuário
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/Gestão MX/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("profile-directory=Default")
chrome_options.add_argument("--disable-sync")  # Evita erros de sincronização do Chrome

# Inicializa o WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Dicionário para mapear OS às abas abertas
tarefas_ativas = {}

try:
    def abrir_nova_aba(os_numero, url):
        """Abre uma nova aba no navegador e vincula ao número da OS."""
        driver.execute_script(f"window.open('{url}', '_blank');")  # Abre a aba com a URL
        time.sleep(2)  # Aguarda um tempo para garantir que a aba seja criada

        # Percorre todas as abas para encontrar a correta
        for aba in driver.window_handles:
            driver.switch_to.window(aba)
            if os_numero in driver.current_url:  # Verifica se a URL contém o número da OS
                tarefas_ativas[os_numero].append(aba)  # Associa a aba à OS
                return
        
        print(f"⚠️ Nenhuma aba encontrada para OS {os_numero}.")

    def fechar_abas_da_os(os_numero):
        """Fecha todas as abas associadas a uma OS específica e remove do controle."""
        if os_numero in tarefas_ativas:
            for aba in tarefas_ativas[os_numero]:
                driver.switch_to.window(aba)
                driver.close()  # Fecha a aba
            del tarefas_ativas[os_numero]  # Remove a OS do controle
            print(f"✅ Todas as abas da OS {os_numero} foram fechadas.")
        else:
            print(f"⚠️ Nenhuma aba registrada para a OS {os_numero}.")

    # Solicita a OS no console
    os_input = input("Digite o número da OS (6 dígitos para COS ou 10 dígitos para GSPN): ").strip()

    # Verifica se a OS já está em andamento
    if os_input in tarefas_ativas:
        print(f"❌ A OS {os_input} já está em andamento. Aguarde a finalização antes de tentar novamente.")
    else:
        tarefas_ativas[os_input] = []  # Inicializa a entrada no dicionário

        if len(os_input) == 6:
            # Se for OS do COS, abrir diretamente a página da OS no COS
            url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_input}"
            abrir_nova_aba(os_input, url_cos)

            time.sleep(3)

            try:
                elemento_os = driver.find_element(By.ID, "OrdemServico").text
                partes = elemento_os.split(" / ")
                os_gspn = partes[1]  # Pegamos a OS do GSPN

                url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_gspn}#tabInfoHref"
                abrir_nova_aba(os_input, url_gspn)

                print(f"OS do COS {os_input} aberta! OS do GSPN correspondente {os_gspn} aberta em outra aba!")

            except Exception as e:
                print("❌ Não foi possível encontrar a OS do GSPN no COS.")
                print("Erro:", e)

        elif len(os_input) == 10:
            # Se for OS do GSPN, buscar a OS correspondente no COS
            url_busca_cos = "http://192.168.25.131:8080/COS_CSO/BuscarOrdemServico.jsp"
            abrir_nova_aba(os_input, url_busca_cos)

            time.sleep(3)

            driver.find_element(By.ID, "OSFabricante").send_keys(os_input)
            driver.find_element(By.ID, "BtnEditar").click()

            time.sleep(3)

            try:
                elemento_os = driver.find_element(By.ID, "OrdemServico").text
                partes = elemento_os.split(" / ")
                os_cos = partes[0]

                url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_cos}"
                abrir_nova_aba(os_input, url_cos)

                url_gspn = f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={os_input}#tabInfoHref"
                abrir_nova_aba(os_input, url_gspn)

                print(f"OS do GSPN {os_input} encontrada! OS do COS correspondente {os_cos} aberta em outra aba!")

            except Exception as e:
                print("❌ Não foi possível encontrar a OS do COS no resultado da busca.")
                print("Erro:", e)

        else:
            print("❌ Número de OS inválido. Digite 6 ou 10 dígitos.")

finally:
    input("Pressione ENTER para fechar as abas da tarefa...")

    # Fecha as abas da OS ao final da execução
    if os_input in tarefas_ativas:
        fechar_abas_da_os(os_input)

    driver.quit()
