def limpar_lista_palavras(arquivo_entrada, arquivo_saida, tamanho_minimo=2):
    """
    Lê um arquivo com uma palavra por linha, remove as linhas que contêm
    palavras menores ou iguais ao tamanho_minimo e cria um novo arquivo
    com a lista limpa, sem linhas em branco.

    Args:
        arquivo_entrada (str): O nome do arquivo de texto de entrada.
        arquivo_saida (str): O nome do arquivo de texto de saída.
        tamanho_minimo (int): O tamanho mínimo que uma palavra deve ter para ser mantida.
                              Por padrão, remove palavras com 2 ou menos letras.
    """
    try:
        palavras_mantidas = 0
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_entrada, \
             open(arquivo_saida, 'w', encoding='utf-8') as f_saida:

            for linha in f_entrada:
                # Remove espaços em branco e quebras de linha do início/fim
                palavra = linha.strip()
                
                # Se a palavra (depois de limpar os espaços) não estiver vazia
                # e tiver um tamanho maior que o mínimo, escrevemos no novo arquivo.
                if len(palavra) > tamanho_minimo:
                    f_saida.write(linha) # Escreve a linha original (com o \n)
                    palavras_mantidas += 1

        print(f"Arquivo '{arquivo_saida}' criado com sucesso!")
        print(f"{palavras_mantidas} palavras foram mantidas.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Nomes dos arquivos de entrada e saída
arquivo_entrada = "robo-soletra\onelet\onelet.txt"
arquivo_saida = "robo-soletra\onelet\onelet_corrigido.txt"

# Chama a função para remover palavras com 2 ou menos letras
limpar_lista_palavras(arquivo_entrada, arquivo_saida, tamanho_minimo=2)