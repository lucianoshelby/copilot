from bs4 import BeautifulSoup

def coletar_dados_cos(os_numero, session):
    """Coleta todas as informações necessárias da OS no COS via requests."""
    url_cos = f"http://192.168.25.131:8080/COS_CSO/EditarOrdemServico.jsp?NumeroOSBusca={os_numero}"

    print(f"🔍 Acessando página da OS: {url_cos}")

    # 📌 Fazer requisição GET para obter a página
    response = session.get(url_cos, headers=HEADERS, cookies=session.cookies, verify=False)

    if response.status_code != 200:
        print(f"❌ Erro ao acessar a página: {response.status_code}")
        return None

    # 📌 Usar BeautifulSoup para processar o HTML
    soup = BeautifulSoup(response.text, "html.parser")
    dados_cos = {}

    # 🟢 Capturar o status da OS
    status_element = soup.find(id="StatusAtual")
    dados_cos["status_os"] = status_element.text.strip() if status_element else "Não encontrado"

    # 🟢 Capturar o tipo de atendimento
    atendimento_element = soup.find(id="Atendimento")
    dados_cos["tipo_atendimento"] = atendimento_element.text.strip() if atendimento_element else "Não encontrado"

    # 🟢 Capturar as peças pedidas no GSPN
    pecas_gspn = []
    todas_entregues = True
    linhas_pecas = soup.select("#tbPecaPedidaGSPN tr")

    for linha in linhas_pecas:
        codigo_peca = linha.find(id="CodigoPeca").text.strip() if linha.find(id="CodigoPeca") else "Desconhecido"
        status_peca = linha.find(id="Status").text.strip() if linha.find(id="Status") else "Desconhecido"

        if status_peca.lower() != "entregue":
            todas_entregues = False
            pecas_gspn.append({"codigo": codigo_peca, "status": status_peca})

    dados_cos["pecas_gspn"] = "Todas as peças foram entregues" if todas_entregues else pecas_gspn

    # 🟢 Capturar as peças requisitadas no estoque
    pecas_requisitadas = []
    elementos_pecas = soup.find_all(id="CodigoPeca")

    for peca in elementos_pecas:
        codigo_texto = peca.text.strip().split("|")[0].strip()
        pecas_requisitadas.append(codigo_texto)

    dados_cos["pecas_requisitadas"] = pecas_requisitadas if pecas_requisitadas else "Não encontrado"

    return dados_cos
