import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- PARTE 1: O "CÉREBRO" DO ROBÔ (COM LÓGICA CORRETA DE CARACTERES) ---

def normalizar_palavra(texto):
    """
    Normaliza uma string para as regras do Soletra:
    - Converte vogais acentuadas para suas formas sem acento (á -> a).
    - MANTÉM o 'ç' como uma letra distinta do 'c'.
    - Converte tudo para minúsculas.
    """
    texto = texto.lower()
    # Mapa de substituição apenas para vogais acentuadas
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
    }
    
    # Cria a nova string substituindo apenas os caracteres do mapa
    texto_normalizado = "".join(mapa_acentos.get(char, char) for char in texto)
    return texto_normalizado

def carregar_dicionario(caminho_arquivo='palavras4.txt'):
    print(f"Carregando o dicionário '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            # Carregamos as palavras originais, com acentos e ç
            palavras = {linha.strip() for linha in f}
            print(f"Dicionário carregado com {len(palavras)} palavras.")
            return palavras
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de dicionário '{caminho_arquivo}' não foi encontrado.")
        return None

def encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario):
    """
    Versão final: Usa a normalização inteligente que diferencia 'c' de 'ç'.
    """
    print("Caçando palavras válidas com a lógica correta (c != ç)...")
    palavras_encontradas = []
    
    # Normalizamos as letras do jogo uma única vez para eficiência
    letra_central_norm = normalizar_palavra(letra_central)
    letras_disponiveis_norm_set = set(normalizar_palavra(letras_disponiveis))

    for palavra_original in dicionario:
        if len(palavra_original) < 4:
            continue
        
        # Normalizamos a palavra do dicionário para a verificação
        palavra_norm = normalizar_palavra(palavra_original)
        
        # Regra 1: A letra central (normalizada) deve estar na palavra (normalizada)
        if letra_central_norm not in palavra_norm:
            continue
        
        # Regra 2: Todas as letras da palavra (normalizada) devem estar no conjunto de letras disponíveis (normalizadas)
        if set(palavra_norm).issubset(letras_disponiveis_norm_set):
            # Adicionamos a palavra ORIGINAL à lista para ser digitada corretamente no jogo
            palavras_encontradas.append(palavra_original)
            
    palavras_encontradas.sort(key=len)
    
    print(f"Sucesso! {len(palavras_encontradas)} palavras válidas foram encontradas.")
    return palavras_encontradas


# --- PARTE 2: AUTOMAÇÃO DO JOGO (SEM MUDANÇAS) ---

def jogar_soletra():
    dicionario = carregar_dicionario()
    if not dicionario:
        return

    print("\nIniciando o navegador...")
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    wait = WebDriverWait(navegador, 15)
    
    try:
        navegador.get("https://g1.globo.com/jogos/soletra/")
        navegador.maximize_window()
        print("Página carregada.")

        # ETAPA 1: NAVEGAÇÃO
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
            print("Pop-up de cookies fechado.")
        except TimeoutException:
            print("Nenhum pop-up de cookie encontrado.")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']"))).click()
        print("Botão 'Iniciar' clicado.")
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']"))).click()
            print("Botão 'Jogar' do tutorial clicado.")
        except TimeoutException:
            print("Nenhuma tela de tutorial encontrada.")

        # ETAPA 2: EXTRAIR LETRAS E ENCONTRAR RESPOSTAS
        print("\n--- Jogo iniciado! Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.6)
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([letra.text for letra in letras_laterais_elementos])
        letras_disponiveis = letras_laterais_texto + letra_central
        print(f"Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"Letra obrigatória: {letra_central.upper()}")
        
        palavras_para_jogar = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        # ETAPA 3: JOGAR AS RESPOSTAS
        if not palavras_para_jogar:
            print("\nNenhuma palavra foi encontrada no dicionário para as letras de hoje.")
        else:
            print(f"\n--- Começando a digitar as {len(palavras_para_jogar)} respostas ---")
            campo_resposta = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Digite ou clique']")))
            botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Confirmar']")))
            
            for i, palavra in enumerate(palavras_para_jogar):
                campo_resposta.send_keys(palavra)
                time.sleep(0.3)
                botao_confirmar.click()
                print(f"({i+1}/{len(palavras_para_jogar)}) Enviada: {palavra}")
                time.sleep(0.5) 
            print("\nTodas as palavras foram enviadas! Jogo concluído.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a automação: {e}")
    finally:
        print("\nO robô vai fechar em 30 segundos para você ver o resultado.")
        time.sleep(10)
        navegador.quit()

if __name__ == "__main__":
    jogar_soletra()