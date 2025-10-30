import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --- O Cérebro Turbinado Do Robô ---


def normalizar_palavra(texto):
    texto = texto.lower()
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
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
    print("Caçando palavras válidas com a lógica correta...")
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


# --- Automação Turbo Do Jogo ---


def configurar_navegador_otimizado():
    """Configura Chrome com opções de performance"""
    opcoes = Options()
    opcoes.add_argument('--disable-blink-features=AutomationControlled')
    opcoes.add_argument('--disable-dev-shm-usage')
    opcoes.add_argument('--no-sandbox')
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    servico = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=servico, options=opcoes)


def ativar_jogo_clicando_letra_central(driver):
    """Clica na letra central e apaga para ativar o sistema"""
    try:
        print("\n🔧 Ativando sistema clicando na letra central...")
        
        letra_central_elemento = driver.find_element(By.CSS_SELECTOR, ".hexagon-cell.center")
        letra_central_elemento.click()
        print("✓ Letra central clicada!")
        time.sleep(0.3)
        
        input_elem = driver.find_element(By.ID, "input")
        input_elem.send_keys(Keys.BACKSPACE)
        print("✓ Letra apagada com Backspace!")
        time.sleep(0.3)
        
        driver.execute_script("document.getElementById('input').value = '';")
        print("✓ Campo limpo e sistema ativado!")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao ativar jogo: {e}")
        return False


def obter_progresso_jogo(driver):
    """Obtém o progresso atual do jogo (acertos/total)"""
    try:
        pontos_elem = driver.find_element(By.CSS_SELECTOR, "span.points")
        texto = pontos_elem.text
        acertos, total = map(int, texto.split('/'))
        return acertos, total
    except Exception as e:
        print(f"⚠️ Erro ao obter progresso: {e}")
        return 0, 0


def obter_palavras_faltantes_por_tamanho(driver):
    """Identifica quantas palavras faltam por número de letras"""
    try:
        word_boxes = driver.find_elements(By.CSS_SELECTOR, ".word-box")
        faltantes_por_tamanho = {}
        palavras_encontradas = []
        
        for box in word_boxes:
            # Verifica se tem a classe "found"
            if "found" in box.get_attribute("class"):
                # Palavra já encontrada
                try:
                    palavra = box.find_element(By.CSS_SELECTOR, "span.word").text
                    palavras_encontradas.append(palavra)
                except:
                    pass
            else:
                # Palavra faltante
                try:
                    length_text = box.find_element(By.CSS_SELECTOR, "span.length").text
                    num_letras = int(length_text.split()[0])
                    faltantes_por_tamanho[num_letras] = faltantes_por_tamanho.get(num_letras, 0) + 1
                except:
                    pass
        
        return faltantes_por_tamanho, palavras_encontradas
    except Exception as e:
        print(f"⚠️ Erro ao obter palavras faltantes: {e}")
        return {}, []


def enviar_palavra_ultra_rapido(driver, palavra):
    """Método ultra-rápido com FOCO no input"""
    try:
        script = f"""
        var input = document.getElementById('input');
        if (!input) {{
            return false;
        }}
        
        input.focus();
        input.value = '';
        input.value = '{palavra}';
        
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
        input.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true }}));
        
        setTimeout(function() {{
            var buttons = document.querySelectorAll('button');
            for (var btn of buttons) {{
                if (btn.textContent.includes('Confirmar')) {{
                    btn.click();
                    return true;
                }}
            }}
        }}, 15);
        
        return true;
        """
        
        resultado = driver.execute_script(script)
        time.sleep(0.04)
        
        return resultado if resultado else True
        
    except Exception as e:
        return False


def enviar_lote_palavras(driver, palavras, descricao=""):
    """Envia um lote de palavras e retorna estatísticas"""
    print(f"\n{'='*60}")
    print(f"📝 {descricao}")
    print(f"🎯 Enviando {len(palavras)} palavras...")
    print(f"{'='*60}\n")
    
    sucesso = 0
    tempo_inicio = time.time()
    
    for i, palavra in enumerate(palavras):
        if enviar_palavra_ultra_rapido(driver, palavra):
            sucesso += 1
        
        if (i + 1) % 50 == 0:
            tempo_decorrido = time.time() - tempo_inicio
            velocidade = sucesso / tempo_decorrido if tempo_decorrido > 0 else 0
            porcentagem = ((i + 1) / len(palavras)) * 100
            print(f"📊 [{porcentagem:5.1f}%] {i+1:4d}/{len(palavras)} | ⚡ {velocidade:.1f} p/s")
    
    tempo_total = time.time() - tempo_inicio
    return sucesso, tempo_total


def jogar_soletra():
    dicionario = carregar_dicionario()
    if not dicionario:
        return

    print("\nIniciando o navegador turbinado...")
    navegador = configurar_navegador_otimizado()
    wait = WebDriverWait(navegador, 20)
    
    try:
        navegador.get("https://g1.globo.com/jogos/soletra/")
        navegador.maximize_window()
        print("Página carregada.")
        time.sleep(2)

        # Navegação inicial
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
            print("Pop-up de cookies fechado.")
            time.sleep(0.5)
        except TimeoutException:
            print("Nenhum pop-up de cookie encontrado.")
        
        botao_iniciar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']")))
        botao_iniciar.click()
        print("Botão 'Iniciar' clicado.")
        time.sleep(1.5)
        
        try:
            botao_jogar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']")))
            botao_jogar.click()
            print("Botão 'Jogar' do tutorial clicado.")
        except TimeoutException:
            print("Nenhuma tela de tutorial encontrada.")
        
        print("\n⏳ Aguardando Svelte renderizar o jogo...")
        wait.until(EC.presence_of_element_located((By.ID, "input")))
        time.sleep(2)
        print("✓ Input encontrado e pronto!")

        # Extrair Letras
        print("\n--- Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([letra.text for letra in letras_laterais_elementos])
        letras_disponiveis = letras_laterais_texto + letra_central
        
        print(f"Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"Letra obrigatória: {letra_central.upper()}")
        
        todas_palavras = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        if not todas_palavras:
            print("\nNenhuma palavra foi encontrada no dicionário.")
            return
        
        print(f"\n{'='*60}")
        print(f"🚀 MODO TURBO COM RETRY INTELIGENTE ATIVADO!")
        print(f"📝 Total de palavras no dicionário: {len(todas_palavras)}")
        print(f"{'='*60}")
        
        # Ativar o jogo
        ativar_jogo_clicando_letra_central(navegador)
        
        # Sistema de tentativas com retry inteligente
        max_tentativas = 5
        tentativa = 1
        palavras_para_enviar = todas_palavras.copy()
        
        tempo_total_inicio = time.time()
        
        while tentativa <= max_tentativas:
            print(f"\n{'#'*60}")
            print(f"🔄 TENTATIVA {tentativa}/{max_tentativas}")
            print(f"{'#'*60}")
            
            # Enviar palavras
            sucesso, tempo = enviar_lote_palavras(
                navegador, 
                palavras_para_enviar,
                f"Tentativa {tentativa} - {len(palavras_para_enviar)} palavras"
            )
            
            time.sleep(1)
            
            # Verificar progresso
            acertos, total = obter_progresso_jogo(navegador)
            faltantes_por_tamanho, palavras_acertadas = obter_palavras_faltantes_por_tamanho(navegador)
            
            print(f"\n{'='*60}")
            print(f"📊 RESULTADO DA TENTATIVA {tentativa}:")
            print(f"{'='*60}")
            print(f"   ✓ Progresso: {acertos}/{total}")
            print(f"   📈 Taxa de acerto: {(acertos/total*100):.1f}%")
            print(f"   ⏱️  Tempo da tentativa: {tempo:.2f}s")
            
            if faltantes_por_tamanho:
                print(f"\n   🔍 Palavras faltantes por tamanho:")
                for tamanho, quantidade in sorted(faltantes_por_tamanho.items()):
                    print(f"      • {tamanho} letras: {quantidade} palavra(s)")
            
            print(f"{'='*60}")
            
            # Verificar se completou
            if acertos == total:
                tempo_total_final = time.time() - tempo_total_inicio
                print(f"\n{'🎉'*20}")
                print(f"🏆 PERFEITO! TODAS AS {total} PALAVRAS ENCONTRADAS!")
                print(f"🎯 Completado na tentativa {tentativa}")
                print(f"⏱️  Tempo total: {tempo_total_final:.2f} segundos")
                print(f"{'🎉'*20}")
                break
            
            # Se não completou, preparar próxima tentativa
            if tentativa < max_tentativas:
                print(f"\n🔄 Preparando tentativa {tentativa + 1}...")
                print(f"   📋 Filtrando apenas palavras faltantes...")
                
                # Converter palavras acertadas para set normalizado
                palavras_acertadas_norm = {normalizar_palavra(p) for p in palavras_acertadas}
                
                # Filtrar palavras que ainda faltam
                palavras_para_enviar = [
                    p for p in todas_palavras 
                    if normalizar_palavra(p) not in palavras_acertadas_norm and
                    len(p) in faltantes_por_tamanho
                ]
                
                print(f"   ✓ {len(palavras_para_enviar)} palavras filtradas para retry")
                
                # Re-ativar o jogo
                time.sleep(1)
                ativar_jogo_clicando_letra_central(navegador)
                
                tentativa += 1
            else:
                tempo_total_final = time.time() - tempo_total_inicio
                print(f"\n{'⚠️'*20}")
                print(f"❌ Limite de {max_tentativas} tentativas atingido")
                print(f"📊 Resultado final: {acertos}/{total} ({(acertos/total*100):.1f}%)")
                print(f"⏱️  Tempo total: {tempo_total_final:.2f} segundos")
                print(f"{'⚠️'*20}")
                break

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n⏳ O robô vai fechar em 30 segundos para você ver o resultado.")
        time.sleep(30)
        navegador.quit()


if __name__ == "__main__":
    jogar_soletra()
