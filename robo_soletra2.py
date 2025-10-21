import time
import pickle
import sys
from typing import Set, List, Optional
from collections import Counter
from colorama import init, Fore, Style

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inicializa o Colorama para que as cores funcionem no terminal
init(autoreset=True)

# --- CONFIGURAÇÕES GERAIS ---
URL_JOGO = "https://g1.globo.com/jogos/soletra/"
ARQUIVO_DICIONARIO_TXT = "palavras4.txt"
ARQUIVO_DICIONARIO_CACHE = "dicionario.pkl"
TEMPO_ESPERA_MAXIMO = 15
TEMPO_FINAL_VISUALIZACAO = 20 # Aumentado para dar tempo de ver o resultado final

# --- FUNÇÕES AUXILIARES E "CÉREBRO" ---

def imprimir_barra_progresso(iteracao, total, prefixo='', sufixo='', comprimento=50, preenchimento='█'):
    """Cria e exibe uma barra de progresso dinâmica no terminal."""
    percentual = ("{0:.1f}").format(100 * (iteracao / float(total)))
    preenchido = int(comprimento * iteracao // total)
    barra = preenchimento * preenchido + '-' * (comprimento - preenchido)
    sys.stdout.write(f'\r{prefixo} |{barra}| {percentual}% {sufixo}')
    sys.stdout.flush()

def normalizar_palavra(texto: str) -> str:
    texto = texto.lower()
    mapa_acentos = {'á':'a','à':'a','â':'a','ã':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u'}
    return "".join(mapa_acentos.get(char, char) for char in texto)

def carregar_dicionario() -> Optional[Set[str]]:
    try:
        with open(ARQUIVO_DICIONARIO_CACHE, 'rb') as f:
            palavras = pickle.load(f)
            print(Fore.GREEN + f"Dicionário carregado rapidamente do cache com {len(palavras)} palavras.")
            return palavras
    except (FileNotFoundError, EOFError):
        print(Fore.YELLOW + f"Cache não encontrado. Carregando de '{ARQUIVO_DICIONARIO_TXT}'...")
        try:
            with open(ARQUIVO_DICIONARIO_TXT, 'r', encoding='utf-8') as f:
                palavras = {linha.strip() for linha in f if linha.strip()}
                print(Fore.GREEN + f"Dicionário carregado. Criando cache para futuras execuções...")
                with open(ARQUIVO_DICIONARIO_CACHE, 'wb') as pkl_f:
                    pickle.dump(palavras, pkl_f)
                return palavras
        except FileNotFoundError:
            print(Fore.RED + f"ERRO CRÍTICO: O arquivo '{ARQUIVO_DICIONARIO_TXT}' não foi encontrado.")
            return None

def encontrar_palavras_validas(letras_disponiveis: str, letra_central: str, dicionario: Set[str]) -> List[str]:
    print("Caçando palavras válidas...")
    pangramas, outras_palavras = [], []
    letra_central_norm = normalizar_palavra(letra_central)
    letras_disponiveis_norm_set = set(normalizar_palavra(letras_disponiveis))

    for palavra_original in dicionario:
        if len(palavra_original) < 4: continue
        palavra_norm = normalizar_palavra(palavra_original)
        if letra_central_norm not in palavra_norm: continue
        
        if set(palavra_norm).issubset(letras_disponiveis_norm_set):
            if len(set(palavra_norm)) == 7:
                pangramas.append(palavra_original)
            else:
                outras_palavras.append(palavra_original)
            
    pangramas.sort(key=len)
    outras_palavras.sort(key=len)
    
    return pangramas + outras_palavras

# --- PARTE PRINCIPAL: AUTOMAÇÃO DO JOGO ---

def jogar_soletra():
    dicionario = carregar_dicionario()
    if not dicionario: return

    print(Fore.CYAN + "\nIniciando o navegador...")
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Limpa o terminal
    
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico, options=options)
    wait = WebDriverWait(navegador, TEMPO_ESPERA_MAXIMO)
    
    try:
        navegador.get(URL_JOGO)
        navegador.maximize_window()
        print("Página carregada.")

        # NAVEGAÇÃO
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
        except TimeoutException: pass
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']"))).click()
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']"))).click()
        except TimeoutException: pass

        # EXTRAIR LETRAS E ENCONTRAR RESPOSTAS
        print(Style.BRIGHT + "\n--- Jogo iniciado! Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.6)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_disponiveis = "".join([l.text for l in letras_laterais_elementos]) + letra_central
        
        print(f"Letras disponíveis: {Fore.YELLOW}{letras_disponiveis.upper()}")
        print(f"Letra obrigatória: {Fore.YELLOW}{letra_central.upper()}")
        
        palavras_para_jogar = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        # JOGAR AS RESPOSTAS
        if not palavras_para_jogar:
            print(Fore.RED + "\nNenhuma palavra foi encontrada no dicionário para as letras de hoje.")
        else:
            print(Style.BRIGHT + f"\n--- Começando a digitar as {len(palavras_para_jogar)} respostas ---")
            campo_resposta = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Digite ou clique']")))
            botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Confirmar']")))
            
            total_palavras = len(palavras_para_jogar)
            imprimir_barra_progresso(0, total_palavras, prefixo='Progresso:', sufixo='Completo')
            
            for i, palavra in enumerate(palavras_para_jogar):
                campo_resposta.send_keys(palavra)
                time.sleep(0.05)
                botao_confirmar.click()
                time.sleep(0.2)
                imprimir_barra_progresso(i + 1, total_palavras, prefixo='Progresso:', sufixo=f'Enviada: {palavra}')

            print() # Nova linha após a barra de progresso
            print(Fore.GREEN + "\nTodas as palavras foram enviadas! Jogo concluído.")
            
            # RELATÓRIO FINAL
            pangramas = [p for p in palavras_para_jogar if len(set(normalizar_palavra(p))) == 7]
            contagem_por_tamanho = Counter(len(p) for p in palavras_para_jogar)

            print(Style.BRIGHT + "\n--- RELATÓRIO FINAL ---")
            print(f"Total de Palavras Válidas Encontradas: {Fore.CYAN}{total_palavras}")
            if pangramas:
                print(f"Pangrama(s): {Fore.YELLOW}{', '.join(p.upper() for p in pangramas)}")
            print("\nDistribuição por Tamanho:")
            for tamanho, contagem in sorted(contagem_por_tamanho.items()):
                print(f"  - {tamanho} letras: {contagem} palavras")
            print("------------------------")

    except Exception as e:
        print(Fore.RED + f"\nOcorreu um erro inesperado durante a automação: {e}")
    finally:
        print(f"\nRobô finalizado. A janela ficará aberta por {TEMPO_FINAL_VISUALIZACAO} segundos.")
        time.sleep(TEMPO_FINAL_VISUALIZACAO)
        navegador.quit()

if __name__ == "__main__":
    jogar_soletra()