import fitz  # PyMuPDF
import os      # Biblioteca para interagir com o sistema operacional

def extrair_palavras_negrito(caminho_pdf, caminho_txt):
    """
    Extrai palavras em negrito de um arquivo PDF e as salva em um arquivo de texto.

    Argumentos:
        caminho_pdf (str): O caminho para o arquivo PDF de entrada.
        caminho_txt (str): O caminho para o arquivo de texto de saída.
    """
    # Verifica se o arquivo PDF existe antes de tentar abri-lo
    if not os.path.exists(caminho_pdf):
        print(f"Erro: O arquivo '{caminho_pdf}' não foi encontrado.")
        print("Por favor, verifique se o nome do arquivo está correto e se ele está na mesma pasta do script.")
        return

    palavras_negrito = []
    try:
        documento = fitz.open(caminho_pdf)
    except Exception as e:
        print(f"Erro ao tentar abrir o arquivo PDF: {e}")
        return

    print(f"Lendo o arquivo '{caminho_pdf}'...")

    # Itera por cada página do documento
    for pagina_num in range(len(documento)):
        pagina = documento.load_page(pagina_num)
        # Extrai o texto da página em formato de dicionário para obter detalhes da fonte
        blocos = pagina.get_text("dict")["blocks"]
        for bloco in blocos:
            if "lines" in bloco:  # Garante que há linhas de texto no bloco
                for linha in bloco["lines"]:
                    for span in linha["spans"]:
                        # A identificação de negrito é feita verificando o nome da fonte.
                        # Nomes de fontes em negrito geralmente contêm "bold", "cn", "cb", etc.
                        if "bold" in span["font"].lower():
                            # Pega o texto do span, remove espaços extras nas pontas e divide em palavras
                            palavras = span["text"].strip().split()
                            if palavras: # Garante que não adiciona listas vazias
                                palavras_negrito.extend(palavras)

    # Fecha o documento PDF para liberar recursos
    documento.close()

    if not palavras_negrito:
        print("Nenhuma palavra em negrito foi encontrada no documento.")
        return

    # Tenta escrever as palavras encontradas no arquivo de texto de saída
    try:
        with open(caminho_txt, "w", encoding="utf-8") as f:
            for palavra in palavras_negrito:
                f.write(palavra + "\n")
        print(f"Sucesso! {len(palavras_negrito)} palavras em negrito foram extraídas e salvas em '{caminho_txt}'")
    except Exception as e:
        print(f"Erro ao escrever no arquivo de texto: {e}")

# --- INSTRUÇÕES DE USO ---

# 1. Coloque o seu arquivo PDF na mesma pasta que este script Python.
# 2. Altere o nome do arquivo aqui para corresponder ao seu.
caminho_arquivo_pdf = 'dict.pdf'

# 3. Defina o nome do arquivo de texto que será criado com o resultado.
caminho_arquivo_txt = 'resultado_negrito.txt'

# 4. Execute o script.
# Chama a função principal para iniciar a extração
extrair_palavras_negrito(caminho_arquivo_pdf, caminho_arquivo_txt)