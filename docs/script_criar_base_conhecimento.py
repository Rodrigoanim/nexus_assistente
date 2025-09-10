# Script para Criação de Base de Conhecimento para IA
# Automatiza a criação da estrutura de documentação
# Setembro 2025

import os
import sys
from pathlib import Path

def criar_estrutura_base_conhecimento(nome_projeto, framework="streamlit"):
    """
    Cria a estrutura completa de base de conhecimento para um projeto
    
    Args:
        nome_projeto (str): Nome do projeto
        framework (str): Framework principal (streamlit, django, flask, etc.)
    """
    
    print(f"🚀 Criando base de conhecimento para: {nome_projeto}")
    print(f"📦 Framework: {framework}")
    
    # Criar diretório docs se não existir
    docs_path = Path("docs")
    docs_path.mkdir(exist_ok=True)
    
    # 1. Criar .cursorrules
    print("📝 Criando .cursorrules...")
    criar_cursorrules(nome_projeto, framework)
    
    # 2. Criar .ai-instructions.md
    print("📝 Criando .ai-instructions.md...")
    criar_ai_instructions(nome_projeto, framework)
    
    # 3. Criar README_PROJETO.md
    print("📝 Criando docs/README_PROJETO.md...")
    criar_readme_projeto(nome_projeto, framework)
    
    # 4. Criar arquitetura_sistema.md
    print("📝 Criando docs/arquitetura_sistema.md...")
    criar_arquitetura_sistema(nome_projeto)
    
    # 5. Criar regras_negocio.md
    print("📝 Criando docs/regras_negocio.md...")
    criar_regras_negocio(nome_projeto)
    
    # 6. Criar configuracao_ambiente.md
    print("📝 Criando docs/configuracao_ambiente.md...")
    criar_configuracao_ambiente(nome_projeto, framework)
    
    print("\n✅ Base de conhecimento criada com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Preencher os templates com informações específicas do projeto")
    print("2. Configurar a IDE para reconhecer os arquivos")
    print("3. Treinar a equipe sobre o uso da base de conhecimento")
    print("4. Estabelecer rotina de manutenção")

def criar_cursorrules(nome_projeto, framework):
    content = f"""# REGRAS ESPECÍFICAS PARA PROJETO {nome_projeto.upper()} - {framework.upper()}

## 🚨 CONSULTA OBRIGATÓRIA
SEMPRE consulte prioritariamente os seguintes arquivos antes de gerar código:
- docs/boas_praticas_cursor.md
- docs/Streamlit_Manual_Gemini.md
- docs/guia_base_conhecimento_ia.md

## 🎯 CONTEXTO DO PROJETO
- Sistema de avaliação DISC com lógica de planilha Excel
- Framework: Streamlit + Python + SQLite
- Deploy: Render.com (disco persistente SSD)
- Estrutura: Células com formato letra+número (B9, C789, DC9876)

## 🚫 RESTRIÇÕES ABSOLUTAS
- NUNCA criar bancos de dados, tabelas ou pastas via código
- SEMPRE emitir warnings se algo estiver ausente
- IMPLEMENTAR passo a passo aguardando feedback do usuário
- DOCUMENTAR todas as alterações em arquivo .txt
- NÃO usar funcionalidades obsoletas do Streamlit

## 📋 CONVENÇÕES DE CÓDIGO OBRIGATÓRIAS
### Cabeçalho em novos arquivos Python:
```python
# <nome do programa>
# <função/funcionalidade>
# <data e hora da atualização>
```

### Debug:
- Usar comentário "# Debug" para prints temporários
- Preferir saída no terminal da IDE Cursor, não via Streamlit

### Streamlit Atualizado:
- ✅ Usar: st.query_params (NÃO st.experimental_get_query_params)
- ✅ Usar: use_container_width (NÃO use_column_width)
- ✅ Evitar tags <h1> a <h6>, preferir <p> com styling
- ✅ Remover comentários # de queries SQL
- ✅ Usar @st.cache_data e @st.cache_resource conforme apropriado

## 🗂️ ESTRUTURA ESPECÍFICA DO PROJETO
- main.py: Arquivo principal da aplicação
- paginas/: Módulos das diferentes páginas
- data/: Bancos de dados SQLite (não modificar via código)
- Conteudo/: Arquivos markdown com conteúdo DISC
- config.py: Configurações do sistema

## 🔄 METODOLOGIA DE TRABALHO
1. **Análise**: Compreenda o contexto consultando a documentação
2. **Proposta**: Apresente solução seguindo padrões estabelecidos
3. **Implementação**: Execute passo a passo aguardando feedback
4. **Teste**: Verifique funcionamento sem quebrar o app
5. **Documentação**: Registre alterações conforme especificado

## 💾 LÓGICA DE SISTEMA (Excel-like)
- Sistema simula planilha Excel com células (letra + número)
- Quando type="formulaH", usar fórmula da coluna math_element
- Manter consistência com essa lógica em todas as implementações

## 📝 DOCUMENTAÇÃO OBRIGATÓRIA
Para cada alteração significativa, criar arquivo .txt com:
- Descrição da alteração
- Arquivo/programa afetado
- Linha específica modificada
- Justificativa técnica
- Impacto no sistema

## ⚠️ AVISOS IMPORTANTES
- Aguarde SEMPRE feedback antes de seguir para próximo passo
- Só inicie após receber instrução clara do objetivo
- Modificações no banco serão feitas manualmente pelo usuário
- Implemente com cuidado para não quebrar funcionalidades existentes
"""
    
    with open(".cursorrules", "w", encoding="utf-8") as f:
        f.write(content)

def criar_ai_instructions(nome_projeto, framework):
    content = f"""# INSTRUÇÕES PARA ASSISTENTES DE IA - PROJETO {nome_projeto.upper()}

## 🚨 IMPORTANTE: CONSULTA OBRIGATÓRIA
Antes de gerar qualquer código, SEMPRE consulte:
1. `docs/boas_praticas_cursor.md` - Práticas de codificação específicas
2. `docs/Streamlit_Manual_Gemini.md` - Manual técnico atualizado
3. `docs/guia_base_conhecimento_ia.md` - Guia de base de conhecimento
4. `.cursorrules` - Regras específicas do projeto

## 🎯 CONTEXTO DO PROJETO
- **Nome**: {nome_projeto}
- **Stack**: Streamlit + Python + SQLite
- **Deploy**: Render.com (disco persistente SSD)
- **Característica Única**: Sistema de avaliação DISC com lógica de planilha Excel

## 🔍 METODOLOGIA DE TRABALHO
1. **Análise**: Compreenda o contexto consultando a documentação obrigatória
2. **Planejamento**: Proponha solução seguindo os padrões estabelecidos
3. **Implementação**: Execute passo a passo aguardando feedback do usuário
4. **Teste**: Verifique funcionamento sem quebrar aplicação existente
5. **Documentação**: Registre alterações conforme especificado

## 🚫 RESTRIÇÕES ABSOLUTAS
- **NUNCA** criar estruturas de banco de dados via código
- **NUNCA** criar pastas ou diretórios automaticamente
- **NUNCA** ignorar as convenções estabelecidas na documentação
- **NUNCA** prosseguir sem feedback em mudanças complexas

## ✅ DIRETRIZES OBRIGATÓRIAS

### Código Python:
```python
# Cabeçalho obrigatório em novos arquivos:
# <nome do programa>
# <função/funcionalidade>
# <data e hora da atualização>
```

### Debug:
- Usar comentário `# Debug` para prints temporários
- Preferir saída no terminal da IDE Cursor

### Streamlit Específico:
- Usar `st.query_params` (NÃO `st.experimental_get_query_params`)
- Usar `use_container_width` (NÃO `use_column_width`)
- Evitar tags `<h1>` a `<h6>`, preferir `<p>` com styling
- Remover comentários `#` de queries SQL
- Usar `@st.cache_data` e `@st.cache_resource` conforme apropriado

## 📁 ESTRUTURA DO PROJETO
```
{nome_projeto}/
├── main.py                  # Aplicação principal
├── paginas/                 # Módulos das diferentes páginas
├── data/                    # Bancos de dados SQLite (NÃO MODIFICAR)
├── Conteudo/                # Arquivos markdown com conteúdo 7 Armadilhas do Eu Empresário
├── docs/                    # Base de conhecimento
├── config.py                # Configurações do sistema
└── requirements.txt         # Dependências
```

## 💾 LÓGICA DE SISTEMA (Excel-like)
- Sistema simula planilha Excel com células (letra + número)
- Quando `type="formulaH"`, usar fórmula da coluna `math_element`
- Manter consistência com essa lógica em todas as implementações

## 📝 DOCUMENTAÇÃO OBRIGATÓRIA
Para **TODA** alteração significativa, criar arquivo `.txt` contendo:
- **Descrição**: O que foi alterado
- **Arquivo**: Programa/módulo afetado
- **Linha**: Localização específica da mudança
- **Justificativa**: Por que a alteração foi necessária
- **Impacto**: Como afeta o sistema

---

**LEMBRE-SE**: Esta base de conhecimento existe para garantir qualidade, consistência e eficiência. Use-a como sua referência principal antes de qualquer implementação.
"""
    
    with open(".ai-instructions.md", "w", encoding="utf-8") as f:
        f.write(content)

def criar_readme_projeto(nome_projeto, framework):
    content = f"""# {nome_projeto}

**Data:** Janeiro 2025  
**Versão:** 1.0  
**Responsável:** Equipe de Desenvolvimento  

---

## 🎯 Visão Geral

Sistema de avaliação DISC adaptado para o assessment "7 Armadilhas do Eu Empresário". 
Desenvolvido pela Erika Rossi - EAR Consultoria, este sistema utiliza a lógica de planilha Excel 
para processar avaliações comportamentais e gerar análises personalizadas.

## 💻 Tecnologias Principais

- **Framework**: Streamlit
- **Linguagem**: Python 3.9+
- **Banco de Dados**: SQLite
- **Deploy**: Render.com (disco persistente SSD)
- **IDE Recomendada**: Cursor

## 🏗️ Arquitetura Resumida

### Estrutura de Diretórios
```
{nome_projeto}/
├── main.py                  # Aplicação principal Streamlit
├── paginas/                 # Módulos das diferentes páginas
├── data/                    # Bancos de dados SQLite
├── Conteudo/                # Arquivos markdown com conteúdo 7 Armadilhas do Eu Empresário
├── docs/                    # Base de conhecimento
├── config.py                # Configurações do sistema
└── requirements.txt         # Dependências Python
```

### Fluxo Principal
1. **Login**: Autenticação de usuários
2. **Avaliação**: Preenchimento de formulários DISC
3. **Processamento**: Cálculo de resultados com lógica Excel-like
4. **Análise**: Geração de relatórios e gráficos
5. **Administração**: Gestão de usuários e dados

## 🔗 Links Importantes da Base de Conhecimento

- **Manual Técnico**: [docs/Streamlit_Manual_Gemini.md](Streamlit_Manual_Gemini.md)
- **Boas Práticas**: [docs/boas_praticas_cursor.md](boas_praticas_cursor.md)
- **Guia Base Conhecimento**: [docs/guia_base_conhecimento_ia.md](guia_base_conhecimento_ia.md)
- **Regras do Projeto**: [docs/projeto - Regras para a Ferramenta.md](projeto%20-%20Regras%20para%20a%20Ferramenta.md)

## 🚨 Restrições Importantes

### Para Desenvolvimento com IA
- **SEMPRE** consultar base de conhecimento antes de gerar código
- **NUNCA** criar/modificar estruturas de banco automaticamente
- **SEMPRE** implementar passo a passo com feedback
- **SEMPRE** documentar alterações em arquivo .txt

### Lógica do Sistema
- Sistema simula planilha Excel com células (letra + número)
- Quando `type="formulaH"`, usar fórmula da coluna `math_element`
- Manter consistência com essa lógica em todas as implementações

---

**⚠️ IMPORTANTE**: Este projeto possui uma base de conhecimento específica que DEVE ser consultada por qualquer assistente de IA antes da geração de código.
"""
    
    with open("docs/README_PROJETO.md", "w", encoding="utf-8") as f:
        f.write(content)

def criar_arquitetura_sistema(nome_projeto):
    content = f"""# Arquitetura do Sistema - {nome_projeto}

**Data:** Janeiro 2025  
**Versão:** 1.0  

---

## 📁 Estrutura de Diretórios

```
{nome_projeto}/
├── main.py                  # Aplicação principal Streamlit
├── config.py                # Configurações do sistema
├── create_forms.py          # Script para criação de formulários
├── paginas/                 # Módulos das diferentes páginas
│   ├── __init__.py
│   ├── form_model.py        # Processamento de formulários
│   ├── resultados.py        # Exibição de resultados
│   ├── resultados_adm.py    # Módulo administrativo
│   ├── monitor.py           # Monitoramento de uso
│   ├── crude.py             # CRUD de dados
│   └── diagnostico.py       # Diagnósticos do sistema
├── data/                    # Bancos de dados SQLite
│   └── calcrh.db           # Banco principal
├── Conteudo/                # Arquivos markdown com conteúdo 7 Armadilhas do Eu Empresário
│   ├── 1_BaixoRisco.md      # Relatório para pontuação 0-7
│   ├── 2_Atencao.md         # Relatório para pontuação 8-14
│   ├── 3_AltoRisco.md       # Relatório para pontuação 15-21
│   ├── 4_RiscoCritico.md    # Relatório para pontuação 22-28
│   └── Prompt NotebookLM.txt # Prompt para IA
├── docs/                    # Base de conhecimento
│   ├── boas_praticas_cursor.md
│   ├── Streamlit_Manual_Gemini.md
│   ├── guia_base_conhecimento_ia.md
│   └── [outros documentos]
├── manutencao/              # Arquivos de documentação de alterações
├── env/                     # Ambiente virtual Python
└── requirements.txt         # Dependências Python
```

## 🔄 Fluxo de Dados

### 1. Autenticação
- Usuário faz login via `main.py`
- Verificação de credenciais na tabela `usuarios`
- Criação de sessão com `st.session_state`

### 2. Avaliação
- Usuário acessa formulários via `paginas/form_model.py`
- Dados são salvos na tabela `forms_tab`
- Processamento com lógica Excel-like (células letra+número)

### 3. Processamento
- Cálculo de fórmulas baseado em `math_element`
- Atualização de valores dependentes
- Geração de resultados na tabela `forms_resultados`

### 4. Análise
- Exibição de resultados via `paginas/resultados.py`
- Cálculo de vulnerabilidade (M3000 + N3000)
- Classificação em 4 faixas de risco
- Exibição automática de relatórios markdown
- Análise de vulnerabilidade 7 Armadilhas do Eu Empresário

## 📋 Padrões de Código

### Convenções de Nomenclatura
- Arquivos Python: snake_case
- Funções: snake_case
- Variáveis: snake_case
- Constantes: UPPER_CASE

### Estrutura de Arquivos
- Cabeçalho obrigatório em todos os arquivos Python
- Separação clara de responsabilidades por módulo
- Documentação inline para funções complexas

### Gerenciamento de Estado
- `st.session_state` para dados de sessão
- Cache com `@st.cache_data` e `@st.cache_resource`
- Controle de rerun com debounce

## 🔗 Integrações

### Banco de Dados
- **SQLite**: Banco principal (`calcrh.db`)
- **Tabelas principais**:

#### 1. `usuarios` - Dados dos Usuários
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    empresa TEXT
);
```

#### 2. `forms_tab` - Formulários e Cálculos 7 Armadilhas
```sql
CREATE TABLE forms_tab (
    ID_element INTEGER PRIMARY KEY AUTOINCREMENT,
    name_element TEXT NOT NULL,
    type_element TEXT NOT NULL,
    math_element TEXT,
    msg_element TEXT,
    value_element REAL,
    select_element TEXT,
    str_element TEXT,
    e_col INTEGER,
    e_row INTEGER,
    user_id INTEGER,
    section TEXT,
    col_len TEXT
);
```

#### 3. `forms_resultados` - Resultados Processados
```sql
CREATE TABLE forms_resultados (
    ID_element INTEGER PRIMARY KEY AUTOINCREMENT,
    name_element TEXT NOT NULL,
    type_element TEXT NOT NULL,
    math_element TEXT,
    msg_element TEXT,
    value_element REAL,
    select_element TEXT,
    str_element TEXT,
    e_col INTEGER,
    e_row INTEGER,
    user_id INTEGER,
    section TEXT
);
```

#### 4. `forms_insumos` - Dados de Entrada
```sql
CREATE TABLE forms_insumos (
    ID_element INTEGER PRIMARY KEY AUTOINCREMENT,
    name_element TEXT NOT NULL,
    type_element TEXT NOT NULL,
    math_element TEXT,
    msg_element TEXT,
    value_element REAL,
    select_element TEXT,
    str_element TEXT,
    e_col INTEGER,
    e_row INTEGER,
    user_id INTEGER,
    section TEXT
);
```

#### 5. `forms_result_sea` - Resultados SEA (Sistema Específico)
```sql
CREATE TABLE forms_result_sea (
    ID_element INTEGER PRIMARY KEY AUTOINCREMENT,
    name_element TEXT NOT NULL,
    type_element TEXT NOT NULL,
    math_element TEXT,
    msg_element TEXT,
    value_element REAL,
    select_element TEXT,
    str_element TEXT,
    e_col INTEGER,
    e_row INTEGER,
    user_id INTEGER,
    section TEXT
);
```

#### 6. `log_acessos` - Log de Acessos do Sistema
```sql
CREATE TABLE log_acessos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    data_acesso DATE NOT NULL,
    hora_acesso TIME NOT NULL,
    programa TEXT NOT NULL,
    acao TEXT NOT NULL
);
```

### Serviços
- **Render.com**: Deploy em produção
- **Streamlit**: Framework web
- **SQLite**: Banco de dados

## 🚀 Deployment

### Ambiente de Desenvolvimento
```bash
# Ativar ambiente virtual
.\\env\\Scripts\\Activate

# Executar aplicação
streamlit run main.py
```

### Ambiente de Produção
- Deploy automático via GitHub no Render.com
- Disco persistente SSD para dados
- Configuração via variáveis de ambiente

## 🔧 Configurações

### Variáveis de Ambiente
- `RENDER`: Detecta ambiente de produção
- Configurações de banco via `config.py`

### Dependências Principais
- `streamlit`: Framework web
- `sqlite3`: Banco de dados
- `pandas`: Manipulação de dados
- `plotly`: Gráficos interativos

---

## 📝 Notas de Implementação

### Lógica Excel-like
- Sistema simula planilha Excel com células (letra + número)
- Quando `type="formulaH"`, usar fórmula da coluna `math_element`
- Manter consistência com essa lógica em todas as implementações

### Restrições Importantes
- NUNCA criar bancos de dados, tabelas ou pastas via código
- SEMPRE emitir warnings se algo estiver ausente
- IMPLEMENTAR passo a passo aguardando feedback do usuário
- DOCUMENTAR todas as alterações em arquivo .txt
"""
    
    with open("docs/arquitetura_sistema.md", "w", encoding="utf-8") as f:
        f.write(content)

def criar_regras_negocio(nome_projeto):
    content = f"""# Regras de Negócio - {nome_projeto}

**Data:** Janeiro 2025  
**Versão:** 1.0  

---

## 🎯 Lógicas Específicas

### Sistema de Células Excel-like
- **Descrição**: Sistema simula planilha Excel com células identificadas por letra+número (ex: B9, C789, DC9876)
- **Implementação**: Células são referenciadas na coluna `name_element` e processadas conforme tipo
- **Validações**: Verificar se referências de células existem antes de processar fórmulas

### Processamento de Fórmulas
- **Descrição**: Quando `type_element="formulaH"`, usar fórmula da coluna `math_element`
- **Implementação**: Função `calculate_formula()` processa referências e executa cálculos
- **Validações**: Divisão por zero retorna 0.0, referências inexistentes são tratadas como 0

### Sistema de Avaliação 7 Armadilhas do Eu Empresário
- **Descrição**: Assessment com 7 perguntas diretas e 7 invertidas (14 total)
- **Implementação**: 
  - **Perguntas Diretas**: Pontuação de Risco = Pontuação (0-3)
  - **Perguntas Invertidas**: Pontuação de Risco = 3 - Pontuação (0-3)
- **Armazenamento no Banco**:
  - **M3000**: Soma das 7 perguntas diretas (str_element = 'M3000')
  - **N3000**: Soma das 7 perguntas invertidas (str_element = 'N3000')
- **Cálculo Final**: Vulnerabilidade Total = M3000 + N3000 (0-28 pontos)
- **Faixas de Vulnerabilidade**:
  - **0-7 pontos**: Baixo Risco (Verde #2E8B57) → 1_BaixoRisco.md
  - **8-14 pontos**: Atenção (Amarelo #DAA520) → 2_Atencao.md
  - **15-21 pontos**: Alto Risco (Laranja #FF8C00) → 3_AltoRisco.md
  - **22-28 pontos**: Risco Crítico (Vermelho #B22222) → 4_RiscoCritico.md
- **Validações**: Valores devem estar entre 0 e 3

### Cálculo de Vulnerabilidade
- **Descrição**: Soma de M3000 + N3000 (máximo 28 pontos)
- **Implementação**: 
  - Busca M3000 na tabela forms_resultados (str_element = 'M3000')
  - Busca N3000 na tabela forms_resultados (str_element = 'N3000')
  - Soma: Vulnerabilidade Total = M3000 + N3000
- **Validações**: Resultado entre 0 e 28 pontos
- **Classificação Automática**: Baseada na pontuação total

## ✅ Validações

### Validação de Entrada
- Pontuações devem estar entre 0 e 3
- Usuário deve estar autenticado
- Dados obrigatórios não podem estar vazios

### Validação de Processo
- Referências de células devem existir
- Fórmulas devem ser válidas
- Cálculos não podem resultar em divisão por zero

### Validação de Saída
- Resultados devem estar nas faixas definidas
- Gráficos devem ter dados válidos
- Relatórios devem ser gerados corretamente

## 🔄 Fluxos de Processo

### Processo Principal de Avaliação 7 Armadilhas
1. **Login**: Usuário autentica no sistema
2. **Preenchimento Direto**: Responde 7 perguntas diretas (seção "fdireta")
3. **Preenchimento Invertido**: Responde 7 perguntas invertidas (seção "finvertida")
4. **Cálculo**: Sistema calcula Pontuações de Risco para cada pergunta
5. **Armazenamento**: Salva M3000 e N3000 na tabela forms_resultados
6. **Análise**: Sistema busca M3000 e N3000 para calcular vulnerabilidade total
7. **Classificação**: Define faixa de risco baseada na pontuação total
8. **Interface**: Exibe métricas visuais e classificação por cores
9. **Relatório**: Carrega e exibe conteúdo do arquivo markdown correspondente:
   - 0-7 pontos → 1_BaixoRisco.md (Verde)
   - 8-14 pontos → 2_Atencao.md (Amarelo)
   - 15-21 pontos → 3_AltoRisco.md (Laranja)
   - 22-28 pontos → 4_RiscoCritico.md (Vermelho)

### Função de Análise de Vulnerabilidade
- **Arquivo**: `paginas/resultados.py`
- **Função**: `analisar_vulnerabilidade_7armadilhas_streamlit()`
- **Funcionalidades**:
  - Busca M3000 e N3000 na tabela forms_resultados
  - Calcula vulnerabilidade total (M3000 + N3000)
  - Classifica em 4 faixas de risco com cores
  - Exibe métricas visuais (3 colunas)
  - Carrega arquivo markdown correspondente
  - Tratamento de erros robusto

### Processos Secundários
- Cópia de dados do template (user_id=0) para novos usuários
- Atualização de elementos dependentes via `condicaoH`
- Cache de resultados para performance
- Leitura automática de arquivos markdown da pasta Conteudo/
- Monitoramento de acesso e uso

## ⚠️ Exceções e Casos Especiais

### Usuário sem Dados de Vulnerabilidade
- **Situação**: M3000 ou N3000 não encontrados na tabela forms_resultados
- **Tratamento**: Exibir mensagem "Análise de Vulnerabilidade não disponível"
- **Ação**: Orientar usuário a completar avaliação

### Arquivo Markdown Não Encontrado
- **Situação**: Arquivo de relatório não existe na pasta Conteudo/
- **Tratamento**: Exibir warning e informações sobre arquivo ausente
- **Ação**: Verificar se arquivo existe na pasta Conteudo/

### Usuário sem Dados
- **Situação**: Novo usuário sem registros na tabela
- **Tratamento**: Copiar dados do template (user_id=0) automaticamente

### Fórmula com Referência Inexistente
- **Situação**: Célula referenciada não existe
- **Tratamento**: Usar valor 0.0 para a referência

### Erro na Leitura de Arquivo
- **Situação**: Erro ao ler arquivo markdown
- **Tratamento**: Exibir erro específico com traceback
- **Ação**: Verificar permissões e encoding do arquivo

### Divisão por Zero
- **Situação**: Fórmula tenta dividir por zero
- **Tratamento**: Retornar 0.0 como resultado

## 📊 Estrutura de Dados da Vulnerabilidade

### Campos Específicos na Tabela forms_resultados
- **M3000**: Soma das 7 perguntas diretas
  - Campo: `str_element = 'M3000'`
  - Valor: `value_element` (0-21 pontos)
- **N3000**: Soma das 7 perguntas invertidas
  - Campo: `str_element = 'N3000'`
  - Valor: `value_element` (0-21 pontos)

### Queries SQL Utilizadas
```sql
-- Buscar pontuação das perguntas diretas
SELECT value_element FROM forms_resultados 
WHERE user_id = ? AND str_element = 'M3000'

-- Buscar pontuação das perguntas invertidas
SELECT value_element FROM forms_resultados 
WHERE user_id = ? AND str_element = 'N3000'
```

### Cálculo da Vulnerabilidade Total
- **Fórmula**: `Vulnerabilidade Total = M3000 + N3000`
- **Escala**: 0 a 28 pontos
- **Classificação**: Baseada na pontuação total

### Dados Corrompidos
- **Situação**: Valores inválidos no banco
- **Tratamento**: Validar e corrigir ou usar valores padrão

## 📊 Algoritmos Específicos

### Cálculo de Fórmulas
```python
def calculate_formula(formula, values, cursor):
    # Processa referências de células
    # Substitui por valores reais
    # Executa cálculo seguro
    # Retorna resultado formatado
```

### Sistema de Cache
```python
@st.cache_data(ttl=300)
def _calculate_formula_cached(formula_str, values_dict, user_id):
    # Cache de 5 minutos para fórmulas
    # Evita recálculos desnecessários
```

### Controle de Rerun
```python
def _reset_rerun_locks(section):
    # Reset de flags de controle
    # Evita reruns em cascata
    # Melhora performance
```

---

## 📋 Checklist de Implementação

- [x] Sistema de células Excel-like implementado
- [x] Processamento de fórmulas funcionando
- [x] Validações de entrada implementadas
- [x] Cálculo de vulnerabilidade funcionando
- [x] Classificação de níveis de risco implementada
- [x] Sistema de cache otimizado
- [x] Controle de rerun implementado
- [x] Tratamento de exceções coberto
"""
    
    with open("docs/regras_negocio.md", "w", encoding="utf-8") as f:
        f.write(content)

def criar_configuracao_ambiente(nome_projeto, framework):
    content = f"""# Configuração de Ambiente - {nome_projeto}

**Data:** Janeiro 2025  
**Versão:** 1.0  

---

## 🔧 Pré-requisitos

### Software Necessário
- Python 3.9+
- Git (para controle de versão)
- Navegador web moderno

### IDE Recomendada
- **Cursor** (com base de conhecimento configurada)
- Extensões recomendadas: Python, Streamlit

## 📦 Instalação

### 1. Clonar Repositório
```bash
git clone [url-do-repositorio]
cd {nome_projeto}
```

### 2. Ambiente Virtual
```bash
python -m venv env
# Windows
env\\Scripts\\activate
# Linux/Mac
source env/bin/activate
```

### 3. Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração do Banco
- Criar pasta `data/` na raiz do projeto
- Colocar arquivo `calcrh.db` na pasta `data/`
- **IMPORTANTE**: Não criar banco via código

## 🏃‍♂️ Execução

### Desenvolvimento Local
```bash
# Ativar ambiente virtual
.\\env\\Scripts\\Activate

# Executar aplicação 7 Armadilhas do Eu Empresário
streamlit run main.py
```

### Acesso
- Aplicação estará disponível em: `http://localhost:8501`
- Login com credenciais do banco de dados

## 🔐 Variáveis de Ambiente

### Configuração Automática
- Sistema detecta ambiente via `config.py`
- Produção: `RENDER=true` (detectado automaticamente)
- Desenvolvimento: ambiente local

### Estrutura de Dados
- **Desenvolvimento**: `./data/calcrh.db`
- **Produção**: `/var/data/calcrh.db` (Render.com)

## 🚀 Deploy

### Preparação
1. Configurar repositório GitHub
2. Conectar ao Render.com
3. Configurar variáveis de ambiente

### Plataforma de Deploy (Render.com)
- **Tipo**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`
- **Disco Persistente**: Habilitado para dados

### Configurações de Produção
- **Porta**: Configurada automaticamente pelo Render
- **Endereço**: 0.0.0.0 (aceita conexões externas)
- **Timeout**: Configurado para aplicações Streamlit

## 🐛 Troubleshooting

### Problemas Comuns

#### Erro: "Banco de dados não encontrado"
**Solução**: Verificar se pasta `data/` existe e contém `calcrh.db`

#### Erro: "Pasta 'data' não encontrada"
**Solução**: Criar pasta `data/` na raiz do projeto

#### Erro: "database is locked"
**Solução**: Aguardar liberação do banco ou reiniciar aplicação

#### Erro: "Module not found"
**Solução**: Verificar se ambiente virtual está ativo e dependências instaladas

### Logs
- **Localização**: Terminal onde Streamlit está rodando
- **Configuração**: Logs automáticos do Streamlit
- **Debug**: Usar comentário `# Debug` para prints temporários

### Performance
- **Cache**: Sistema usa `@st.cache_data` para otimização
- **Rerun**: Controle inteligente evita reruns desnecessários
- **Banco**: SQLite otimizado para operações

---

## 📞 Suporte

Em caso de problemas:
1. Verificar documentação em `docs/`
2. Consultar logs no terminal
3. Verificar configurações em `config.py`
4. Verificar se banco de dados está acessível
5. Contatar equipe de desenvolvimento

### Comandos Úteis
```bash
# Verificar dependências
pip list

# Verificar estrutura do projeto
dir /s  # Windows
ls -la  # Linux/Mac

# Verificar banco de dados
sqlite3 data/calcrh.db ".tables"
```
"""
    
    with open("docs/configuracao_ambiente.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python script_criar_base_conhecimento.py <nome_projeto> [framework]")
        print("📝 Exemplo: python script_criar_base_conhecimento.py meu_projeto streamlit")
        sys.exit(1)
    
    nome_projeto = sys.argv[1]
    framework = sys.argv[2] if len(sys.argv) > 2 else "streamlit"
    
    criar_estrutura_base_conhecimento(nome_projeto, framework) 