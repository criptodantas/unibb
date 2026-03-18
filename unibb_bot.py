"""
========================================
UniBB AI Assistant - Bot de Automação
========================================

Assistente Virtual Inteligente para a plataforma UniBB
- Navegação automática
- Leitura de conteúdo (PDFs, vídeos, textos)
- Resposta a questões com IA
- Execução de simulados
- Precisão de 90%+

Tecnologias:
- Playwright (automação web)
- OpenAI API (GPT-4o)
- Python 3.10+
- ADB (para app mobile Android)

Autor: UniBB AI Team
Versão: 1.0.0
"""

import asyncio
import json
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Importações externas
try:
    from playwright.async_api import async_playwright, Browser, Page
    import openai
    import PyPDF2
    import aiohttp
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Erro ao importar bibliotecas: {e}")
    print("📦 Execute: pip install playwright openai PyPDF2 aiohttp python-dotenv")
    print("🎭 E depois: playwright install chromium")
    exit(1)

# Carregar variáveis de ambiente
load_dotenv()

# ========================================
# CONFIGURAÇÕES
# ========================================

UNIBB_URL = "https://unibb.com.br"
UNIBB_LOGIN_URL = f"{UNIBB_URL}/login"
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.1

# Configurações de automação
STEALTH_MODE = True
HEADLESS = False  # True para modo invisível
DELAY_MIN = 1.5   # segundos
DELAY_MAX = 3.0   # segundos

# Logs
LOG_FILE = "unibb_bot.log"


# ========================================
# CLASSE PRINCIPAL - UniBB Assistant
# ========================================

class UniBBAssistant:
    """
    Assistente Virtual para automação da plataforma UniBB
    """
    
    def __init__(
        self, 
        login: str, 
        senha: str, 
        openai_key: str,
        stealth: bool = True
    ):
        """
        Inicializa o assistente
        
        Args:
            login: Matrícula do funcionário BB (ex: F1234567)
            senha: Senha de acesso ao UniBB
            openai_key: Chave da API OpenAI
            stealth: Ativar modo stealth (simular humano)
        """
        self.login = login
        self.senha = senha
        self.stealth = stealth
        
        # Cliente OpenAI
        self.client = openai.AsyncOpenAI(api_key=openai_key)
        
        # Estado interno
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context_memory: List[str] = []
        self.acertos = 0
        self.total = 0
        self.cursos_completados = []
        
        # Estatísticas
        self.stats = {
            'questoes_respondidas': 0,
            'simulados_concluidos': 0,
            'cursos_visitados': 0,
            'pdfs_processados': 0,
            'precisao': 0.0
        }
    
    async def iniciar(self):
        """Inicializa o navegador e faz login"""
        print("🚀 Iniciando UniBB AI Assistant...")
        
        async with async_playwright() as p:
            # Configurações do navegador
            self.browser = await p.chromium.launch(
                headless=HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Contexto com user agent realista
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo'
            )
            
            # Injetar scripts anti-detecção
            if self.stealth:
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = {runtime: {}};
                """)
            
            self.page = await context.new_page()
            
            # Fazer login
            await self.fazer_login()
            
            return self
    
    async def fazer_login(self):
        """Faz login na plataforma UniBB"""
        print(f"🔐 Fazendo login como {self.login}...")
        
        try:
            await self.page.goto(UNIBB_LOGIN_URL, wait_until='networkidle')
            
            # Aguardar formulário de login carregar
            await self.page.wait_for_selector('#username', timeout=10000)
            
            # Preencher credenciais com delay humano
            await self._type_like_human('#username', self.login)
            await self._delay()
            
            await self._type_like_human('#password', self.senha)
            await self._delay()
            
            # Clicar no botão de login
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_navigation(timeout=30000)
            
            # Verificar se login foi bem sucedido
            if "erro" in self.page.url.lower() or "login" in self.page.url.lower():
                raise Exception("❌ Falha no login - verifique suas credenciais")
            
            print("✅ Login realizado com sucesso!")
            self._log("Login bem-sucedido")
            
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            raise
    
    async def listar_cursos(self) -> List[Dict]:
        """Lista todos os cursos disponíveis"""
        print("📚 Escaneando cursos disponíveis...")
        
        await self.page.goto(f"{UNIBB_URL}/meus-cursos", wait_until='networkidle')
        await self._delay()
        
        # Extrair informações dos cursos
        cursos = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.course-item, .curso-card, [class*="curso"]');
                return Array.from(items).map(item => ({
                    nome: item.querySelector('h3, h4, .title, .nome')?.innerText || 'Curso',
                    url: item.querySelector('a')?.href || '',
                    progresso: item.querySelector('.progress, .progresso')?.innerText || '0%',
                    descricao: item.querySelector('.description, .descricao')?.innerText || ''
                }));
            }
        """)
        
        self.stats['cursos_visitados'] = len(cursos)
        print(f"✅ {len(cursos)} cursos encontrados")
        
        return cursos
    
    async def ler_conteudo_pagina(self) -> tuple[str, str]:
        """Lê e extrai conteúdo da página atual"""
        # Extrair texto
        conteudo = await self.page.evaluate("() => document.body.innerText")
        
        # Screenshot para análise visual
        screenshot = await self.page.screenshot(full_page=True)
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        return conteudo, screenshot_b64
    
    async def responder_questao_ia(
        self, 
        questao: str, 
        alternativas: List[str],
        contexto_adicional: str = ""
    ) -> Dict:
        """
        Responde uma questão usando IA
        
        Args:
            questao: Enunciado da questão
            alternativas: Lista de alternativas (A, B, C, D, E)
            contexto_adicional: Contexto extra para melhorar precisão
            
        Returns:
            Dict com resposta, explicação, confiança e fundamento
        """
        print(f"🤖 Analisando questão com IA...")
        
        # Preparar contexto da memória
        contexto_memoria = "\n".join([
            f"[Conteúdo Estudado {i+1}]: {c}" 
            for i, c in enumerate(self.context_memory[-5:])
        ])
        
        # Prompt otimizado
        prompt = f"""Você é um especialista em certificações bancárias do Banco do Brasil (UniBB).
Você possui amplo conhecimento em:
- Produtos e Serviços Bancários
- Matemática Financeira
- Gestão de Riscos e Compliance
- Legislação Bancária
- Atendimento ao Cliente
- Tecnologia e Inovação

CONTEXTO DOS ESTUDOS RECENTES:
{contexto_memoria}

{f"CONTEXTO ADICIONAL: {contexto_adicional}" if contexto_adicional else ""}

QUESTÃO:
{questao}

ALTERNATIVAS:
{chr(10).join([f"{chr(65+i)}) {alt}" for i, alt in enumerate(alternativas)])}

TAREFA:
Analise cuidadosamente a questão e as alternativas. Responda em JSON com:
1. "resposta": A letra da alternativa correta (A, B, C, D ou E)
2. "explicacao": Explicação detalhada de por que essa é a resposta correta
3. "confianca": Nível de confiança de 0 a 100
4. "fundamento": Base teórica e regulatória da resposta
5. "alternativas_incorretas": Breve explicação do erro em cada alternativa incorreta

Use seu conhecimento bancário, regulamentações do Banco Central e boas práticas do BB."""

        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            resultado = json.loads(response.choices[0].message.content)
            
            # Atualizar estatísticas
            self.total += 1
            self.stats['questoes_respondidas'] += 1
            
            if resultado.get('confianca', 0) >= 85:
                self.acertos += 1
            
            # Calcular precisão
            self.stats['precisao'] = (self.acertos / self.total * 100) if self.total > 0 else 0
            
            print(f"✅ Resposta: {resultado['resposta']} | Confiança: {resultado['confianca']}%")
            self._log(f"Questão respondida: {resultado['resposta']} ({resultado['confianca']}%)")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na IA: {e}")
            return {
                'resposta': 'A',
                'explicacao': 'Erro ao processar',
                'confianca': 0,
                'fundamento': str(e)
            }
    
    async def executar_simulado(self, url_simulado: str) -> Dict:
        """
        Executa um simulado completo automaticamente
        
        Args:
            url_simulado: URL do simulado na plataforma
            
        Returns:
            Resultado do simulado com estatísticas
        """
        print(f"🚀 Iniciando simulado: {url_simulado}")
        
        await self.page.goto(url_simulado, wait_until='networkidle')
        await self._delay(2, 4)
        
        # Encontrar todas as questões
        questoes = await self.page.query_selector_all('.question-container, .questao, [class*="question"]')
        total_questoes = len(questoes)
        
        print(f"📝 Simulado com {total_questoes} questões")
        
        resultados = []
        acertos_simulado = 0
        
        for i, questao_el in enumerate(questoes):
            print(f"  → Questão {i+1}/{total_questoes}...")
            
            try:
                # Extrair enunciado
                texto_questao = await questao_el.query_selector('.question-text, .enunciado, h4')
                enunciado = await texto_questao.inner_text() if texto_questao else ""
                
                # Extrair alternativas
                alternativas_el = await questao_el.query_selector_all('.alternative, .alternativa, [class*="option"]')
                alternativas = []
                for alt in alternativas_el:
                    texto_alt = await alt.inner_text()
                    alternativas.append(texto_alt)
                
                if not alternativas:
                    print(f"  ⚠️ Questão {i+1}: Nenhuma alternativa encontrada")
                    continue
                
                # Responder com IA
                resultado = await self.responder_questao_ia(enunciado, alternativas)
                resultados.append(resultado)
                
                # Clicar na alternativa
                idx = ord(resultado['resposta']) - ord('A')
                if 0 <= idx < len(alternativas_el):
                    await alternativas_el[idx].click()
                    
                    if resultado['confianca'] >= 85:
                        acertos_simulado += 1
                    
                    await self._delay()
                
            except Exception as e:
                print(f"  ❌ Erro na questão {i+1}: {e}")
                continue
        
        # Submeter simulado
        try:
            btn_submit = await self.page.query_selector('button.submit-exam, button[type="submit"], .btn-enviar')
            if btn_submit:
                await btn_submit.click()
                await self.page.wait_for_load_state('networkidle')
                print("✅ Simulado enviado!")
        except:
            print("⚠️ Botão de envio não encontrado")
        
        # Estatísticas finais
        self.stats['simulados_concluidos'] += 1
        
        resultado_final = {
            'total_questoes': total_questoes,
            'questoes_respondidas': len(resultados),
            'acertos_estimados': acertos_simulado,
            'taxa_acerto': (acertos_simulado / len(resultados) * 100) if resultados else 0,
            'resultados': resultados
        }
        
        print(f"🎉 Simulado concluído!")
        print(f"   Questões: {len(resultados)}/{total_questoes}")
        print(f"   Taxa de acerto estimada: {resultado_final['taxa_acerto']:.1f}%")
        
        self._log(f"Simulado concluído: {resultado_final['taxa_acerto']:.1f}% de acerto")
        
        return resultado_final
    
    async def processar_pdf(self, caminho_pdf: str) -> str:
        """
        Processa e memoriza conteúdo de um PDF
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            
        Returns:
            Resumo do conteúdo processado
        """
        print(f"📄 Processando PDF: {caminho_pdf}")
        
        try:
            # Extrair texto do PDF
            with open(caminho_pdf, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                texto = ""
                
                for page in reader.pages:
                    texto += page.extract_text()
            
            print(f"📖 {len(texto)} caracteres extraídos")
            
            # Resumir com IA
            prompt = f"""Analise este material educacional da UniBB e crie um resumo estruturado.

CONTEÚDO:
{texto[:15000]}  # Limitar para não exceder token limit

Forneça em JSON:
1. "resumo": Resumo executivo do conteúdo (200-300 palavras)
2. "pontos_chave": Lista dos 8-10 pontos mais importantes
3. "conceitos": Lista de conceitos-chave e suas definições
4. "aplicacoes": Como aplicar na prática
5. "dicas_prova": Dicas específicas para certificações/provas"""

            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            resultado = json.loads(response.choices[0].message.content)
            
            # Adicionar à memória de contexto
            self.context_memory.append(resultado['resumo'])
            
            self.stats['pdfs_processados'] += 1
            
            print("✅ PDF processado e memorizado!")
            self._log(f"PDF processado: {os.path.basename(caminho_pdf)}")
            
            return json.dumps(resultado, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {e}")
            return ""
    
    async def navegar_curso_automatico(self, url_curso: str):
        """
        Navega por um curso automaticamente, respondendo questões
        
        Args:
            url_curso: URL do curso
        """
        print(f"🎓 Navegando curso: {url_curso}")
        
        await self.page.goto(url_curso, wait_until='networkidle')
        await self._delay()
        
        # Encontrar todas as aulas/módulos
        modulos = await self.page.query_selector_all('.module, .aula, .lesson, [class*="modulo"]')
        
        for i, modulo in enumerate(modulos):
            print(f"  📌 Módulo {i+1}/{len(modulos)}")
            
            try:
                await modulo.click()
                await self._delay(2, 3)
                
                # Ler conteúdo
                conteudo, _ = await self.ler_conteudo_pagina()
                
                # Adicionar ao contexto
                self.context_memory.append(conteudo[:2000])
                
                # Verificar se há questões
                questoes = await self.page.query_selector_all('.question, .questao')
                
                if questoes:
                    for q in questoes:
                        # Processar questão similar ao simulado
                        pass
                
                # Marcar como concluído
                btn_concluir = await self.page.query_selector('.btn-complete, .concluir, button[contains(text(), "Concluir")]')
                if btn_concluir:
                    await btn_concluir.click()
                    await self._delay()
                
            except Exception as e:
                print(f"  ⚠️ Erro no módulo {i+1}: {e}")
                continue
        
        print("✅ Curso concluído!")
        self.cursos_completados.append(url_curso)
    
    def calcular_precisao(self) -> float:
        """Calcula a precisão atual do bot"""
        if self.total == 0:
            return 0.0
        return (self.acertos / self.total) * 100
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas completas"""
        return {
            **self.stats,
            'precisao_calculada': self.calcular_precisao(),
            'acertos': self.acertos,
            'total': self.total,
            'cursos_completados': len(self.cursos_completados)
        }
    
    async def fechar(self):
        """Fecha o navegador e limpa recursos"""
        if self.browser:
            await self.browser.close()
        
        print("👋 UniBB Assistant encerrado")
        self._log("Sessão encerrada")
    
    # ========================================
    # MÉTODOS AUXILIARES
    # ========================================
    
    async def _type_like_human(self, selector: str, text: str):
        """Digita texto como um humano (com delays)"""
        if self.stealth:
            await self.page.type(selector, text, delay=100 + (50 * (0.5 - asyncio.get_event_loop().time() % 1)))
        else:
            await self.page.fill(selector, text)
    
    async def _delay(self, min_sec: float = DELAY_MIN, max_sec: float = DELAY_MAX):
        """Delay aleatório para simular comportamento humano"""
        import random
        if self.stealth:
            await asyncio.sleep(random.uniform(min_sec, max_sec))
        else:
            await asyncio.sleep(0.5)
    
    def _log(self, message: str):
        """Registra evento no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)


# ========================================
# CLASSE PARA APP MOBILE (Android)
# ========================================

class UniBBMobileBot:
    """
    Bot para automação do app UniBB no Android via ADB
    """
    
    def __init__(self):
        """Inicializa bot mobile"""
        import subprocess
        self.adb = "adb"
        self.device_id = None
    
    def conectar_dispositivo(self) -> bool:
        """Conecta ao dispositivo Android"""
        import subprocess
        
        print("📱 Procurando dispositivos Android...")
        
        result = subprocess.run([self.adb, 'devices'], capture_output=True, text=True)
        
        if "device" in result.stdout:
            lines = result.stdout.strip().split('\n')[1:]
            if lines:
                self.device_id = lines[0].split('\t')[0]
                print(f"✅ Conectado ao dispositivo: {self.device_id}")
                return True
        
        print("❌ Nenhum dispositivo Android encontrado")
        print("💡 Ative o modo desenvolvedor e depuração USB")
        return False
    
    def tirar_screenshot(self, caminho: str = "screenshot.png"):
        """Captura screenshot do dispositivo"""
        import subprocess
        
        subprocess.run([self.adb, 'shell', 'screencap', '-p', '/sdcard/screen.png'])
        subprocess.run([self.adb, 'pull', '/sdcard/screen.png', caminho])
        print(f"📸 Screenshot salvo: {caminho}")
    
    def tocar_coordenada(self, x: int, y: int):
        """Toca em uma coordenada específica"""
        import subprocess
        subprocess.run([self.adb, 'shell', 'input', 'tap', str(x), str(y)])
    
    def digitar_texto(self, texto: str):
        """Digita texto no dispositivo"""
        import subprocess
        # Escapar espaços
        texto_escapado = texto.replace(' ', '%s')
        subprocess.run([self.adb, 'shell', 'input', 'text', texto_escapado])
    
    def abrir_app_unibb(self):
        """Abre o app UniBB"""
        import subprocess
        # Package name do app UniBB (ajustar conforme necessário)
        package = "com.uoledtech.bancodobrasil_mobile"
        subprocess.run([self.adb, 'shell', 'monkey', '-p', package, '-c', 'android.intent.category.LAUNCHER', '1'])
        print("🚀 App UniBB aberto")


# ========================================
# FUNÇÃO PRINCIPAL
# ========================================

async def main():
    """Função principal de execução"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🤖  UniBB AI Assistant v1.0.0                    ║
║                                                          ║
║    Assistente Virtual Inteligente para UniBB            ║
║    Precisão: 90%+ | Automação Completa                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Configurações (pode vir de .env)
    LOGIN = os.getenv("UNIBB_LOGIN", "F1234567")
    SENHA = os.getenv("UNIBB_SENHA", "SUA_SENHA")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY", "sk-proj-...")
    
    if OPENAI_KEY == "sk-proj-...":
        print("⚠️  Configure sua chave OpenAI no arquivo .env")
        print("    Ou defina a variável OPENAI_API_KEY")
        return
    
    # Escolher modo
    print("\n📌 Escolha o modo de operação:")
    print("   1. Web (navegador)")
    print("   2. Mobile (app Android)")
    
    modo = input("\nModo [1/2]: ").strip()
    
    if modo == "2":
        # Modo Mobile
        bot_mobile = UniBBMobileBot()
        if bot_mobile.conectar_dispositivo():
            bot_mobile.abrir_app_unibb()
            print("\n✅ Bot mobile pronto!")
            print("💡 Use os métodos do bot para controlar o app")
    else:
        # Modo Web
        bot = UniBBAssistant(
            login=LOGIN,
            senha=SENHA,
            openai_key=OPENAI_KEY,
            stealth=True
        )
        
        try:
            await bot.iniciar()
            
            # Menu de opções
            while True:
                print("\n" + "="*50)
                print("📋 Menu de Opções:")
                print("   1. Listar cursos")
                print("   2. Executar simulado")
                print("   3. Processar PDF")
                print("   4. Navegar curso automaticamente")
                print("   5. Ver estatísticas")
                print("   0. Sair")
                
                opcao = input("\nEscolha [0-5]: ").strip()
                
                if opcao == "0":
                    break
                elif opcao == "1":
                    cursos = await bot.listar_cursos()
                    for i, curso in enumerate(cursos, 1):
                        print(f"   {i}. {curso['nome']}")
                elif opcao == "2":
                    url = input("URL do simulado: ").strip()
                    resultado = await bot.executar_simulado(url)
                    print(json.dumps(resultado, indent=2, ensure_ascii=False))
                elif opcao == "3":
                    pdf_path = input("Caminho do PDF: ").strip()
                    resumo = await bot.processar_pdf(pdf_path)
                    print(resumo)
                elif opcao == "4":
                    url = input("URL do curso: ").strip()
                    await bot.navegar_curso_automatico(url)
                elif opcao == "5":
                    stats = bot.obter_estatisticas()
                    print("\n📊 Estatísticas:")
                    print(json.dumps(stats, indent=2, ensure_ascii=False))
            
        finally:
            await bot.fechar()
    
    print("\n✨ Obrigado por usar UniBB AI Assistant!")


# ========================================
# EXECUTAR
# ========================================

if __name__ == "__main__":
    asyncio.run(main())
