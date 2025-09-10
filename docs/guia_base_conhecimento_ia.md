# 🧠 Guia de Base de Conhecimento para Projetos com Assistentes de IA

**Data do documento:** Janeiro 2025  
**Objetivo:** Instruções para configuração e uso de base de conhecimento específica por projeto  
**Aplicável a:** Cursor, GitHub Copilot, Claude, ChatGPT e outros assistentes de IA  

---

## 📋 Índice

1. [Conceito e Importância](#conceito-e-importância)
2. [Estrutura da Base de Conhecimento](#estrutura-da-base-de-conhecimento)
3. [Configuração por Projeto](#configuração-por-projeto)
4. [Arquivos Obrigatórios](#arquivos-obrigatórios)
5. [Boas Práticas de Documentação](#boas-práticas-de-documentação)
6. [Instruções para Assistentes de IA](#instruções-para-assistentes-de-ia)
7. [Manutenção e Atualização](#manutenção-e-atualização)

---

## 🎯 Conceito e Importância

### Por que uma Base de Conhecimento Específica?

A base de conhecimento específica por projeto é essencial porque:

- **Contexto Específico**: Cada projeto tem suas particularidades, convenções e restrições únicos
- **Informações Atualizadas**: O pré-treinamento dos assistentes de IA pode estar desatualizado
- **Padrões do Projeto**: Manter consistência no código e abordagens
- **Regras de Negócio**: Documentar lógicas específicas do domínio
- **Restrições Técnicas**: Definir limitações e diretrizes técnicas específicas

### Benefícios

✅ **Consistência**: Código uniforme seguindo padrões estabelecidos  
✅ **Eficiência**: Redução de retrabalho e correções  
✅ **Qualidade**: Menos bugs e melhor manutenibilidade  
✅ **Conhecimento**: Preservação do conhecimento do projeto  
✅ **Onboarding**: Facilita integração de novos desenvolvedores  

---

## 📁 Estrutura da Base de Conhecimento

### Estrutura de Diretórios Recomendada

```
projeto/
├── docs/
│   ├── README_PROJETO.md              # Visão geral do projeto
│   ├── boas_praticas_cursor.md        # Práticas específicas para IA
│   ├── manual_tecnico_[framework].md  # Manual do framework principal
│   ├── arquitetura_sistema.md         # Documentação da arquitetura
│   ├── regras_negocio.md             # Lógicas específicas do domínio
│   ├── configuracao_ambiente.md      # Setup e configuração
│   └── historico_alteracoes.md       # Log de mudanças importantes
├── .cursorrules                      # Regras específicas do Cursor
├── .ai-instructions.md               # Instruções gerais para IA
└── [demais arquivos do projeto]
```

---

## ⚙️ Configuração por Projeto

### 1. Arquivo `.cursorrules` (Específico para Cursor)

Crie na raiz do projeto:

```markdown
# REGRAS ESPECÍFICAS PARA ESTE PROJETO

## Consulta Obrigatória
SEMPRE consulte prioritariamente os seguintes arquivos antes de gerar código:
- docs/boas_praticas_cursor.md
- docs/manual_tecnico_[framework].md
- docs/arquitetura_sistema.md
- docs/regras_negocio.md

## Restrições Importantes
- NUNCA criar bancos de dados, tabelas ou pastas via código
- SEMPRE emitir warnings se algo estiver ausente
- IMPLEMENTAR passo a passo aguardando feedback
- DOCUMENTAR todas as alterações em arquivo .txt

## Convenções de Código
- Incluir cabeçalho em novos arquivos Python:
  # <nome do programa>
  # <função/funcionalidade>  
  # <data e hora da atualização>

## Debug
- Usar comentário "# Debug" para prints temporários
- Preferir saída no terminal da IDE, não via Streamlit

## Framework Específico
[Incluir regras específicas do framework usado no projeto]
```

### 2. Arquivo `.ai-instructions.md` (Universal)

```markdown
# INSTRUÇÕES PARA ASSISTENTES DE IA

## 🚨 IMPORTANTE: CONSULTA OBRIGATÓRIA
Antes de gerar qualquer código, SEMPRE consulte:
1. `docs/boas_praticas_cursor.md` - Práticas de codificação específicas
2. `docs/manual_tecnico_[framework].md` - Manual técnico atualizado
3. `docs/arquitetura_sistema.md` - Arquitetura e padrões do sistema
4. `docs/regras_negocio.md` - Lógicas específicas do domínio

## 🎯 Metodologia de Trabalho
1. **Análise**: Compreenda o contexto consultando a documentação
2. **Planejamento**: Proponha solução seguindo os padrões estabelecidos
3. **Implementação**: Execute passo a passo aguardando feedback
4. **Documentação**: Registre alterações conforme especificado

## 🚫 RESTRIÇÕES ABSOLUTAS
- Não criar estruturas de banco de dados via código
- Não criar pastas ou diretórios automaticamente
- Não ignorar as convenções estabelecidas
- Não prosseguir sem feedback em mudanças complexas

## 📝 DOCUMENTAÇÃO OBRIGATÓRIA
Para cada alteração significativa, criar arquivo `.txt` com:
- Descrição da alteração
- Programa afetado
- Linha modificada
- Justificativa técnica
```

---

## 📚 Arquivos Obrigatórios

### 1. `docs/README_PROJETO.md`

```markdown
# [Nome do Projeto]

## Visão Geral
[Descrição breve do projeto]

## Tecnologias Principais
- Framework: [ex: Streamlit]
- Linguagem: [ex: Python 3.9+]
- Banco de Dados: [ex: SQLite]
- Deploy: [ex: Render.com]

## Arquitetura Resumida
[Descrição da estrutura do sistema]

## Particularidades do Projeto
[Lógicas específicas, ex: sistema de células estilo Excel]

## Links Importantes
- Manual Técnico: [docs/manual_tecnico_streamlit.md]
- Boas Práticas: [docs/boas_praticas_cursor.md]
- Arquitetura: [docs/arquitetura_sistema.md]
```

### 2. `docs/boas_praticas_cursor.md`

Use como base o arquivo existente, adaptando para o projeto específico.

### 3. `docs/manual_tecnico_[framework].md`

Use como base o manual do Streamlit existente, atualizando conforme necessário.

### 4. `docs/arquitetura_sistema.md`

```markdown
# Arquitetura do Sistema

## Estrutura de Diretórios
[Explicar organização dos arquivos]

## Fluxo de Dados
[Explicar como os dados fluem no sistema]

## Padrões de Código
[Convenções específicas adotadas]

## Integrações
[APIs, bancos de dados, serviços externos]

## Deployment
[Processo de deploy e configurações]
```

### 5. `docs/regras_negocio.md`

```markdown
# Regras de Negócio

## Lógicas Específicas
[Documentar algoritmos e regras particulares do projeto]

## Validações
[Regras de validação de dados]

## Fluxos de Processo
[Processos específicos do domínio]

## Exceções e Casos Especiais
[Situações especiais que o sistema deve tratar]
```

---

## 📝 Boas Práticas de Documentação

### Estrutura de Documentos

1. **Cabeçalho Padrão**:
```markdown
# Título do Documento
**Data:** [data]
**Versão:** [versão]
**Responsável:** [nome]
**Última Atualização:** [data]
```

2. **Seções Obrigatórias**:
   - Objetivo/Propósito
   - Pré-requisitos (se aplicável)
   - Instruções detalhadas
   - Exemplos práticos
   - Observações importantes
   - Links relacionados

3. **Formatação**:
   - Use emojis para facilitar identificação (📝, ⚠️, ✅, ❌)
   - Destaque informações críticas
   - Inclua exemplos de código
   - Use listas numeradas para sequências

### Manutenção de Versionamento

```markdown
## Histórico de Versões
| Versão | Data | Alteração | Responsável |
|--------|------|-----------|-------------|
| 1.0 | 01/01/2025 | Criação inicial | [nome] |
| 1.1 | 15/01/2025 | Adição de seção X | [nome] |
```

---

## 🤖 Instruções para Assistentes de IA

### Para Desenvolvedores que Usam IA

Ao iniciar trabalho em um projeto, sempre instrua o assistente:

```
"Este projeto possui uma base de conhecimento específica na pasta /docs. 
Antes de gerar qualquer código, consulte obrigatoriamente:
1. docs/boas_praticas_cursor.md
2. docs/manual_tecnico_[framework].md  
3. docs/arquitetura_sistema.md
4. docs/regras_negocio.md

Siga rigorosamente as diretrizes estabelecidas e aguarde meu feedback 
antes de prosseguir com implementações complexas."
```

### Comandos Úteis para IA

```
# Consulta inicial
"Analise a base de conhecimento do projeto em /docs e me dê um resumo das principais diretrizes."

# Verificação de conformidade
"Verifique se o código proposto está em conformidade com as boas práticas documentadas."

# Atualização de documentação
"Atualize a documentação conforme as alterações realizadas."
```

---

## 🔄 Manutenção e Atualização

### Frequência de Revisão

- **Semanal**: Verificar se novas práticas precisam ser documentadas
- **Mensal**: Revisar e atualizar documentação técnica
- **Por Release**: Atualizar arquitetura e regras de negócio
- **Quando Necessário**: Atualizações emergenciais

### Checklist de Manutenção

✅ Documentação está atualizada?  
✅ Exemplos de código funcionam?  
✅ Links internos estão corretos?  
✅ Novas restrições foram documentadas?  
✅ Alterações foram versionadas?  

### Responsabilidades

- **Tech Lead**: Manter arquitetura e padrões gerais
- **Desenvolvedores**: Atualizar documentação de features específicas
- **Product Owner**: Validar regras de negócio
- **DevOps**: Manter documentação de deployment

---

## 🎯 Implementação Prática

### Passo a Passo para Novo Projeto

1. **Criar estrutura de diretórios**:
```bash
mkdir docs
touch docs/README_PROJETO.md
touch docs/boas_praticas_cursor.md
touch docs/manual_tecnico_[framework].md
touch docs/arquitetura_sistema.md
touch docs/regras_negocio.md
touch .cursorrules
touch .ai-instructions.md
```

2. **Preencher templates básicos** usando este guia

3. **Configurar IDE** para reconhecer os arquivos

4. **Treinar equipe** sobre o uso da base de conhecimento

5. **Estabelecer rotina** de manutenção

---

## 🚨 Alertas Importantes

⚠️ **A base de conhecimento é inútil se não for consultada!**  
⚠️ **Mantenha sempre atualizada para ser efetiva**  
⚠️ **Documente exceções e casos especiais**  
⚠️ **Não assuma que a IA conhece particularidades do seu projeto**  

---

## 📞 Suporte e Dúvidas

Para dúvidas sobre implementação da base de conhecimento:
1. Consulte este guia primeiro
2. Verifique documentação existente do projeto
3. Documente novos padrões descobertos
4. Atualize a base de conhecimento

---

**Lembre-se**: Uma base de conhecimento bem estruturada é um investimento que paga dividendos em produtividade, qualidade e consistência do código ao longo de todo o ciclo de vida do projeto. 