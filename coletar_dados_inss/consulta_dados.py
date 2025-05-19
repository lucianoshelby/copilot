import requests
import json
import sqlite3
import sys
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot\\')
from login_gspn.cookies_manager import obter_cookies_validos_recentes
def consulta_dez_dias(data_inicio, data_fim, codigo_asc, cookies):
    """
    Realiza uma consulta à base de dados para um intervalo de 10 dias.

    Args:
        data_inicio (str): Data inicial da busca no formato 'DD/MM/AAAA'.
        data_fim (str): Data final da busca no formato 'DD/MM/AAAA'.
        codigo_asc (str): Código da ASC.
        cookies (dict): Dicionário contendo os cookies para a requisição.

    Returns:
        dict: Dicionário contendo a resposta da requisição (ou None em caso de erro).
    """

    url = "https://biz6.samsungcsportal.com/gspn/operate.do"
    headers = {
        "Host": "biz6.samsungcsportal.com",
        "Connection": "keep-alive",
        "Content-Length": "770",  # Este valor pode precisar ser ajustado
        "X-Prototype-Version": "1.7.2",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://biz6.samsungcsportal.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://biz6.samsungcsportal.com/svctracking/lite/ServiceOrderListLite.jsp?search_status=&searchContent=&menuBlock=&menuUrl=&naviDirValue=",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }
    payload = {
        "cmd": "SvcOrderArkListCmd",
        "objectID": "",
        "ascJobNo": "",
        "tokenNo": "",
        "ascCode": "",
        "jspName": "/svctracking/svcorder/ServiceOrderList.jsp",
        "popup": "Y",
        "soDetailType": "",
        "MOBILE_FLAG": "",
        "asc_acctno": codigo_asc,
        "asc_code": codigo_asc,
        "cc_code": "",
        "service_order_no": "",
        "asc_job_no": "",
        "token_no": "",
        "status": "",
        "reason": "",
        "status1": "ST030",
        "reason1": "",
        "req_date_from1": data_inicio,
        "req_date_to1": data_fim,
        "req_date_from": data_inicio,
        "req_date_to": data_fim,
        "status2": "",
        "reason2": "",
        "DEALER_JOB_NO": "",
        "service_type": "",
        "model": "",
        "SUB_SVC_TYPE3": "",
        "SUB_SVC_TYPE": "",
        "serial_no": "",
        "imei": "",
        "CONSUMER": "",
        "appt_date_from": "",
        "appt_date_to": "",
        "dateType_from": data_inicio,
        "dateType_to": data_fim,
        "engineer": "",
        "voc_flag": "",
        "b2b_flag": "",
        "ZSVC_LEVEL": "",
        "product": "",
        "LOCAL_PRODUCT": "",
        "wty_flag": "",
        "wty_type": "",
        "OBJECT_ID_FROM": "",
        "OBJECT_ID_TO": "",
        "redo_flag": "",
        "VANID": "",
        "PV_RESULT": "",
        "FEEDBACK_STATUS": "",
        "high_risk_flag": ""
    }

    try:
        response = requests.post(url, headers=headers, data=payload, cookies=cookies, verify=False)
        response.raise_for_status()
        return response.json()  # Use response.json() directly
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

import json

def filtrar_ordens_servico(resposta_api):
    """
    Filtra os números das ordens de serviço da resposta da API.

    Args:
        resposta_api (dict): Dicionário contendo a resposta da API.

    Returns:
        list: Lista de strings, onde cada string é um número de ordem de serviço.
    """

    ordens_servico = []
    if resposta_api and 'etSvcInfo' in resposta_api:
        for ordem in resposta_api['etSvcInfo']:
            ordens_servico.append(ordem.get("service_order_no"))
    return ordens_servico


import requests
from bs4 import BeautifulSoup

def consultar_codigos_clientes(lista_os, codigo_asc, cookies):
    """
    Consulta os códigos dos clientes para uma lista de ordens de serviço.

    Args:
        lista_os (list): Lista de números de ordens de serviço (strings).
        codigo_asc (str): Código da ASC.
        cookies (dict): Dicionário contendo os cookies para a requisição.

    Returns:
        list: Lista de strings, onde cada string é o código do cliente.
    """

    url = "https://biz6.samsungcsportal.com/gspn/operate.do"
    headers = {
        "Host": "biz6.samsungcsportal.com",
        "Connection": "keep-alive",
        "Content-Length": "253",  # Este valor pode precisar ser ajustado
        "sec-ch-ua-platform": "\"Windows\"",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/html, */*; q=0.01",
        "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "Content-Type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://biz6.samsungcsportal.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID=4172916970",  # A URL de Referer pode variar
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    codigos_clientes = []
    for os_numero in lista_os:
        payload = {
            "ui": "",
            "isFieldUser": "false",
            "useEngineer": "true",
            "isBillingSaved": "false",
            "cmd": "ZifGspnSvcCustomerLDCmd",
            "objectId": os_numero,  # Usar o número da OS atual
            "ascCode": codigo_asc,
            "isMedisonUser": "false",
            "serviceType": "CI",
            "tab": "/svctracking/lite/ServiceOrderUpdateCustInfo.jsp",  # A URL da tab pode variar
            "sawExistReverseVoidApproved": "true"
        }

        try:
            response = requests.post(url, headers=headers, data=payload, cookies=cookies, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            consumer_element = soup.find(id="CONSUMER")
            if consumer_element:
                codigos_clientes.append(consumer_element.get("value"))
            else:
                print(f"Código do consumidor não encontrado para OS: {os_numero}")
                codigos_clientes.append(None)  # Ou outra forma de indicar que não foi encontrado
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar código do consumidor para OS {os_numero}: {e}")
            codigos_clientes.append(None)

    return codigos_clientes

import requests
import json

def consultar_dados_clientes(lista_codigos_cliente, codigo_asc, cookies):
    """
    Consulta os dados dos clientes para uma lista de códigos de cliente.

    Args:
        lista_codigos_cliente (list): Lista de códigos de cliente (strings).
        codigo_asc (str): Código da ASC.
        cookies (dict): Dicionário contendo os cookies para a requisição.

    Returns:
        list: Lista de dicionários, onde cada dicionário representa um cliente
              com os dados formatados para o banco de dados.
    """

    url = "https://biz6.samsungcsportal.com/gspn/operate.do"
    headers = {
        "Host": "biz6.samsungcsportal.com",
        "Connection": "keep-alive",
        "Content-Length": "574",  # Este valor pode precisar ser ajustado
        "X-Prototype-Version": "1.7.2",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://biz6.samsungcsportal.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://biz6.samsungcsportal.com/svctracking/common/SVCPopCustomerSearch.jsp",  # A URL de Referer pode variar
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        #"Cookie": cookies  # Usar os cookies fornecidos
    }

    dados_clientes = []
    for codigo_cliente in lista_codigos_cliente:
        payload = {
            "cmd": "SVCPopCustomerDetailCmd",
            "numPerPage": "100",
            "currPage": "0",
            "SVCRequestNo": "false",
            "BP_NO": codigo_cliente,
            "MODEL": "",
            "SERIAL_NO": "",
            "IMEI": "",
            "bpKind": "",
            "IV_C_CHANNEL": "",
            "IV_DIVISION": "X",
            "country": "BR",
            "IV_ASC_CODE": codigo_asc,
            "Sequence": "",
            "firstName": "",
            "lastName": "",
            "phone": "",
            "uniqueID": "",
            "bpno": codigo_cliente,
            "IV_EMAIL": "",
            "D_BP_TYPE": "",
            "D_TITLE": "",
            "D_NAME_FIRST": "",
            "D_NAME_LAST": "",
            "D_CONSUMER": "",
            "D_GENDER": "",
            "D_UNIQUE_ID": "",
            "D_PREFERENCE_CHANNEL": "",
            "D_HOME_PHONE": "",
            "D_OFFICE_PHONE": "",
            "D_OFFICE_PHONE_EXT": "",
            "D_MOBILE_PHONE": "",
            "D_FAX": "",
            "D_EMAIL": "",
            "D_CONTACT_FLAG": "",
            "D_STREET1": "",
            "D_STREET2": "",
            "D_STREET3": "",
            "D_DISTRICT": "",
            "D_CITY": "",
            "D_CITY_CODE": "",
            "D_REGION_CODE": "",
            "D_REGION": "",
            "D_COUNTRY": "",
            "D_POST_CODE": ""
        }

        try:
            response = requests.post(url, headers=headers, data=payload, cookies=cookies, verify=False)
            response.raise_for_status()
            dados = response.json()
            if dados and 'dataLists' in dados and dados['dataLists']:
                cliente_data = dados['dataLists'][0]  # Assuming the first element is the relevant one
                nome = f"{cliente_data.get('NAME_FIRST', '')} {cliente_data.get('NAME_LAST', '')}".strip()
                email = cliente_data.get('EMAIL', '').lower()
                telefones = [
                    cliente_data.get('MOBILE_PHONE'),
                    cliente_data.get('HOME_PHONE'),
                    cliente_data.get('OFFICE_PHONE')
                ]
                telefones = [tel for tel in telefones if tel]  # Filtra telefones vazios
                cidade = cliente_data.get('CITY')
                estado = cliente_data.get('REGION')
                
                # Extrair modelos de produtos (exemplo básico)
                produtos = []
                if 'productlists' in dados and dados['productlists']:
                    for produto in dados['productlists']:
                        if produto.get('MODEL'):
                            produtos.append(produto.get('MODEL'))
                produtos = list(set(produtos))  # Remove duplicatas

                dados_clientes.append({
                    "codigo_cliente": codigo_cliente,
                    "nome": nome,
                    "telefone1": telefones[0] if telefones else None,
                    "telefone2": telefones[1] if len(telefones) > 1 else None,
                    "telefone3": telefones[2] if len(telefones) > 2 else None,
                    "email": email,
                    "cidade": cidade,
                    "estado": estado,
                    "produtos": json.dumps(produtos)
                })
            else:
                print(f"Dados do cliente não encontrados para código: {codigo_cliente}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar dados do cliente {codigo_cliente}: {e}")
    return dados_clientes

if __name__ == "__main__":
    # Exemplo de uso

    cookies_exemplo = obter_cookies_validos_recentes()
    data_inicio = "12/05/2025"
    data_fim = "15/05/2025"
    codigo_asc = "0002446971"
    #resposta_api = consulta_dez_dias(data_inicio, data_fim, codigo_asc, cookies_exemplo)
    #ordens_servico = filtrar_ordens_servico(resposta_api)
    #codigos_cliente_exemplo = consultar_codigos_clientes(ordens_servico, codigo_asc, cookies_exemplo)
    codigos_cliente_exemplo = ["6022147136"]  # Exemplo de códigos de cliente
   
    codigo_asc_teste = "0002446971"

    dados_clientes = consultar_dados_clientes(codigos_cliente_exemplo, codigo_asc_teste, cookies_exemplo)
    print(json.dumps(dados_clientes, indent=4, ensure_ascii=False))