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
ARQUIVO_DICIONARIO = "correcoes.txt"
ARQUIVO_RESPOSTAS_DO_DIA = "respostas_do_dia.txt"

# NOVOS ARQUIVOS DE APRENDIZADO
ARQUIVO_PALAVRAS_ACEITAS = "palavras_aceitas.txt"
ARQUIVO_PALAVRAS_RECUSADAS = "palavras_recusadas.txt"

TEMPO_ESPERA_MAXIMO = 15
TEMPO_FINAL_VISUALIZACAO = 15 # Reduzido para conveniência


# --- PARTE 1: O "CÉREBRO" DO ROBÔ ---

def normalizar_palavra(texto: str) -> str:
    """Normaliza vogais acentuadas, mas mantém 'ç' distinto de 'c'."""
    texto = texto.lower()
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'é': 'e', 'ê': 'e',
        'í': 'i', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u',
    }
    return "".join(mapa_acentos.get(char, char) for char in texto)

def carregar_set_de_arquivo(caminho_arquivo: str) -> Set[str]:
    """Função auxiliar para carregar um arquivo de texto em um set."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return {linha.strip().lower() for linha in f if linha.strip()}
    except FileNotFoundError:
        return set() # Retorna um set vazio se o arquivo não existir

def encontrar_palavras_validas(letras_disponiveis: str, letra_central: str, dicionario: Set[str], palavras_recusadas: Set[str]) -> List[str]:
    """Filtra o dicionário, agora ignorando palavras que já foram recusadas anteriormente."""
    print("Caçando palavras válidas e ignorando as já recusadas...")
    pangramas, outras_palavras = [], []
    letra_central_norm = normalizar_palavra(letra_central)
    letras_disponiveis_norm_set = set(normalizar_palavra(letras_disponiveis))

    for palavra_original in dicionario:
        # NOVO: Pula a palavra se ela já foi recusada no passado
        if palavra_original.lower() in palavras_recusadas:
            continue
            
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
        print(f"✨ PANGRAMA ENCONTRADO: {' | '.join(p.upper() for p in pangramas)}")
        
    palavras_encontradas = pangramas + outras_palavras
    print(f"Sucesso! {len(palavras_encontradas)} palavras candidatas foram encontradas.")
    return palavras_encontradas


# --- PARTE 2: AUTOMAÇÃO DO JOGO ---

def jogar_soletra():
    dicionario_completo = carregar_set_de_arquivo(ARQUIVO_DICIONARIO)
    if not dicionario_completo:
        return

    # NOVO: Carrega o conhecimento prévio do robô
    palavras_recusadas = carregar_set_de_arquivo(ARQUIVO_PALAVRAS_RECUSADAS)
    print(f"O robô já aprendeu a ignorar {len(palavras_recusadas)} palavras.")

    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    wait = WebDriverWait(navegador, TEMPO_ESPERA_MAXIMO)
    
    try:
        navegador.get(URL_JOGO)
        navegador.maximize_window()
        # ETAPA 1: NAVEGAÇÃO
        # ... (código de navegação sem alterações) ...
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
        except TimeoutException:
            pass
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']"))).click()
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']"))).click()
        except TimeoutException:
            pass
            
        # ETAPA 2: EXTRAIR LETRAS E ENCONTRAR RESPOSTAS
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elems = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_disponiveis = "".join([elem.text for elem in letras_laterais_elems]) + letra_central
        
        palavras_para_jogar = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario_completo, palavras_recusadas)
        
        # ETAPA 3: JOGAR, VERIFICAR E APRENDER
        if not palavras_para_jogar:
            print("\nNenhuma palavra candidata foi encontrada.")
        else:
            print(f"\n--- Começando a digitar as {len(palavras_para_jogar)} palavras ---")
            campo_resposta = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Digite ou clique']")))
            botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Confirmar']")))
            
            # Lê as palavras que já estão na tela antes de começar
            palavras_ja_na_tela = {e.text.lower() for e in navegador.find_elements(By.CSS_SELECTOR, ".word-box.found")}

            for i, palavra in enumerate(palavras_para_jogar, 1):
                if palavra.lower() in palavras_ja_na_tela:
                    continue

                campo_resposta.send_keys(palavra)
                time.sleep(0.05) # Pausa mínima
                botao_confirmar.click()
                
                # CORREÇÃO DE VELOCIDADE: Pausa drasticamente reduzida
                time.sleep(0.2) 

                # NOVO: Lógica de verificação e aprendizado
                palavras_na_tela_agora = {e.text.lower() for e in navegador.find_elements(By.CSS_SELECTOR, ".word-box.found")}
                if palavra.lower() in palavras_na_tela_agora and palavra.lower() not in palavras_ja_na_tela:
                    print(f"({i}/{len(palavras_para_jogar)}) ✅ Aceita: {palavra}")
                    with open(ARQUIVO_PALAVRAS_ACEITAS, 'a', encoding='utf-8') as f:
                        f.write(palavra.lower() + '\n')
                    palavras_ja_na_tela.add(palavra.lower())
                else:
                    print(f"({i}/{len(palavras_para_jogar)}) ❌ Recusada: {palavra}")
                    with open(ARQUIVO_PALAVRAS_RECUSADAS, 'a', encoding='utf-8') as f:
                        f.write(palavra.lower() + '\n')

            print("\nTodas as palavras foram enviadas! Jogo concluído.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a automação: {e}")
    finally:
        print(f"\nO robô vai fechar em {TEMPO_FINAL_VISUALIZACAO} segundos.")
        time.sleep(TEMPO_FINAL_VISUALIZACAO)
        navegador.quit()

if __name__ == "__main__":
    jogar_soletra()