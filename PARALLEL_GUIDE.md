# 🎯 Guia de Uso - Execução Paralela e Priorização

## 🚀 Execução Paralela - Como Funciona

### **Conceito**
O UniBB AI Assistant v2.0 pode processar **até 5 cursos simultaneamente**, cada um em uma "aba" independente do navegador. Isso **multiplica por 5x a velocidade** de conclusão dos seus estudos!

### **Benefícios**
- ⚡ **5x mais rápido** - Conclua 5 cursos no tempo de 1
- 🎯 **Priorização inteligente** - Cursos obrigatórios processados primeiro
- 📊 **Monitoramento visual** - Veja o progresso de cada curso em tempo real
- 🔄 **Balanceamento automático** - Sistema gerencia a fila automaticamente
- ⏸️ **Controle granular** - Pause ou pare cursos individuais

---

## 📋 Como Usar - Passo a Passo

### **1. Escanear Cursos**
```
1. Abra o dashboard (index.html)
2. Vá para "Navegação Automática"
3. Clique em "Escanear Cursos Disponíveis"
4. Aguarde o sistema encontrar e priorizar todos os cursos
```

### **2. Entender as Prioridades**

Os cursos são automaticamente classificados:

| Prioridade | Cor da Borda | Estrelas | Descrição |
|------------|--------------|----------|-----------|
| 🔴 **OBRIGATÓRIO** | Vermelha | ⭐⭐⭐⭐⭐ | Cursos essenciais (Produtos Bancários, Matemática, Compliance) |
| 🟡 **ALTO VALOR** | Amarela | ⭐⭐⭐⭐ | Certificações importantes (Investimentos, Riscos) |
| 🔵 **MÉDIO VALOR** | Azul | ⭐⭐⭐ | Cursos complementares (Tecnologia, Marketing) |
| ⚪ **BAIXO VALOR** | Cinza | ⭐⭐ | Cursos opcionais |

### **3. Filtrar e Ordenar**

Use os filtros para focar no que importa:

- **📍 Todos** - Mostra todos os cursos
- **🔴 Obrigatórios** - Apenas cursos essenciais
- **⭐ Alto Valor** - Cursos de alta prioridade
- **🔄 Em Andamento** - Cursos já iniciados

**Botões de ordenação:**
- 🎯 **Filtrar por Prioridade** - Mostra apenas obrigatórios
- 📊 **Ordenar por Valor** - Ordena por estrelas

### **4. Selecionar Cursos**

```
✅ Marque os checkboxes dos cursos desejados
💡 Dica: Selecione até 20 cursos por vez
💡 Recomendação: Priorize obrigatórios e alto valor primeiro
```

### **5. Iniciar Execução Paralela**

```
1. Clique em "Iniciar Automação Paralela"
2. O sistema criará até 5 abas simultaneamente
3. Cada aba processa um curso independentemente
4. Novos cursos são iniciados automaticamente conforme abas ficam livres
```

---

## 🖥️ Monitor de Abas Paralelas

Quando a execução iniciar, você verá o **Monitor de Abas**:

### **Cada aba mostra:**

```
┌─────────────────────────────────────┐
│  [1]              [Executando]      │ ← Número e Status
├─────────────────────────────────────┤
│  Produtos Bancários e Serviços      │ ← Nome do curso
├─────────────────────────────────────┤
│   45/120          38%               │ ← Questões e Progresso
├─────────────────────────────────────┤
│  ████████░░░░░░░░░░                 │ ← Barra de progresso
├─────────────────────────────────────┤
│  ⏱️ 02:34                            │ ← Tempo decorrido
├─────────────────────────────────────┤
│  [⏸️ Pausar]  [⏹️ Parar]            │ ← Controles
└─────────────────────────────────────┘
```

### **Status das Abas:**

- 🟢 **Executando** - Processando questões
- 🟡 **Pausado** - Temporariamente pausado
- 🔵 **Concluído** - Curso finalizado
- 🔴 **Erro** - Problema detectado

---

## ⚙️ Configurações Avançadas

### **Número de Slots Paralelos**

Por padrão, o sistema usa **5 slots** (máximo). Você pode ajustar:

```python
# No arquivo parallel_execution.py
manager = ParallelExecutionManager(
    assistant,
    max_slots=5  # Altere para 1-5
)
```

**Recomendações:**
- 💻 **Computador potente**: Use 5 slots
- 🖥️ **Computador médio**: Use 3-4 slots
- 💾 **Computador fraco**: Use 2-3 slots
- 📱 **Dispositivos móveis**: Use 1-2 slots

### **Critérios de Priorização**

O sistema usa múltiplos critérios:

1. **Tipo de curso** (obrigatório > alto valor > médio > baixo)
2. **Progresso atual** (cursos não iniciados têm bonus)
3. **Questões restantes** (mais questões = maior prioridade)
4. **Categoria** (Produtos, Compliance, etc.)

**Score final:** Soma ponderada de todos os critérios

---

## 📊 Estatísticas e Performance

### **Métricas em Tempo Real:**

```
🔢 Abas Ativas: 5/5
📚 Na Fila: 8 cursos
✅ Concluídos: 3 cursos
⏱️ Tempo Médio/Curso: 4m 32s
📈 Taxa de Conclusão: 42.5 questões/min
```

### **Comparação de Performance:**

| Modo | Cursos/Hora | Economia de Tempo |
|------|-------------|-------------------|
| Sequencial (1 por vez) | ~8 cursos | Baseline |
| Paralelo 3x | ~24 cursos | 66% mais rápido |
| Paralelo 5x | ~40 cursos | 80% mais rápido |

---

## 🎯 Estratégias Recomendadas

### **Estratégia 1: Obrigatórios Primeiro**
```
1. Filtrar por "Obrigatórios"
2. Selecionar todos
3. Executar em paralelo
4. Garantir 100% dos essenciais
```

### **Estratégia 2: Alto Valor + Em Andamento**
```
1. Filtrar por "Alto Valor"
2. Adicionar cursos "Em Andamento"
3. Executar para maximizar aproveitamento
4. Foco em certificações importantes
```

### **Estratégia 3: Finalizar Tudo**
```
1. Selecionar "Todos"
2. Ordenar por progresso (mais próximos de concluir)
3. Executar em lotes de 20
4. Completar 100% da plataforma
```

---

## 🐛 Troubleshooting

### **Problema: Abas não iniciam**
**Solução:**
- Verifique se o navegador está aberto
- Confirme credenciais no .env
- Reduza o número de slots paralelos

### **Problema: Abas travam**
**Solução:**
- Clique em "Pausar" na aba específica
- Aguarde alguns segundos
- Clique em "Retomar" ou "Parar"

### **Problema: Performance baixa**
**Solução:**
- Reduza max_slots para 2-3
- Feche outros programas
- Use modo headless=True no Python

### **Problema: Alguns cursos não são priorizados**
**Solução:**
- Ajuste as palavras-chave em `parallel_execution.py`
- Adicione o nome do curso em KEYWORDS_OBRIGATORIO
- Recarregue a página

---

## 💡 Dicas Pro

1. **🎯 Priorize sempre obrigatórios** - Garanta o essencial primeiro
2. **📊 Monitore RAM/CPU** - Ajuste slots conforme recursos
3. **⏸️ Use pausas estratégicas** - Se o sistema está lento
4. **🔄 Execute em horários de baixo uso** - Menos concorrência no servidor
5. **💾 Salve progresso regularmente** - Exportar relatórios CSV
6. **🧪 Teste com 1-2 slots primeiro** - Valide funcionamento
7. **📈 Aumente gradualmente** - Vá de 2 → 3 → 4 → 5 slots
8. **🎨 Use filtros inteligentes** - Foque no que importa
9. **⭐ Revise valores acadêmicos** - Ajuste prioridades manualmente se necessário
10. **📋 Mantenha registro** - Acompanhe estatísticas para otimizar

---

## 🚀 Exemplos Práticos

### **Exemplo 1: Certificação Urgente**
```python
# Processar apenas obrigatórios com máxima prioridade
cursos_obrigatorios = [c for c in cursos if c.prioridade.obrigatorio]
await assistant.executar_cursos_paralelo(cursos_obrigatorios, max_slots=5)
```

### **Exemplo 2: Finalizar Em Andamento**
```python
# Processar cursos já iniciados
em_andamento = [c for c in cursos if 0 < c.progresso < c.total]
await assistant.executar_cursos_paralelo(em_andamento, max_slots=3)
```

### **Exemplo 3: Maratona Completa**
```python
# Processar TODOS os cursos disponíveis
todos = cursos  # Lista completa
await assistant.executar_cursos_paralelo(todos, max_slots=5)
# Com priorização automática!
```

---

## 📞 Suporte

Dúvidas sobre execução paralela?

- 📖 Leia o README.md completo
- 💬 Abra uma Issue no GitHub
- 📧 Email: unibb.ai@example.com
- 🐛 Reporte bugs com logs detalhados

---

<div align="center">

**🚀 Execute 5x mais rápido com Execução Paralela! 🚀**

*UniBB AI Assistant v2.0 - Parallel Edition*

</div>
