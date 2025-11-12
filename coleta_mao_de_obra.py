from finalizar_sem_reparo import aplicar_produto_entregue, aplicar_reparo_completo_remontagem, mudar_pra_ow, muda_tecnico_gspn, aplica_ag_custo_gspn
from automacoes.cos.auto_cos import deletar_cos
from automacoes.cos.coletar_dados_cos import obter_os_correspondentes
from automacoes.coletar_dados import fetch_os_data
from coletar_os_da_base.coletar_informações_os import coletar_informacoes_os
from automacoes.montar_payloads import extract_js_variable
import time
from login_gspn.cookies_manager import obter_cookies_validos_recentes
import requests
CAMINHO_ARQUIVO = r"C:\\Users\\Gestão MX\\Documents\\Copilot\\OS.txt"

from bs4 import BeautifulSoup

def extrair_numero_garantia(html):
    """
    Extrai o valor do input com id 'claimno' apenas se o campo <select id="STATUS">
    estiver com a opção 'ST040' (Produto Entregue) selecionada.

    Parâmetros:
        html (str): conteúdo HTML como string.

    Retorna:
        str ou None: o valor de 'claimno', ou None se o status não for ST040 ou o campo não existir.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Verifica o select com id STATUS
    select_status = soup.find('select', id='STATUS')
    if not select_status:
        return None

    selected_option = select_status.find('option', selected=True)
    if not selected_option or selected_option.get('value') != 'ST040':
        return None

    # Se status for ST040, continua procurando o claimno
    input_claimno = soup.find('input', id='claimno')
    if input_claimno and input_claimno.has_attr('value'):
        return input_claimno['value']

    return None


def coleta_mao_de_obra(objectid, cookies):
    url = "https://biz6.samsungcsportal.com/gspn/operate.do?popupReason=viewClaim"

    headers = {
        "Host": "biz6.samsungcsportal.com",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Origin": "https://biz6.samsungcsportal.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://biz6.samsungcsportal.com/gspn/operate.do?cmd=ZifGspnSvcMainLDCmd&objectID=4171139579",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }

    dados_os = fetch_os_data(objectid)
    html = dados_os['html_os']
    garantia = extrair_numero_garantia(html)
    if not garantia:
        return 00.00
    data = {
        "openTabID": "",
        "jobServiceType": "CI",
        "cmd": "WtyClaimDetailCmd",
        "objectID": objectid,
        "ascCode": "0002446971",
        "claimno": garantia,
        "IV_OBJECT_ID": objectid
    }

    response = requests.post(url, headers=headers, data=data, cookies=cookies, verify=False)

    html_garantia = response.text
    soup = BeautifulSoup(html_garantia, 'html.parser')

    
    campo = soup.find('input', {'name': 'i_labor_amt'})
    
    if campo and campo.has_attr('value'):
        valor = campo['value'].strip()
        if valor:
            return valor.replace('.', ',')

    return None

def fechar_lista_de_os(cookies=None):

    print("Iniciando consulta de lista de OS...")
    fallhas = []
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as file:
        os_list = [line.strip() for line in file.readlines() if line.strip()]
    total=[]
    for os in os_list:
        #deletar = deletar_cos(os)
        #os = obter_os_correspondentes(os)
        #dados= fetch_os_data(os)
        #fechamento = mudar_pra_ow(dados)
        #fechamento = aplica_ag_custo_gspn(os)
        #fechamento = muda_tecnico_gspn(os)
        #fechamento = coletar_informacoes_os(os, cookies)
        fechamento = coleta_mao_de_obra(os, cookies)
        
        #fechamento = aplicar_reparo_completo_remontagem(os)
        if fechamento:
            fechamento = {os: fechamento}
            print(f"Consulta da OS {os} realizado com sucesso.")
            total.append(fechamento)
            #time.sleep(2)
        else:
            print(f"Erro ao consultar a OS {os}.")
            fallhas.append(os)
            continue
        """print('Aplicando o produto entregue...')
        produto_entregue = aplicar_produto_entregue(os)
        if produto_entregue:
            print(f"Produto entregue aplicado na OS {os} com sucesso.")
            print("Deletando OS COS...")
            deletar = deletar_cos(os)
            if deletar:
                print(f"OS COS {os} deletada com sucesso.")
            else:
                print(f"Erro ao deletar a OS COS {os}.")
        else:
            print(f"Erro ao aplicar o produto entregue na OS {os}.")
            fallhas.append(os)"""
    if fallhas:
        print("As seguintes OSs falharam na consulta:")
        for os in fallhas:
            print(os)
    for fechamento in total:
        #print('------Dados da OS-------')
        for chave, valor in fechamento.items():
            print(f'{chave}: {valor}')






if __name__ == "__main__":
    cookies = obter_cookies_validos_recentes()
    fechar_lista_de_os(cookies)
    #aplicar_reparo_completo_remontagem("4172771585")
    #resposta = coleta_mao_de_obra("4171139579", cookies)
    print("Consulta de mão de obra concluida.")
