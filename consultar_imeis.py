"""def calcular_check_digit(imei14):
    ""Calcula o dígito verificador de um IMEI usando Luhn.""
    soma = 0
    for i, digito in enumerate(imei14):
        n = int(digito)
        if i % 2 == 1:  # posições pares no índice (começando do 0) são dobradas
            n *= 2
            if n > 9:
                n -= 9
        soma += n
    return str((10 - (soma % 10)) % 10)

def gerar_imeis(tac, inicio_snr, fim_snr):
    imeis = []
    for snr in range(fim_snr, inicio_snr - 1, -1):  # do mais recente pro mais antigo
        base = f"{tac}{snr:06d}"
        check = calcular_check_digit(base)
        imeis.append(base + check)
    return imeis

# Configuração
TAC = "35344374"       # Identificado para o Galaxy S22 Plus preto
inicio_SNR = 511000    # intervalo inicial estimado
fim_SNR = 518000       # intervalo final estimado

# Gerar IMEIs
lista_imeis = gerar_imeis(TAC, inicio_SNR, fim_SNR)

# Exibir os primeiros 10 mais recentes
for imei in lista_imeis[:10]:
    print(imei)

if __name__ == "__main__":
    TAC = "35082856"
    inicio_SNR = 0510000
    fim_SNR = 0519999
    lista_imeis = gerar_imeis(TAC, inicio_SNR, fim_SNR)
    for imei in lista_imeis:
        print(imei)"""

def calcular_check_digit(imei14):
    """Calcula o dígito verificador de um IMEI (Luhn). Recebe string de 14 dígitos."""
    imei14 = str(imei14)
    if len(imei14) != 14 or not imei14.isdigit():
        raise ValueError("IMEI precisa ser uma string de 14 dígitos para calcular o check digit.")
    soma = 0
    for i, digito in enumerate(imei14):
        n = int(digito)
        # algoritmo Luhn usado para IMEI
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        soma += n
    return str((10 - (soma % 10)) % 10)

def gerar_imeis(tac, inicio_snr, fim_snr, snr_digits=6, descending=True):
    """
    - tac: string ou int (se tiver zeros à esquerda passe como string)
    - inicio_snr, fim_snr: int ou string. Se for string, infere-se a largura do SNR.
    - snr_digits: largura do SNR (default 6).
    """
    tac_str = str(tac)
    if not tac_str.isdigit():
        raise ValueError("TAC precisa conter apenas dígitos (se tiver zeros à esquerda, passe como string).")

    def to_int(x):
        if isinstance(x, str):
            if not x.isdigit():
                raise ValueError("SNR em string deve conter apenas dígitos")
            return int(x)
        return int(x)

    start = to_int(inicio_snr)
    end = to_int(fim_snr)

    # se o usuário passou strings para inicio/fim, deduzimos snr_digits
    if isinstance(inicio_snr, str) or isinstance(fim_snr, str):
        snr_digits = max(len(str(inicio_snr)), len(str(fim_snr)))

    low, high = min(start, end), max(start, end)
    rng = range(high, low - 1, -1) if descending else range(low, high + 1)

    imeis = []
    for snr_val in rng:
        base = f"{tac_str}{snr_val:0{snr_digits}d}"  # padding com zeros à esquerda
        if len(base) != 14:
            raise ValueError(
                f"Comprimento da base IMEI incorreto ({len(base)}). "
                f"TAC='{tac_str}' + SNR com {snr_digits} dígitos -> '{base}'. Ajuste snr_digits ou TAC."
            )
        check = calcular_check_digit(base)
        imeis.append(base + check)
    return imeis


if __name__ == "__main__":
    TAC = "35017561"
    inicio_SNR = "057734"
    fim_SNR = "058734"
    lista_imeis = gerar_imeis(TAC, inicio_SNR, fim_SNR)
    for imei in lista_imeis:
        print(imei)
#lista = gerar_imeis("35082856", "051000", "051010")
