from bs4 import BeautifulSoup
import sys
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot\\')
from login_gspn.cookies_manager import obter_cookies_validos_recentes

import requests
import json
from automacoes.coletar_dados import fetch_os_data
from automacoes.montar_payloads import payload_dados_prod, obter_dados_saw
from automacoes.cos.coletar_dados_cos import obter_os_correspondentes, coletar_dados_os, coletar_usadas_cos
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

def converter_saws(lista_de_saws):
    status_map = {
        "SS005": "Solicitada",
        "SS010": "Aprovada",
        "SS015": "Rejeitada",
        "SS020": "Cancelada"
    }

    categoria_map = {
        "SRC09": "AEG 1x",
        "SRC11": "Troca do produto",
        "SRC29": "Uso Excessivo",
        "SRC73": "[VOID] Exceção de garantia",
        "SRC75": "OS Mista",
        "SRC84": "Verificação de data de compra",
        "SRC86": "SKIP de Fenrir",
        "SRC91": "Troca CARE+",
        "SRZ12": "QR Code",
        "SRZ15": "Peças cosméticas"
    }

    resultado = {}

    for i, saw in enumerate(lista_de_saws, start=1):
        saw_dict = {}
        for chave, valor in saw:
            if chave == "SAW_STATUS":
                saw_dict["status"] = status_map.get(valor, f"Status desconhecido ({valor})")
            elif chave == "SAW_CATEGORY":
                saw_dict["categoria"] = categoria_map.get(valor, f"Categoria desconhecida ({valor})")

        resultado[f"SAW {i}"] = saw_dict

    return resultado

def coletar_informacoes_os(numero_os, cookies=obter_cookies_validos_recentes()):
    """
    Extrai informações da OS no GSPN e COS.
    Retorna um dicionário com as informações coletadas.
    """
    target_url = "https://biz6.samsungcsportal.com/gspn/operate.do"

    headers = {
    "Host": "biz6.samsungcsportal.com",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": '"Windows"',
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "text/html, */*; q=0.01",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "Content-Type": "application/x-www-form-urlencoded",
    "sec-ch-ua-mobile": "?0",
    "Origin": "https://biz6.samsungcsportal.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": f"https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID={numero_os}",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    
}

    html_os = fetch_os_data(numero_os, cookies)
    dados_full = html_os

    payload_prod = payload_dados_prod(dados_full)
    if not payload_prod:
        print("Erro ao montar o payload de dados do produto.")
        return None
    dados_full.update(payload_prod)
    soup = BeautifulSoup(dados_full['html_os'], 'html.parser')
    cookies = dados_full['cookies']
    try:
        os_cos = obter_os_correspondentes(numero_os)
    except Exception as e:
        print(f"Erro ao obter OS correspondentes: {e}")
        return None
    dados_os_cos = coletar_dados_os(os_cos)
    try:
        response = requests.post(target_url, headers=headers, cookies=cookies, data=dados_full['payload_prod'], verify=False)
        response.raise_for_status()  # Verifica erro HTTP
        #print(f"Status Code: {response.status_code}")
        html_prod = response.text
    except Exception as e:
        print(f"Erro ao enviar requisição: {e}")
        return None
    soup_prod = BeautifulSoup(html_prod, 'html.parser')

    os_gspn = numero_os
    dados_saw = obter_dados_saw(numero_os, cookies)
    if dados_saw:
        dados_saw = converter_saws(dados_saw)
        print(f"dados saw: {dados_saw}")
    if not dados_saw:
        dados_saw = "Não possui SAW"
    status_garantia_gspn = soup_prod.find("input", {"id": "IN_OUT_WTY"}).get("value")
    status_garantia_cos = dados_os_cos['tipo_atendimento']
    status_os_cos = dados_os_cos['status_os']
    descricao_status = dados_os_cos['descricao_status']
    void = soup_prod.find('select', {'id': 'WTY_EXCEPTION'}).find('option', selected=True)['value'] if soup_prod.find('select', {'id': 'WTY_EXCEPTION'}).find('option', selected=True) else ""
    tecnico = dados_os_cos['tecnico']
    data_abertura_cos = dados_os_cos['data_entrada']
    data_abertura_gspn = soup.find("input", {"id": "CREATE_DATE"}).get("value")
    numero_sinistro =soup.find("input", {"id": "DEALER_JOB_NO"}).get("value", False)
    data_producao = soup_prod.find("input", {"id": "PRODUCT_DATE"}).get("value")
    data = datetime.strptime(data_producao, "%d/%m/%Y")
    suposta_data_de_compra = data + relativedelta(months=2)
    data_da_compra = soup_prod.find("input", {"id": "PURCHASE_DATE"}).get("value", suposta_data_de_compra)
    fim_garantia = soup_prod.find("input", {"id": "NEW_LABOR_WT_D"}).get("value")
    """try:
        pecas_cos = coletar_usadas_cos(os_cos)
        pecas_cos = pecas_cos.get('used_parts_cos', [])
        
    except Exception as e: 
        print(f"Erro ao coletar peças usadas: {e}")
        pecas_cos = None
    pecas_requisitadas = dados_os_cos['pecas_requisitadas']"""

    dados_completos = {
        'os_gspn': os_gspn,
        'status_garantia_gspn': status_garantia_gspn,
        'status_garantia_cos': status_garantia_cos,
        'status_os_cos': status_os_cos,
        'descricao_status': descricao_status,
        'void': void,
        'tecnico': tecnico,
        'data_abertura_cos': data_abertura_cos,
        'data_abertura_gspn': data_abertura_gspn,
        #'numero_sinistro': numero_sinistro,
        'data_producao': data_producao,
        'data_da_compra': data_da_compra,
        'fim_garantia': fim_garantia,
        'dados_saw': dados_saw
        #'pecas_cos': pecas_cos,
        #'pecas_requisitadas': pecas_requisitadas
    }

    return dados_completos

if __name__ == "__main__":
    # Exemplo de uso
    numero_os = "4174350555"  # Substitua pelo número da OS desejada
    dados_os = coletar_informacoes_os(numero_os)
    if dados_os:
        print(f"Dados coletados para a OS {numero_os}:")
        for chave, valor in dados_os.items():
            print(f"{chave}: {valor}")
    else:
        print("Falha ao coletar dados da OS.")


