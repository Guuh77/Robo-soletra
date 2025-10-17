def extrair_primeiras_palavras(arquivo_entrada, arquivo_saida):
    """
    Lê um arquivo de texto linha por linha, extrai a palavra antes da primeira vírgula
    de cada linha e salva essas palavras em um novo arquivo.

    Args:
        arquivo_entrada (str): O caminho para o arquivo .txt de onde ler (ex: 'palavros.txt').
        arquivo_saida (str): O caminho para o arquivo .txt onde salvar as palavras extraídas.
    """
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_entrada:
            palavras_extraidas = []
            for linha in f_entrada:
                linha = linha.strip()  # Remove espaços em branco e quebras de linha
                if linha:  # Garante que a linha não está vazia
                    # Divide a linha na primeira vírgula e pega a primeira parte
                    partes = linha.split(',', 1) # O '1' garante que divide apenas na primeira vírgula
                    palavra = partes[0]
                    palavras_extraidas.append(palavra)

        with open(arquivo_saida, 'w', encoding='utf-8') as f_saida:
            for palavra in palavras_extraidas:
                f_saida.write(palavra + '\n')

        print(f"Primeiras palavras extraídas com sucesso de '{arquivo_entrada}' e salvas em '{arquivo_saida}'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# --- Modo de uso ---
if __name__ == "__main__":
    # Corrigido: Usando 'palavros.txt' como nome do arquivo de entrada
    nome_arquivo_entrada = 'teste\palavros.txt'

    # Defina o nome do arquivo de saída onde as palavras serão salvas
    nome_arquivo_saida = 'teste\correcoes.txt'

    # Chame a função para executar a tarefa
    extrair_primeiras_palavras(nome_arquivo_entrada, nome_arquivo_saida)

    # Opcional: Você pode verificar o conteúdo do arquivo de saída
    print("\nConteúdo do arquivo 'correcoes.txt':")
    try:
        with open(nome_arquivo_saida, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print("Arquivo de saída não encontrado (possivelmente um erro anterior impediu sua criação).")