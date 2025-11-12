from coletar_dados import fetch_os_data
from montar_payloads import extract_js_variable
from cos.coletar_dados_cos import obter_os_correspondentes, coletar_dados_os
from bs4 import BeautifulSoup
import re

def extrair_os_relacionada(html: str) -> str | None:
    """
    Analisa um conteúdo HTML para extrair o número da OS (Ordem de Serviço) relacionada,
    realizando a busca dentro do formulário com id='detailForm'.

    Args:
        html_content: Uma string contendo o HTML completo.

    Returns:
        Uma string com o número da OS relacionada (ex: '4173178000') ou None
        se não for encontrado."""

    padrao = r"Related Ticket\s*:\s*<a [^>]*svcOrderLink\('(\d+)'"
    match = re.search(padrao, html)
    if match:
        return match.group(1)
    return None


def extrair_codigo_asc(html_content: str) -> str | None:
    """
    Analisa um conteúdo HTML para extrair um código de referência específico.

    A função procura pela célula de tabela (<td>) com o texto 'Criado por'
    e extrai o código da célula imediatamente seguinte.

    Args:
        html_content: Uma string contendo o HTML completo da página.

    Returns:
        Uma string com o código encontrado (ex: '0003178766') ou None se
        o código não puder ser encontrado na estrutura esperada.
    """
    try:
        # 1. Cria o objeto BeautifulSoup para parsear o HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 2. Encontra a célula âncora que contém o texto "Criado por "
        #    O espaço no final é importante para corresponder exatamente ao HTML.
        celula_ancora = soup.find('td', class_='ser_ti', string='Criado por ')

        if not celula_ancora:
            # Fallback para caso o texto não tenha o espaço no final
            celula_ancora = soup.find('td', class_='ser_ti', string=lambda text: 'Criado por' in text)

        # 3. Encontra a célula seguinte (a que contém o código)
        #    O método find_next_sibling é perfeito para isso.
        celula_alvo = celula_ancora.find_next_sibling('td', class_='ser_td')

        # 4. Extrai o texto da célula, limpa os espaços e pega o código
        texto_completo = celula_alvo.get_text()
        
        # .strip() remove espaços em branco e caracteres especiais (como &nbsp;) do início e fim
        # .split()[0] divide a string por espaços e pega o primeiro item (o código)
        codigo = texto_completo.strip().split()[0]
        
        return codigo

    except (AttributeError, IndexError) as e:
        # AttributeError ocorre se 'celula_ancora' ou 'celula_alvo' for None
        # IndexError ocorre se o .split() não encontrar nada
        print(f"Erro ao processar o HTML: {e}")
        return None

def consulta_nome_inss(asc_code):
    
    if not asc_code:
        print("Código ASC não encontrado.")
    elif asc_code == "0002464889":
        return "Araguaia Shopping"
    elif asc_code == "0003178766":
        return "Goiânia Shopping"
    elif asc_code == "0004885160":
        return "Buriti Shopping"
    elif asc_code == "0003178021":
        return "Brasil Park Shopping"
    else:
        return "Não encontrado"


def extrai_dados_os(os_inss, cookies):
    dados_full = fetch_os_data(object_id= os_inss, cookies=cookies, inss=True)
    html = dados_full['html_os']
    soup = BeautifulSoup(html, 'html.parser')
    
    # Encontra a tabela com a classe 'table'
    serial =  extract_js_variable(soup, '_l.SERIAL_NO')
    os_csp = extrair_os_relacionada(html)
    print(os_csp)
    dados2 = fetch_os_data(object_id=os_csp)
    html2 = dados2['html_os']
    asc_code = extrair_codigo_asc(html2)
    os_cos = obter_os_correspondentes(serial)
    try:
        os_gspn = obter_os_correspondentes(os_cos)
    except:
        os_gspn = 'Não encontrado'
    if os_cos:
        dados_cos = coletar_dados_os(os_cos)
        status_cos1 = dados_cos['status_os']
        status_cos2 = dados_cos['descricao_status']
    else:
        status_cos1 = 'Não encontrado'
        status_cos2 = 'Não encontrado'
    nome_inss = consulta_nome_inss(asc_code)
    dados = {
        'SERIAL_NO': serial,
        'ASC_CODE': asc_code,
        'UNIDADE': nome_inss,
        'OS_INSS': os_inss,
        'OS_COS': os_cos,
        'OS_CSP_GSPN': os_gspn,
        'STATUS_COS': status_cos2,
    }
    return dados

if __name__ == "__main__":
    dados_full = fetch_os_data(object_id= 4173223584, inss=True)
    html = dados_full['html_os']
    print(extrai_dados_os(html))