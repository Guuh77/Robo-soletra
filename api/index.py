import requests
import string
import time  # Importa a biblioteca de tempo

# Import para desabilitar os avisos de segurança ao ignorar a verificação SSL
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Desabilitar os avisos sobre a verificação SSL não ser segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_words_by_starting_letter(letter):
    """
    Busca palavras que começam com uma determinada letra na API do Dicionário Aberto.

    Args:
        letter (str): A letra inicial das palavras a serem pesquisadas.

    Returns:
        list: Uma lista de palavras que começam com a letra especificada.
              Retorna uma lista vazia se a solicitação falhar.
    """
    # URL CORRETA da API para busca por prefixo
    url = f"http://dicionario-aberto.net/search-json?prefix={letter}"
    
    try:
        # Adicionado o parâmetro verify=False para ignorar o erro de SSL
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP
        
        # O novo endpoint retorna a lista diretamente
        data = response.json()
        # A estrutura da resposta é uma lista de dicionários, cada um com a chave 'word'
        return [entry.get("word") for entry in data if entry.get("word")]

    except requests.exceptions.JSONDecodeError:
        print(f"A resposta para a letra '{letter}' não foi um JSON válido. A API pode estar offline ou o endpoint mudou.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar palavras com a letra '{letter}': {e}")
        return []

def create_word_list_file(filename="palavras5.txt"):
    """
    Cria um arquivo de texto contendo todas as palavras da API do Dicionário Aberto.

    Args:
        filename (str, optional): O nome do arquivo a ser criado.
                                  O padrão é "palavras.txt".
    """
    all_words = set()
    alphabet = string.ascii_lowercase
    
    for letter in alphabet:
        print(f"Buscando palavras que começam com a letra '{letter}'...")
        words = get_words_by_starting_letter(letter)
        if words:
            print(f"Encontradas {len(words)} palavras com a letra '{letter}'.")
            all_words.update(words)
        else:
            print(f"Nenhuma palavra encontrada para a letra '{letter}'.")
        
        # Pausa de 1 segundo entre as requisições para não sobrecarregar a API
        time.sleep(1)

    if all_words:
        print("\nOrdenando e salvando as palavras no arquivo...")
        with open(filename, "w", encoding="utf-8") as f:
            for word in sorted(list(all_words)):
                f.write(f"{word}\n")
        print(f"Arquivo '{filename}' criado com sucesso com {len(all_words)} palavras.")
    else:
        print("\nNão foi possível obter nenhuma palavra da API.")

if __name__ == "__main__":
    create_word_list_file()