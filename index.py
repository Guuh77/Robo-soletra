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
    """Carrega histórico de palavras ACEITAS anteriormente"""
    if os.path.exists(HISTORICO_FILE):
        try:
            df = pd.read_csv(HISTORICO_FILE)
            print(f"📊 Histórico ML carregado: {len(df)} palavras ACEITAS")
            return df
        except Exception as e:
            print(f"⚠️ Erro ao carregar histórico: {e}. Criando novo...")
            return pd.DataFrame(columns=["palavra", "tamanho", "frequencia"])
    else:
        print("📊 Nenhum histórico encontrado. Será criado após vitória completa.")
        return pd.DataFrame(columns=["palavra", "tamanho", "frequencia"])


def salvar_historico_vitoria(palavras_aceitas):
    """Salva APENAS palavras aceitas no histórico - SÓ CHAMADO QUANDO GANHA 100%"""
    historico = carregar_historico()
    
    print(f"\n💾 Salvando histórico de VITÓRIA com {len(palavras_aceitas)} palavras aceitas...")
    
    # Adicionar/atualizar palavras aceitas
    for palavra in palavras_aceitas:
        if palavra in historico['palavra'].values:
            # Incrementa frequência
            idx = historico[historico['palavra'] == palavra].index[0]
            historico.at[idx, 'frequencia'] = historico.at[idx, 'frequencia'] + 1
        else:
            # Nova palavra aceita
            novo_registro = pd.DataFrame([{
                "palavra": palavra, 
                "tamanho": len(palavra),
                "frequencia": 1
            }])
            historico = pd.concat([historico, novo_registro], ignore_index=True)
    
    # Salvar histórico
    historico.to_csv(HISTORICO_FILE, index=False)
    print(f"✅ Histórico salvo com sucesso: {len(historico)} palavras no total")
    print(f"   📁 Arquivo: {HISTORICO_FILE}")


def priorizar_palavras_ml(palavras):
    """Usa histórico para priorizar palavras aceitas anteriormente"""
    historico = carregar_historico()
    
    if historico.empty:
        print("🤖 ML: Sem histórico. Primeira execução - usando ordem padrão.")
        return palavras
    
    # Criar dicionário de scores para acesso rápido
    score_dict = {}
    palavras_conhecidas = 0
    
    for _, row in historico.iterrows():
        palavra = row['palavra']
        # Score: frequencia * 100 (quanto mais aceita, maior prioridade)
        score = row['frequencia'] * 100
        score_dict[palavra] = score
        palavras_conhecidas += 1
    
    print(f"🤖 ML: {palavras_conhecidas} palavras no histórico")
    
    # Atribuir scores
    palavras_com_score = []
    
    for palavra in palavras:
        if palavra in score_dict:
            score = score_dict[palavra]
        else:
            # Palavras novas recebem score baseado no tamanho
            score = 50 - len(palavra)
        
        palavras_com_score.append((palavra, score))
    
    # Ordenar por score (MAIOR primeiro)
    palavras_com_score.sort(key=lambda x: (-x[1], len(x[0])))
    palavras_priorizadas = [p[0] for p in palavras_com_score]
    
    # Mostrar top 10
    palavras_do_historico = [p for p in palavras_priorizadas if p in score_dict]
    if palavras_do_historico:
        top_10 = palavras_do_historico[:min(10, len(palavras_do_historico))]
        print(f"🤖 ML: Top 10 do histórico: {', '.join(top_10)}")
    
    return palavras_priorizadas


# --- AUTOMAÇÃO TURBO DO JOGO ---


def configurar_navegador_otimizado(headless=False):
    """Configura Chrome com opções de performance máxima"""
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
        time.sleep(0.2)
        
        input_elem = driver.find_element(By.ID, "input")
        input_elem.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)
        
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


def obter_palavras_acertadas(driver):
    """Extrai lista de palavras que foram ACEITAS pelo jogo"""
    try:
        word_boxes = driver.find_elements(By.CSS_SELECTOR, ".word-box.found")
        palavras_aceitas = []
        
        for box in word_boxes:
            try:
                palavra = box.find_element(By.CSS_SELECTOR, "span.word").text
                if palavra:
                    palavras_aceitas.append(palavra)
            except:
                pass
        
        return palavras_aceitas
    except Exception as e:
        return []


def enviar_palavra_ultra_rapido(driver, palavra):
    """Método EXTREMAMENTE rápido - 25+ palavras/segundo"""
    try:
        script = f"""
        var input = document.getElementById('input');
        if (!input) return false;
        
        input.focus();
        input.value = '{palavra}';
        
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        input.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true }}));
        
        var buttons = document.querySelectorAll('button');
        for (var btn of buttons) {{
            if (btn.textContent.includes('Confirmar')) {{
                btn.click();
                break;
            }}
        }}
        return true;
        """
        
        driver.execute_script(script)
        time.sleep(0.03)
        return True
        
    except Exception as e:
        return False


def enviar_lote_palavras_ultra_rapido(driver, palavras, tentativa_num):
    """Envia palavras em velocidade máxima"""
    print(f"\n{'='*60}")
    print(f"🎯 Tentativa {tentativa_num}: Enviando {len(palavras)} palavras...")
    print(f"{'='*60}\n")
    
    tempo_inicio = time.time()
    acertos_anterior, total = obter_progresso_jogo(driver)
    
    for i, palavra in enumerate(palavras):
        enviar_palavra_ultra_rapido(driver, palavra)
        
        # Verifica a cada 20 palavras
        if (i + 1) % 20 == 0 or (i + 1) == len(palavras):
            acertos_atual, total_atual = obter_progresso_jogo(driver)
            
            # Se completou, encerra imediatamente
            if acertos_atual >= total_atual and total_atual > 0:
                tempo_decorrido = time.time() - tempo_inicio
                velocidade = (i + 1) / tempo_decorrido if tempo_decorrido > 0 else 0
                
                print(f"\n{'🎉'*30}")
                print(f"🏆 TODAS AS PALAVRAS ENCONTRADAS!")
                print(f"✓ Completado em {i + 1} palavras enviadas")
                print(f"⚡ Velocidade: {velocidade:.1f} palavras/segundo")
                print(f"⏱️  Tempo: {tempo_decorrido:.2f} segundos")
                print(f"{'🎉'*30}\n")
                
                return tempo_decorrido, True
            
            acertos_anterior = acertos_atual
            
            # Mostrar progresso a cada 100
            if (i + 1) % 100 == 0:
                tempo_decorrido = time.time() - tempo_inicio
                velocidade = (i + 1) / tempo_decorrido if tempo_decorrido > 0 else 0
                porcentagem = ((i + 1) / len(palavras)) * 100
                print(f"📊 [{porcentagem:5.1f}%] {i+1:4d}/{len(palavras)} | ⚡ {velocidade:.1f} p/s | 🎯 {acertos_atual}/{total_atual}")
    
    time.sleep(0.5)
    tempo_total = time.time() - tempo_inicio
    
    return tempo_total, False


def jogar_soletra_ml(headless=False):
    """Versão definitiva - Salva histórico SÓ quando ganhar tudo"""
    dicionario = carregar_dicionario()
    if not dicionario:
        return

    print("\n" + "="*60)
    print("🤖 ROBÔ SOLETRA ULTIMATE - VELOCIDADE MÁXIMA + ML")
    print("="*60)
    
    navegador = configurar_navegador_otimizado(headless=headless)
    wait = WebDriverWait(navegador, 20)
    
    try:
        navegador.get("https://g1.globo.com/jogos/soletra/")
        if not headless:
            navegador.maximize_window()
        print("\n✓ Página carregada.")
        time.sleep(2)

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

        print("\n--- Lendo o tabuleiro... ---")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "letters")))
        time.sleep(0.5)
        
        letra_central = navegador.find_element(By.CSS_SELECTOR, ".hexagon-cell.center .cell-letter").text
        letras_laterais_elementos = navegador.find_elements(By.CSS_SELECTOR, ".hexagon-cell.outer .cell-letter")
        letras_laterais_texto = "".join([letra.text for letra in letras_laterais_elementos])
        letras_disponiveis = letras_laterais_texto + letra_central
        
        print(f"✓ Letras disponíveis: {letras_disponiveis.upper()}")
        print(f"✓ Letra obrigatória: {letra_central.upper()}")
        
        todas_palavras = encontrar_palavras_validas(letras_disponiveis, letra_central, dicionario)
        
        if not todas_palavras:
            print("\n❌ Nenhuma palavra foi encontrada.")
            return
        
        # Priorizar com ML
        palavras_priorizadas = priorizar_palavras_ml(todas_palavras)
        
        print(f"\n{'='*60}")
        print(f"🚀 MODO LOOP INFINITO ATÉ VITÓRIA!")
        print(f"📝 Total de palavras: {len(palavras_priorizadas)}")
        print(f"⚡ Alvo: 25-30 palavras/segundo")
        print(f"{'='*60}")
        
        ativar_jogo_clicando_letra_central(navegador)
        
        # LOOP INFINITO até completar
        tentativa = 1
        completou = False
        tempo_total_inicio = time.time()
        
        while not completou:
            print(f"\n{'#'*60}")
            print(f"🔄 TENTATIVA {tentativa}")
            print(f"{'#'*60}")
            
            tempo, completou_agora = enviar_lote_palavras_ultra_rapido(
                navegador, 
                palavras_priorizadas,
                tentativa
            )
            
            completou = completou_agora
            time.sleep(0.5)
            
            acertos, total = obter_progresso_jogo(navegador)
            
            print(f"\n{'='*60}")
            print(f"📊 RESULTADO DA TENTATIVA {tentativa}:")
            print(f"{'='*60}")
            print(f"   ✓ Progresso: {acertos}/{total}")
            print(f"   📈 Taxa de acerto: {(acertos/total*100) if total > 0 else 0:.1f}%")
            print(f"   ⏱️  Tempo: {tempo:.2f}s")
            print(f"{'='*60}")
            
            if completou or acertos >= total:
                tempo_total_final = time.time() - tempo_total_inicio
                
                # Extrair palavras que foram REALMENTE aceitas
                palavras_aceitas_reais = obter_palavras_acertadas(navegador)
                
                print(f"\n{'🎉'*20}")
                print(f"🏆 VITÓRIA COMPLETA! {total} PALAVRAS!")
                print(f"🎯 Completado na tentativa {tentativa}")
                print(f"⏱️  Tempo total: {tempo_total_final:.2f} segundos")
                print(f"✅ Palavras aceitas extraídas: {len(palavras_aceitas_reais)}")
                print(f"{'🎉'*20}")
                
                # SALVA O HISTÓRICO SÓ QUANDO GANHA TUDO
                salvar_historico_vitoria(palavras_aceitas_reais)
                
                break
            
            # Se não completou, tenta novamente
            print(f"\n⚠️ Não completou na tentativa {tentativa}. Tentando novamente...")
            time.sleep(1)
            ativar_jogo_clicando_letra_central(navegador)
            tentativa += 1

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n⏳ Fechando navegador em 30 segundos...")
        time.sleep(30)
        navegador.quit()


if __name__ == "__main__":
    jogar_soletra_ml(headless=False)
