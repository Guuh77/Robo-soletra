import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --- CONFIGURAÇÕES ---
HISTORICO_FILE = "historico_soletra.csv"


# --- O Cérebro Turbinado Com Machine Learning ---


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
    print(f"📚 Carregando o dicionário '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            palavras = {linha.strip() for linha in f}
            print(f"✓ Dicionário carregado com {len(palavras)} palavras.")
            return palavras
    except FileNotFoundError:
        print(f"❌ ERRO: O arquivo de dicionário '{caminho_arquivo}' não foi encontrado.")
        return None


def encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario):
    print("🔍 Caçando palavras válidas...")
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
    
    print(f"✓ {len(palavras_encontradas)} palavras válidas encontradas.")
    return palavras_encontradas


# --- MACHINE LEARNING: HISTÓRICO E PRIORIZAÇÃO ---


def carregar_historico():
    """Carrega histórico de palavras que funcionaram antes"""
    if os.path.exists(HISTORICO_FILE):
        df = pd.read_csv(HISTORICO_FILE)
        print(f"📊 Histórico carregado: {len(df)} registros")
        return df
    else:
        print("📊 Nenhum histórico encontrado. Criando novo...")
        return pd.DataFrame(columns=["palavra", "foi_aceita", "tamanho", "frequencia"])


def atualizar_historico(palavras_aceitas, palavras_rejeitadas):
    """Atualiza o histórico com novos resultados (Machine Learning)"""
    historico = carregar_historico()
    
    # Adicionar palavras aceitas
    for palavra in palavras_aceitas:
        if palavra in historico['palavra'].values:
            # Incrementa frequência
            historico.loc[historico['palavra'] == palavra, 'frequencia'] += 1
        else:
            # Nova entrada
            novo_registro = pd.DataFrame([{
                "palavra": palavra, 
                "foi_aceita": 1,
                "tamanho": len(palavra),
                "frequencia": 1
            }])
            historico = pd.concat([historico, novo_registro], ignore_index=True)
    
    # Adicionar palavras rejeitadas (aprendizado negativo)
    for palavra in palavras_rejeitadas:
        if palavra not in historico['palavra'].values:
            novo_registro = pd.DataFrame([{
                "palavra": palavra, 
                "foi_aceita": 0,
                "tamanho": len(palavra),
                "frequencia": 0
            }])
            historico = pd.concat([historico, novo_registro], ignore_index=True)
    
    historico.to_csv(HISTORICO_FILE, index=False)
    print(f"💾 Histórico atualizado: {len(palavras_aceitas)} aceitas, {len(palavras_rejeitadas)} rejeitadas")


def priorizar_palavras_ml(palavras):
    """Usa Machine Learning para priorizar palavras com maior probabilidade de sucesso"""
    historico = carregar_historico()
    
    if historico.empty:
        print("🤖 ML: Sem dados históricos. Usando ordem padrão.")
        return palavras
    
    # Calcular score de cada palavra baseado no histórico
    palavras_com_score = []
    
    for palavra in palavras:
        if palavra in historico['palavra'].values:
            registro = historico[historico['palavra'] == palavra].iloc[0]
            # Score baseado em: foi_aceita (peso 10) + frequencia (peso 2)
            score = (registro['foi_aceita'] * 10) + (registro['frequencia'] * 2)
        else:
            # Palavras novas recebem score médio
            score = 5
        
        palavras_com_score.append((palavra, score))
    
    # Ordenar por score (maior primeiro) e depois por tamanho (menor primeiro)
    palavras_com_score.sort(key=lambda x: (-x[1], len(x[0])))
    
    palavras_priorizadas = [p[0] for p in palavras_com_score]
    
    print(f"🤖 ML: Palavras priorizadas com base no histórico")
    return palavras_priorizadas


# --- AUTOMAÇÃO TURBO DO JOGO ---


def configurar_navegador_otimizado(headless=False):
    """Configura Chrome com opções de performance"""
    opcoes = Options()
    
    if headless:
        opcoes.add_argument('--headless=new')
    
    opcoes.add_argument('--disable-blink-features=AutomationControlled')
    opcoes.add_argument('--disable-gpu')
    opcoes.add_argument('--disable-dev-shm-usage')
    opcoes.add_argument('--no-sandbox')
    opcoes.add_argument('--window-size=1920,1080')
    opcoes.add_argument('--log-level=3')
    opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    servico = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=servico, options=opcoes)


def ativar_jogo_clicando_letra_central(driver):
    """Clica na letra central e apaga para ativar o sistema"""
    try:
        print("\n🔧 Ativando sistema clicando na letra central...")
        
        letra_central_elemento = driver.find_element(By.CSS_SELECTOR, ".hexagon-cell.center")
        letra_central_elemento.click()
        time.sleep(0.3)
        
        input_elem = driver.find_element(By.ID, "input")
        input_elem.send_keys(Keys.BACKSPACE)
        time.sleep(0.3)
        
        driver.execute_script("document.getElementById('input').value = '';")
        print("✓ Sistema ativado!")
        
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
        return 0, 0


def obter_palavras_faltantes_por_tamanho(driver):
    """Identifica quantas palavras faltam por número de letras"""
    try:
        word_boxes = driver.find_elements(By.CSS_SELECTOR, ".word-box")
        faltantes_por_tamanho = {}
        palavras_encontradas = []
        
        for box in word_boxes:
            if "found" in box.get_attribute("class"):
                try:
                    palavra = box.find_element(By.CSS_SELECTOR, "span.word").text
                    palavras_encontradas.append(palavra)
                except:
                    pass
            else:
                try:
                    length_text = box.find_element(By.CSS_SELECTOR, "span.length").text
                    num_letras = int(length_text.split()[0])
                    faltantes_por_tamanho[num_letras] = faltantes_por_tamanho.get(num_letras, 0) + 1
                except:
                    pass
        
        return faltantes_por_tamanho, palavras_encontradas
    except Exception as e:
        return {}, []


def enviar_palavra_ultra_rapido(driver, palavra):
    """Método ultra-rápido com JavaScript puro"""
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
        
        driver.execute_script(script)
        time.sleep(0.04)
        return True
        
    except Exception as e:
        return False


def enviar_lote_palavras_com_tracking(driver, palavras, descricao=""):
    """Envia palavras e rastreia quais foram aceitas vs rejeitadas"""
    print(f"\n{'='*60}")
    print(f"📝 {descricao}")
    print(f"🎯 Enviando {len(palavras)} palavras...")
    print(f"{'='*60}\n")
    
    palavras_aceitas = []
    palavras_rejeitadas = []
    
    tempo_inicio = time.time()
    
    acertos_anterior, total = obter_progresso_jogo(driver)
    
    for i, palavra in enumerate(palavras):
        # Envia palavra
        enviar_palavra_ultra_rapido(driver, palavra)
        
        # Aguarda um pouco para processar
        time.sleep(0.06)
        
        # Verifica se foi aceita
        acertos_atual, _ = obter_progresso_jogo(driver)
        
        if acertos_atual > acertos_anterior:
            palavras_aceitas.append(palavra)
            acertos_anterior = acertos_atual
            status = "✅"
        else:
            palavras_rejeitadas.append(palavra)
            status = "❌"
        
        # Mostrar progresso a cada 50 palavras
        if (i + 1) % 50 == 0:
            tempo_decorrido = time.time() - tempo_inicio
            velocidade = (i + 1) / tempo_decorrido if tempo_decorrido > 0 else 0
            porcentagem = ((i + 1) / len(palavras)) * 100
            print(f"📊 [{porcentagem:5.1f}%] {i+1:4d}/{len(palavras)} | ✅ {len(palavras_aceitas)} | ❌ {len(palavras_rejeitadas)} | ⚡ {velocidade:.1f} p/s")
    
    tempo_total = time.time() - tempo_inicio
    
    return palavras_aceitas, palavras_rejeitadas, tempo_total


def jogar_soletra_ml(headless=False):
    """Versão definitiva com Machine Learning"""
    dicionario = carregar_dicionario()
    if not dicionario:
        return

    print("\n" + "="*60)
    print("🤖 ROBÔ SOLETRA ULTIMATE - COM MACHINE LEARNING")
    print("="*60)
    
    navegador = configurar_navegador_otimizado(headless=headless)
    wait = WebDriverWait(navegador, 20)
    
    try:
        navegador.get("https://g1.globo.com/jogos/soletra/")
        if not headless:
            navegador.maximize_window()
        print("\n✓ Página carregada.")
        time.sleep(2)

        # Navegação inicial
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "cookie-ok-button"))).click()
            time.sleep(0.5)
        except TimeoutException:
            pass
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Iniciar']"))).click()
        time.sleep(1.5)
        
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Jogar']"))).click()
        except TimeoutException:
            pass
        
        print("\n⏳ Aguardando jogo carregar...")
        wait.until(EC.presence_of_element_located((By.ID, "input")))
        time.sleep(2)

        # Extrair Letras
        print("\n--- Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([letra.text for letra in letras_laterais_elementos])
        letras_disponiveis = letras_laterais_texto + letra_central
        
        print(f"✓ Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"✓ Letra obrigatória: {letra_central.upper()}")
        
        # Encontrar palavras válidas
        todas_palavras = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        if not todas_palavras:
            print("\n❌ Nenhuma palavra foi encontrada.")
            return
        
        # MACHINE LEARNING: Priorizar palavras
        palavras_priorizadas = priorizar_palavras_ml(todas_palavras)
        
        print(f"\n{'='*60}")
        print(f"🚀 MODO TURBO COM ML E RETRY INTELIGENTE!")
        print(f"📝 Total de palavras: {len(palavras_priorizadas)}")
        print(f"{'='*60}")
        
        # Ativar o jogo
        ativar_jogo_clicando_letra_central(navegador)
        
        # Sistema de tentativas
        max_tentativas = 5
        tentativa = 1
        palavras_para_enviar = palavras_priorizadas.copy()
        todas_aceitas = []
        todas_rejeitadas = []
        
        tempo_total_inicio = time.time()
        
        while tentativa <= max_tentativas:
            print(f"\n{'#'*60}")
            print(f"🔄 TENTATIVA {tentativa}/{max_tentativas}")
            print(f"{'#'*60}")
            
            # Enviar palavras com tracking
            aceitas, rejeitadas, tempo = enviar_lote_palavras_com_tracking(
                navegador, 
                palavras_para_enviar,
                f"Tentativa {tentativa} - {len(palavras_para_enviar)} palavras"
            )
            
            todas_aceitas.extend(aceitas)
            todas_rejeitadas.extend(rejeitadas)
            
            time.sleep(1)
            
            # Verificar progresso
            acertos, total = obter_progresso_jogo(navegador)
            faltantes_por_tamanho, palavras_acertadas = obter_palavras_faltantes_por_tamanho(navegador)
            
            print(f"\n{'='*60}")
            print(f"📊 RESULTADO DA TENTATIVA {tentativa}:")
            print(f"{'='*60}")
            print(f"   ✓ Progresso: {acertos}/{total}")
            print(f"   ✅ Aceitas nesta tentativa: {len(aceitas)}")
            print(f"   ❌ Rejeitadas nesta tentativa: {len(rejeitadas)}")
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
            
            # Preparar próxima tentativa
            if tentativa < max_tentativas:
                print(f"\n🔄 Preparando tentativa {tentativa + 1}...")
                
                palavras_acertadas_norm = {normalizar_palavra(p) for p in palavras_acertadas}
                
                palavras_para_enviar = [
                    p for p in todas_palavras 
                    if normalizar_palavra(p) not in palavras_acertadas_norm and
                    len(p) in faltantes_por_tamanho
                ]
                
                # Re-priorizar com ML
                palavras_para_enviar = priorizar_palavras_ml(palavras_para_enviar)
                
                print(f"   ✓ {len(palavras_para_enviar)} palavras filtradas para retry")
                
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
        
        # Atualizar histórico com Machine Learning
        print("\n💾 Atualizando histórico com Machine Learning...")
        atualizar_historico(todas_aceitas, todas_rejeitadas)
        print("✓ Histórico atualizado! O robô ficará mais inteligente na próxima execução.")

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n⏳ Fechando navegador em 30 segundos...")
        time.sleep(30)
        navegador.quit()


if __name__ == "__main__":
    # headless=False para ver o navegador | headless=True para rodar sem interface
    jogar_soletra_ml(headless=False)
