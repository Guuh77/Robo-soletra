import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- PARTE 1: O "CÉREBRO" DO ROBÔ (NÃO MUDA) ---

def normalizar_palavra(texto):
    texto = texto.lower()
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'é': 'e', 'ê': 'e', 'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o', 'ú': 'u',
    }
    texto_normalizado = "".join(mapa_acentos.get(char, char) for char in texto)
    return texto_normalizado

def carregar_dicionario(caminho_arquivo='Robo-soletra/Robo/palavras3.txt'):
    print(f"Carregando o dicionário '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            palavras = {linha.strip() for linha in f}
            print(f"Dicionário carregado com {len(palavras)} palavras.")
            return palavras
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de dicionário '{caminho_arquivo}' não foi encontrado.")
        return None

def encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario):
    print("Caçando palavras válidas com a lógica correta (c != ç)...")
    palavras_encontradas = []
    letra_central_norm = normalizar_palavra(letra_central)
    letras_disponiveis_norm_set = set(normalizar_palavra(letras_disponiveis))
    for palavra_original in dicionario:
        if len(palavra_original) < 4:
            continue
        palavra_norm = normalizar_palavra(palavra_original)
        if letra_central_norm not in palavra_norm:
            continue
        if set(palavra_norm).issubset(letras_disponiveis_norm_set):
            palavras_encontradas.append(palavra_original)
    palavras_encontradas.sort(key=len)
    print(f"Sucesso! {len(palavras_encontradas)} palavras válidas foram encontradas.")
    return palavras_encontradas


# --- PARTE 2: AUTOMAÇÃO DO JOGO (VERSÃO COM SINCRONIZAÇÃO ABSOLUTA) ---

def jogar_soletra():
    dicionario = carregar_dicionario()
    if not dicionario:
        return

    print("\nIniciando o navegador...")
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    wait = WebDriverWait(navegador, 5) # Espera de 5 segundos é mais que suficiente para a sincronização
    
    try:
        navegador.get("https://g1.globo.com/jogos/soletra/")
        navegador.maximize_window()
        print("Página carregada.")

        # ETAPA 1
        wait_longo = WebDriverWait(navegador, 15)
        try:
            wait_longo.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
            print("Pop-up de cookies fechado.")
        except TimeoutException:
            print("Nenhum pop-up de cookie encontrado.")
        wait_longo.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']"))).click()
        print("Botão 'Iniciar' clicado.")
        try:
            wait_longo.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']"))).click()
            print("Botão 'Jogar' do tutorial clicado.")
        except TimeoutException:
            print("Nenhuma tela de tutorial encontrada.")

        # ETAPA 2
        print("\n--- Jogo iniciado! Lendo o tabuleiro... ---")
        wait_longo.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([letra.text for letra in letras_laterais_elementos])
        letras_disponiveis = letras_laterais_texto + letra_central
        print(f"Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"Letra obrigatória: {letra_central.upper()}")
        
        palavras_para_jogar = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        # --- ETAPA 3: A LÓGICA INFALÍVEL ---
        if not palavras_para_jogar:
            print("\nNenhuma palavra foi encontrada no dicionário para as letras de hoje.")
        else:
            print(f"\n--- Começando a digitar as {len(palavras_para_jogar)} respostas com sincronização total ---")
            
            seletor_campo = (By.CSS_SELECTOR, "input[placeholder='Digite ou clique']")
            seletor_toast = (By.CSS_SELECTOR, "div.toast") # O seletor da mensagem de popup

            campo_resposta = wait.until(EC.presence_of_element_located(seletor_campo))
            botao_confirmar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Confirmar']")))
            
            for i, palavra in enumerate(palavras_para_jogar):
                try:
                    # Passo 1: Limpa e envia a palavra
                    campo_resposta.clear()
                    campo_resposta.send_keys(palavra)
                    
                    # Passo 2: Clica da forma mais robusta possível
                    navegador.execute_script("arguments[0].click();", botao_confirmar)
                    print(f"({i+1}/{len(palavras_para_jogar)}) Enviada: {palavra}")

                    # Passo 3: A SINCRONIZAÇÃO ABSOLUTA
                    # Espera a mensagem de popup (toast) FICAR INVISÍVEL.
                    # Se o toast não aparecer (caso raro), a espera de 5s vai falhar (TimeoutException),
                    # o que é bom, pois nos permite continuar para a próxima palavra.
                    wait.until(EC.invisibility_of_element_located(seletor_toast))
                
                except StaleElementReferenceException:
                    # Se a página recarregar os elementos, os reencontramos
                    print("Elemento obsoleto, reencontrando...")
                    campo_resposta = wait.until(EC.presence_of_element_located(seletor_campo))
                    botao_confirmar = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Confirmar']")))
                    # Tentamos de novo a mesma palavra
                    campo_resposta.clear()
                    campo_resposta.send_keys(palavra)
                    navegador.execute_script("arguments[0].click();", botao_confirmar)
                    wait.until(EC.invisibility_of_element_located(seletor_toast))

                except TimeoutException:
                    # Se o toast NUNCA DESAPARECER (improvável) ou se o toast NUNCA APARECER,
                    # o wait vai falhar. Em ambos os casos, a melhor ação é continuar.
                    print(f"Sincronização com o popup falhou para a palavra '{palavra}'. Continuando...")
                    continue


            print("\nTodas as palavras foram enviadas! Jogo concluído.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a automação: {e}")
    finally:
        print("\nO robô vai fechar em 10 segundos para você ver o resultado.")
        time.sleep(10)
        navegador.quit()

if __name__ == "__main__":
    jogar_soletra()