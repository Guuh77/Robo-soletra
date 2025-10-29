def remove_palavras_duplicadas(nome_arquivo_entrada, nome_arquivo_saida):
    palavras_unicas = set() # Usamos um set para armazenar palavras únicas por sua natureza de não permitir duplicatas

    try:
        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f_entrada:
            for linha in f_entrada:
                # Remove espaços em branco extras e divide a linha em palavras
                palavras = linha.strip().split()
                for palavra in palavras:
                    # Adiciona a palavra ao set. Se já existir, não será adicionada novamente.
                    palavras_unicas.add(palavra)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return

    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f_saida:
            for palavra in sorted(list(palavras_unicas)): # Opcional: ordenar as palavras antes de escrever
                f_saida.write(palavra + '\n')
        print(f"As palavras duplicadas foram removidas. As palavras únicas foram salvas em '{nome_arquivo_saida}'.")
    except Exception as e:
        print(f"Ocorreu um erro ao escrever no arquivo: {e}")

# Nome do seu arquivo de entrada
arquivo_entrada = 'Robo-soletra\dup\dups.txt'
# Nome do arquivo de saída onde as palavras sem duplicatas serão salvas
arquivo_saida = 'Robo-soletra\dup\mno_dups.txt'

# Chama a função para remover as duplicatas
remove_palavras_duplicadas(arquivo_entrada, arquivo_saida)