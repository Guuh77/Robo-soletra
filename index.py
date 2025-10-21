import re
import unicodedata

# Define os nomes dos arquivos de entrada e saída
arquivo_de_entrada = "robo-soletra\correcoes.txt"
arquivo_de_saida = "robo-soletra\correcoes_formatado.txt"

try:
    # 1. Abre o arquivo original para leitura
    with open(arquivo_de_entrada, 'r', encoding='utf-8') as f_entrada:
        conteudo = f_entrada.read()

    # 2. Normaliza o texto para juntar caracteres decompostos (ex: 'c' + '¸' -> 'ç')
    conteudo_normalizado = unicodedata.normalize('NFC', conteudo)

    # 3. Encontra todas as sequências de letras, incluindo as acentuadas
    # Este padrão garante que palavras como "coração" e "paçoca" sejam capturadas corretamente
    palavras = re.findall(r'[a-zA-ZÀ-ÿ]+', conteudo_normalizado)

    # 4. Abre o novo arquivo para escrita
    with open(arquivo_de_saida, 'w', encoding='utf-8') as f_saida:
        # 5. Escreve a lista de palavras no novo arquivo, cada uma em sua própria linha
        f_saida.write('\n'.join(palavras))

    print(f"Sucesso! O arquivo '{arquivo_de_entrada}' foi lido e um novo arquivo formatado foi criado em '{arquivo_de_saida}'.")

except FileNotFoundError:
    print(f"ERRO: O arquivo de entrada '{arquivo_de_entrada}' não foi encontrado.")
    print("Verifique se o nome está correto e se o arquivo está na mesma pasta do script.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")