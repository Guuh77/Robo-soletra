import re
import os # Importar para lidar com caminhos de arquivo

def remove_palavras_duplicadas(nome_arquivo_entrada, nome_arquivo_saida):
    """
    Lê um arquivo de texto, remove palavras duplicadas, filtra caracteres especiais
    e escreve o resultado em um novo arquivo.

    Args:
        nome_arquivo_entrada (str): O nome do arquivo de onde ler as palavras.
        nome_arquivo_saida (str): O nome do arquivo onde salvar as palavras únicas.
    """
    palavras_unicas = set()

    try:
        # Garante que o diretório de saída exista
        diretorio_saida = os.path.dirname(nome_arquivo_saida)
        if diretorio_saida and not os.path.exists(diretorio_saida):
            os.makedirs(diretorio_saida)

        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f_entrada:
            for linha in f_entrada:
                # Remove espaços em branco extras e encontra todas as "palavras"
                # Uma palavra é definida como uma sequência de letras e números.
                # re.findall(r'\b\w+\b', ...) encontra todas as sequências de caracteres alfanuméricos.
                # Poderíamos usar r'[a-zA-Z0-9]+' se quiséssemos apenas letras e números.
                palavras_na_linha = re.findall(r'[a-zA-Z0-9]+', linha.lower()) # Convertendo para minúsculas aqui

                for palavra in palavras_na_linha:
                    # Opcional: remover acentos se necessário (exige a biblioteca unidecode)
                    # if unidecode:
                    #     palavra = unidecode(palavra)

                    if palavra: # Garante que a palavra não está vazia após a limpeza
                        palavras_unicas.add(palavra)

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return

    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f_saida:
            for palavra in sorted(list(palavras_unicas)):
                f_saida.write(palavra + '\n')
        print(f"As palavras duplicadas foram removidas e filtradas. As palavras únicas foram salvas em '{nome_arquivo_saida}'.")
    except Exception as e:
        print(f"Ocorreu um erro ao escrever no arquivo: {e}")

# Nome do seu arquivo de entrada (usando r'' para raw string para evitar problemas com '\d')
arquivo_entrada = r'dup\dups.txt'
# Nome do arquivo de saída onde as palavras sem duplicatas serão salvas
arquivo_saida = r'dup\mno_dups.txt'

# Chama a função para remover as duplicatas
remove_palavras_duplicadas(arquivo_entrada, arquivo_saida)