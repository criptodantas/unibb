"""
========================================
UniBB AI Assistant - Módulo de Execução Paralela
========================================

Adiciona capacidade de processar múltiplos cursos simultaneamente
usando múltiplos contextos do navegador (abas/páginas)

Autor: UniBB AI Team
Versão: 2.0.0 - Parallel Edition
"""

import asyncio
from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import logging

# ========================================
# ESTRUTURAS DE DADOS
# ========================================

@dataclass
class CursoPrioridade:
    """Informações de prioridade de um curso"""
    tipo: str  # 'obrigatorio', 'alto-valor', 'medio-valor', 'baixo-valor'
    valor_academico: int  # 1-5 estrelas
    obrigatorio: bool
    score: int  # Score para ordenação

@dataclass
class Curso:
    """Representa um curso na plataforma"""
    id: int
    nome: str
    url: str
    progresso: int
    total: int
    categoria: str = ""
    prioridade: CursoPrioridade = None
    
    def __post_init__(self):
        if self.prioridade is None:
            self.prioridade = calcular_prioridade_curso(self)

@dataclass
class ExecucaoTab:
    """Estado de uma aba/contexto de execução"""
    id: int
    curso: Curso
    status: str = 'running'  # running, paused, completed, error
    questoes_respondidas: int = 0
    tempo_inicio: datetime = field(default_factory=datetime.now)
    progresso: float = 0.0
    page = None
    context = None

# ========================================
# SISTEMA DE PRIORIZAÇÃO
# ========================================

# Palavras-chave para identificar prioridade
KEYWORDS_OBRIGATORIO = [
    'produtos bancários', 'matemática financeira', 'compliance',
    'ética', 'obrigatório', 'essencial', 'fundamentos'
]

KEYWORDS_ALTO_VALOR = [
    'gestão de riscos', 'investimentos', 'atendimento',
    'certificação', 'crédito', 'financiamento'
]

KEYWORDS_MEDIO_VALOR = [
    'marketing', 'tecnologia', 'inovação', 'digital'
]

def calcular_prioridade_curso(curso: Curso) -> CursoPrioridade:
    """
    Calcula a prioridade de um curso baseado em múltiplos critérios
    
    Args:
        curso: Objeto Curso
        
    Returns:
        CursoPrioridade com tipo, valor acadêmico e score
    """
    nome_lower = curso.nome.lower()
    score = 0
    tipo = 'baixo-valor'
    valor_academico = 1
    obrigatorio = False
    
    # Verificar se é obrigatório (máxima prioridade)
    if any(keyword in nome_lower for keyword in KEYWORDS_OBRIGATORIO):
        obrigatorio = True
        tipo = 'obrigatorio'
        score += 100
        valor_academico = 5
    # Alto valor acadêmico
    elif any(keyword in nome_lower for keyword in KEYWORDS_ALTO_VALOR):
        tipo = 'alto-valor'
        score += 75
        valor_academico = 4
    # Médio valor
    elif any(keyword in nome_lower for keyword in KEYWORDS_MEDIO_VALOR):
        tipo = 'medio-valor'
        score += 50
        valor_academico = 3
    # Baixo valor
    else:
        tipo = 'baixo-valor'
        score += 25
        valor_academico = 2
    
    # Bonificação por progresso baixo (priorizar não iniciados)
    progresso_percent = (curso.progresso / curso.total * 100) if curso.total > 0 else 0
    if progresso_percent < 30:
        score += 20
    elif progresso_percent < 60:
        score += 10
    
    # Bonificação por quantidade de questões restantes
    questoes_faltantes = curso.total - curso.progresso
    score += min(questoes_faltantes / 2, 50)  # Máximo 50 pontos
    
    return CursoPrioridade(
        tipo=tipo,
        valor_academico=valor_academico,
        obrigatorio=obrigatorio,
        score=int(score)
    )

# ========================================
# GERENCIADOR DE EXECUÇÃO PARALELA
# ========================================

class ParallelExecutionManager:
    """
    Gerencia a execução paralela de múltiplos cursos
    usando múltiplos contextos do navegador
    """
    
    def __init__(
        self,
        assistant,  # Instância de UniBBAssistant
        max_slots: int = 5
    ):
        """
        Inicializa o gerenciador
        
        Args:
            assistant: Instância principal do UniBBAssistant
            max_slots: Número máximo de execuções simultâneas (1-5)
        """
        self.assistant = assistant
        self.max_slots = min(max_slots, 5)  # Limitar a 5
        
        self.queue: List[Curso] = []
        self.tabs: List[ExecucaoTab] = []
        self.completed: List[Curso] = []
        self.active_slots = 0
        self.paused = False
        
        self.logger = logging.getLogger('ParallelExecution')
    
    def adicionar_cursos(self, cursos: List[Curso], priorizar: bool = True):
        """
        Adiciona cursos à fila de processamento
        
        Args:
            cursos: Lista de objetos Curso
            priorizar: Se True, ordena por prioridade antes de adicionar
        """
        if priorizar:
            # Ordenar por score de prioridade (maior = mais importante)
            cursos.sort(key=lambda c: c.prioridade.score, reverse=True)
        
        self.queue.extend(cursos)
        
        self.logger.info(f"✅ {len(cursos)} cursos adicionados à fila")
        self.logger.info(f"📊 Distribuição:")
        
        obrigatorios = sum(1 for c in cursos if c.prioridade.obrigatorio)
        alto_valor = sum(1 for c in cursos if c.prioridade.tipo == 'alto-valor')
        
        self.logger.info(f"   • Obrigatórios: {obrigatorios}")
        self.logger.info(f"   • Alto Valor: {alto_valor}")
        self.logger.info(f"   • Total: {len(cursos)}")
    
    async def iniciar_execucao(self):
        """
        Inicia a execução paralela dos cursos na fila
        """
        self.logger.info(f"🚀 Iniciando execução paralela com {self.max_slots} slots")
        self.logger.info(f"📚 {len(self.queue)} curso(s) na fila")
        
        # Criar tasks para preencher todos os slots disponíveis
        tasks = []
        while self.active_slots < self.max_slots and len(self.queue) > 0:
            curso = self.queue.pop(0)
            task = asyncio.create_task(self._processar_curso_slot(curso))
            tasks.append(task)
            await asyncio.sleep(0.5)  # Delay entre inicializações
        
        # Aguardar conclusão de todas as tasks
        if tasks:
            await asyncio.gather(*tasks)
        
        self.logger.info(f"✅ Execução paralela concluída!")
        self.logger.info(f"🎉 {len(self.completed)} curso(s) finalizados")
    
    async def _processar_curso_slot(self, curso: Curso):
        """
        Processa um curso em um slot individual
        
        Args:
            curso: Objeto Curso a ser processado
        """
        slot_id = len(self.tabs) + 1
        
        # Criar novo contexto do navegador (nova aba)
        context = await self.assistant.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.assistant.page.context.browser.user_agent
        )
        
        page = await context.new_page()
        
        # Criar tab de execução
        tab = ExecucaoTab(
            id=slot_id,
            curso=curso,
            page=page,
            context=context
        )
        
        self.tabs.append(tab)
        self.active_slots += 1
        
        self.logger.info(f"[ABA {slot_id}] 📖 Processando: {curso.nome}")
        self.logger.info(f"[ABA {slot_id}] 🎯 Prioridade: {curso.prioridade.tipo.upper()}")
        
        try:
            # Navegar para o curso
            await page.goto(curso.url, wait_until='networkidle', timeout=30000)
            await self._delay()
            
            # Processar questões do curso
            total_questoes = curso.total - curso.progresso
            
            for i in range(total_questoes):
                if self.paused or tab.status == 'paused':
                    self.logger.warning(f"[ABA {slot_id}] ⏸ Pausada")
                    break
                
                if tab.status == 'stopped':
                    break
                
                # Simular processamento de questão
                # (Em produção, fazer lógica real de extração e resposta)
                await self._delay(0.8, 1.5)
                
                tab.questoes_respondidas += 1
                tab.progresso = (tab.questoes_respondidas / total_questoes) * 100
                
                if i % 10 == 0:
                    self.logger.info(
                        f"[ABA {slot_id}] ✅ {tab.questoes_respondidas}/{total_questoes} "
                        f"({tab.progresso:.1f}%)"
                    )
            
            # Marcar como concluído
            if tab.questoes_respondidas >= total_questoes:
                tab.status = 'completed'
                self.completed.append(curso)
                
                tempo_total = (datetime.now() - tab.tempo_inicio).total_seconds()
                minutos = int(tempo_total // 60)
                segundos = int(tempo_total % 60)
                
                self.logger.info(
                    f"[ABA {slot_id}] 🎉 Concluído em {minutos}m {segundos}s!"
                )
        
        except Exception as e:
            self.logger.error(f"[ABA {slot_id}] ❌ Erro: {e}")
            tab.status = 'error'
        
        finally:
            # Fechar contexto
            await context.close()
            self.active_slots -= 1
            
            # Processar próximo da fila
            if len(self.queue) > 0 and not self.paused:
                await asyncio.sleep(1)
                proximo_curso = self.queue.pop(0)
                await self._processar_curso_slot(proximo_curso)
    
    def pausar_todas(self):
        """Pausa todas as execuções ativas"""
        self.paused = True
        for tab in self.tabs:
            if tab.status == 'running':
                tab.status = 'paused'
        self.logger.warning("⏸ Todas as execuções pausadas")
    
    def retomar_todas(self):
        """Retoma todas as execuções pausadas"""
        self.paused = False
        for tab in self.tabs:
            if tab.status == 'paused':
                tab.status = 'running'
        self.logger.info("▶ Execuções retomadas")
    
    def parar_tab(self, tab_id: int):
        """Para uma tab específica"""
        tab = next((t for t in self.tabs if t.id == tab_id), None)
        if tab:
            tab.status = 'stopped'
            self.logger.warning(f"[ABA {tab_id}] ⏹ Interrompida")
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas da execução paralela"""
        return {
            'max_slots': self.max_slots,
            'active_slots': self.active_slots,
            'queue_size': len(self.queue),
            'completed': len(self.completed),
            'total_tabs': len(self.tabs),
            'running': sum(1 for t in self.tabs if t.status == 'running'),
            'paused': sum(1 for t in self.tabs if t.status == 'paused'),
            'completed_tabs': sum(1 for t in self.tabs if t.status == 'completed'),
            'errors': sum(1 for t in self.tabs if t.status == 'error')
        }
    
    async def _delay(self, min_sec: float = 0.5, max_sec: float = 1.5):
        """Delay aleatório"""
        import random
        await asyncio.sleep(random.uniform(min_sec, max_sec))


# ========================================
# INTEGRAÇÃO COM CLASSE PRINCIPAL
# ========================================

def adicionar_capacidade_paralela(assistant_class):
    """
    Adiciona métodos de execução paralela à classe UniBBAssistant
    
    Uso:
        adicionar_capacidade_paralela(UniBBAssistant)
    """
    
    async def executar_cursos_paralelo(
        self,
        cursos: List[Dict],
        max_slots: int = 5
    ) -> Dict:
        """
        Executa múltiplos cursos em paralelo
        
        Args:
            cursos: Lista de dicionários com info dos cursos
            max_slots: Número máximo de execuções simultâneas (1-5)
            
        Returns:
            Estatísticas da execução
        """
        # Converter dicts para objetos Curso
        objetos_curso = []
        for c in cursos:
            curso = Curso(
                id=c.get('id', 0),
                nome=c.get('nome', ''),
                url=c.get('url', ''),
                progresso=c.get('progresso', 0),
                total=c.get('total', 0),
                categoria=c.get('categoria', '')
            )
            objetos_curso.append(curso)
        
        # Criar gerenciador
        manager = ParallelExecutionManager(self, max_slots=max_slots)
        
        # Adicionar cursos (com priorização automática)
        manager.adicionar_cursos(objetos_curso, priorizar=True)
        
        # Executar
        await manager.iniciar_execucao()
        
        # Retornar estatísticas
        return manager.obter_estatisticas()
    
    # Adicionar método à classe
    assistant_class.executar_cursos_paralelo = executar_cursos_paralelo
    
    print("✅ Capacidade de execução paralela adicionada ao UniBBAssistant")


# ========================================
# EXEMPLO DE USO
# ========================================

if __name__ == "__main__":
    """
    Exemplo de como usar o sistema de execução paralela
    """
    
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║   UniBB AI - Sistema de Execução Paralela           ║
    ║   Processe até 5 cursos simultaneamente!            ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Exemplo de cursos
    cursos_exemplo = [
        {
            'id': 1,
            'nome': 'Produtos Bancários Essenciais',
            'url': 'https://unibb.com.br/curso/1',
            'progresso': 20,
            'total': 100,
            'categoria': 'Produtos'
        },
        {
            'id': 2,
            'nome': 'Matemática Financeira Avançada',
            'url': 'https://unibb.com.br/curso/2',
            'progresso': 0,
            'total': 80,
            'categoria': 'Matemática'
        },
        {
            'id': 3,
            'nome': 'Gestão de Riscos e Compliance',
            'url': 'https://unibb.com.br/curso/3',
            'progresso': 45,
            'total': 120,
            'categoria': 'Compliance'
        }
    ]
    
    # Demonstração de priorização
    print("\n📊 Sistema de Priorização:\n")
    for c in cursos_exemplo:
        curso = Curso(**c)
        print(f"Curso: {curso.nome}")
        print(f"  • Tipo: {curso.prioridade.tipo}")
        print(f"  • Obrigatório: {'Sim' if curso.prioridade.obrigatorio else 'Não'}")
        print(f"  • Valor Acadêmico: {'⭐' * curso.prioridade.valor_academico}")
        print(f"  • Score: {curso.prioridade.score}")
        print()
