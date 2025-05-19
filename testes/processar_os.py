import os
import time
from config import configurar_driver
from automacoes.abrir_os import abrir_os_cos
from automacoes.coletar_dados import coletar_dados_cos
from automacoes.manipular_os import mudar_status_ag_custo_reparo
from automacoes.obter_os import obter_os_correspondentes

# Caminho do arquivo com a lista de OS
CAMINHO_ARQUIVO = r"C:\Users\Gestão MX\Documents\AutoMX\OS.txt"

# Caminho para salvar os logs
CAMINHO_LOG = r"C:\Users\Gestão MX\Documents\AutoMX\log_processamento.txt"

def registrar_log(mensagem):
    """Escreve uma mensagem no arquivo de log."""
    with open(CAMINHO_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")

def processar_os():
    """Processa a lista de OS conforme as regras especificadas."""
    if not os.path.exists(CAMINHO_ARQUIVO):
        print(f"❌ Arquivo '{CAMINHO_ARQUIVO}' não encontrado!")
        return

    # Iniciar WebDriver
    driver = configurar_driver()
    input('pressione enter para iniciar')

    # Ler lista de OS do arquivo
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as file:
        os_list = [line.strip() for line in file.readlines() if line.strip()]

    registrar_log("🔄 Iniciando processamento das OS...")

    for os_gspn in os_list:
        try:
            print(f"🔍 Processando OS GSPN: {os_gspn}")
            registrar_log(f"🔍 Processando OS GSPN: {os_gspn}")

            # Obter OS do COS correspondente
            os_cos, _ = obter_os_correspondentes(driver, os_gspn)
            if not os_cos:
                registrar_log(f"⚠️ OS {os_gspn} - Não foi possível obter OS do COS.")
                continue

            # Abrir OS no COS e coletar dados
            abrir_os_cos(driver, os_cos)
            time.sleep(3)
            dados_os = coletar_dados_cos(driver)

            status_os = dados_os.get("status_os", "Não encontrado")
            tipo_atendimento = dados_os.get("tipo_atendimento", "Não encontrado")

            print(f"📌 Status: {status_os} | Tipo Atendimento: {tipo_atendimento}")
            registrar_log(f"📌 OS {os_gspn} - Status: {status_os} | Tipo Atendimento: {tipo_atendimento}")

            # 🟢 Aplicar regras para chamar "AG CUSTO DE REPARO"
            if status_os.startswith("Pendente"):
                registrar_log(f"✅ OS {os_gspn} - Chamando AG CUSTO DE REPARO (Status: {status_os})")
                mudar_status_ag_custo_reparo(driver, os_gspn)

            elif status_os == "Técnico Designado / Reparo em Andamento" and (
                tipo_atendimento.startswith("Aprovado Balcão") or tipo_atendimento.startswith("Fora de Garantia")
            ):
                registrar_log(f"✅ OS {os_gspn} - Chamando AG CUSTO DE REPARO (Status: {status_os}, Atendimento: {tipo_atendimento})")
                mudar_status_ag_custo_reparo(driver, os_gspn)

            else:
                registrar_log(f"⚠️ OS {os_gspn} - Não atende aos critérios para mudança de status.")

        except Exception as e:
            print(f"❌ Erro ao processar OS {os_gspn}: {e}")
            registrar_log(f"❌ OS {os_gspn} - Erro: {e}")

    driver.quit()
    registrar_log("✅ Processamento concluído.")

# Executar o script
if __name__ == "__main__":
    processar_os()
