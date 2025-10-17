import time
from typing import List, Set, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURAÇÕES GERAIS ---
URL_JOGO = "https://g1.globo.com/jogos/soletra/"
ARQUIVO_DICIONARIO = "palavras3.txt"
ARQUIVO_RESPOSTAS = "respostas_do_dia.txt"
TEMPO_ESPERA_MAXIMO = 15  # Segundos
TEMPO_FINAL_VISUALIZACAO = 20  # Segundos


# --- PARTE 1: O "CÉREBRO" DO ROBÔ ---

def normalizar_palavra(texto: str) -> str:
    """
    Normaliza vogais acentuadas (á -> a), mas mantém 'ç' distinto de 'c'.
    """
    texto = texto.lower()
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'é': 'e', 'ê': 'e',
        'í': 'i', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u',
    }
    return "".join(mapa_acentos.get(char, char) for char in texto)

def carregar_dicionario(caminho_arquivo: str) -> Optional[Set[str]]:
    """Lê o arquivo de dicionário e o carrega em um 'set' para busca rápida."""
    print(f"Carregando o dicionário '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            palavras = {linha.strip() for linha in f if linha.strip()}
            print(f"Dicionário carregado com {len(palavras)} palavras.")
            return palavras
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de dicionário '{caminho_arquivo}' não foi encontrado.")
        return None

def encontrar_palavras_validas(letras_disponiveis: str, letra_central: str, dicionario: Set[str]) -> List[str]:
    """Filtra o dicionário e retorna as palavras válidas, com o pangrama primeiro."""
    print("Caçando palavras válidas no dicionário...")
    pangramas, outras_palavras = [], []
    
    letra_central_norm = normalizar_palavra(letra_central)
    letras_disponiveis_norm_set = set(normalizar_palavra(letras_disponiveis))

    for palavra_original in dicionario:
        if len(palavra_original) < 4:
            continue
        
        palavra_norm = normalizar_palavra(palavra_original)
        
        if letra_central_norm not in palavra_norm:
            continue
        
        if set(palavra_norm).issubset(letras_disponiveis_norm_set):
            if len(set(palavra_norm)) == 7:
                pangramas.append(palavra_original)
            else:
                outras_palavras.append(palavra_original)
            
    pangramas.sort(key=len)
    outras_palavras.sort(key=len)
    
    if pangramas:
        print(f"✨ PANGRAMA ENCONCONTRADO: {' | '.join(p.upper() for p in pangramas)}")
        
    palavras_encontradas = pangramas + outras_palavras
    print(f"Sucesso! {len(palavras_encontradas)} palavras válidas foram encontradas.")
    return palavras_encontradas


# --- PARTE 2: AUTOMAÇÃO DO JOGO ---

def jogar_soletra():
    """Função principal que orquestra todo o processo do robô."""
    
    dicionario = carregar_dicionario(ARQUIVO_DICIONARIO)
    if not dicionario:
        return

    print("\nIniciando o navegador...")
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    wait = WebDriverWait(navegador, TEMPO_ESPERA_MAXIMO)
    
    try:
        navegador.get(URL_JOGO)
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

        # ETAPA 2: EXTRAIR LETRAS, ENCONTRAR RESPOSTAS E SALVAR
        print("\n--- Jogo iniciado! Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elems = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([elem.text for elem in letras_laterais_elems])
        letras_disponiveis = letras_laterais_texto + letra_central
        
        print(f"Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"Letra obrigatória: {letra_central.upper()}")
        
        palavras_para_jogar = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        if palavras_para_jogar:
            with open(ARQUIVO_RESPOSTAS, "w", encoding="utf-8") as f:
                f.write(f"Respostas para as letras: {letras_disponiveis.upper()} (Central: {letra_central.upper()})\n\n")
                for palavra in palavras_para_jogar:
                    f.write(palavra + "\n")
            print(f"Lista de respostas salva em '{ARQUIVO_RESPOSTAS}'")
        
        # ETAPA 3: JOGAR AS RESPOSTAS
        if not palavras_para_jogar:
            print("\nNenhuma palavra foi encontrada no dicionário para as letras de hoje.")
        else:
            print(f"\n--- Começando a digitar as {len(palavras_para_jogar)} respostas ---")
            campo_resposta = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Digite ou clique']")))
            botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Confirmar']")))
            
            for i, palavra in enumerate(palavras_para_jogar, 1):
                campo_resposta.send_keys(palavra)
                time.sleep(0.05) # Pausa mínima para digitação
                botao_confirmar.click()
                print(f"({i}/{len(palavras_para_jogar)}) Enviada: {palavra}")
                
                # VELOCIDADE AJUSTADA: Uma pausa confortável para observar
                time.sleep(0.3) 

            print("\nTodas as palavras foram enviadas! Jogo concluído.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a automação: {e}")
    finally:
        print(f"\nO robô vai fechar em {TEMPO_FINAL_VISUALIZACAO} segundos.")
        time.sleep(TEMPO_FINAL_VISUALIZACAO)
        navegador.quit()

if __name__ == "__main__":
    jogar_soletra()