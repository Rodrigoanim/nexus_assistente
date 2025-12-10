# 🔧 Documentação da Refatoração da Plataforma de Assessments

**Data:** 09/11/2025  
**Versão:** 1.0  
**Objetivo:** Documentar a refatoração realizada para tornar a plataforma modular, consistente e facilitar adição de novos assessments

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Problemas Identificados](#problemas-identificados)
3. [Solução Implementada](#solução-implementada)
4. [Arquitetura da Solução](#arquitetura-da-solução)
5. [Organograma de Estrutura](#organograma-de-estrutura)
6. [Lógica de Funcionamento](#lógica-de-funcionamento)
7. [Como Adicionar Novo Assessment](#como-adicionar-novo-assessment)
8. [Benefícios da Refatoração](#benefícios-da-refatoração)

---

## 🎯 Visão Geral

A refatoração foi realizada para eliminar inconsistências e exceções no código, tornando a plataforma **100% modular** e **consistente**. O objetivo principal é facilitar a adição de novos assessments sem necessidade de modificar código central.

### **Antes da Refatoração:**
- ❌ Assessment 01 tinha função especial `process_forms_tab()` (sem sufixo)
- ❌ Cada assessment tinha bloco `elif` específico no `main.py` (~280 linhas duplicadas)
- ❌ Configurações espalhadas em múltiplos arquivos
- ❌ Código duplicado para renderização de menus
- ❌ Difícil adicionar novos assessments (precisava modificar `main.py`)

### **Depois da Refatoração:**
- ✅ Todos os assessments usam `process_forms_tab_XX()` (padronizado)
- ✅ Código genérico e reutilizável (~40 linhas)
- ✅ Configuração centralizada em `assessment_config.py`
- ✅ Função genérica para renderização de menus
- ✅ Adicionar novo assessment = apenas adicionar entrada na configuração

---

## 🔍 Problemas Identificados

### **1. Inconsistência de Nomes de Funções**

**Problema:**
```python
# Assessment 01 - EXCEÇÃO
def process_forms_tab(section='perfil'):  # Sem sufixo numérico
    return process_forms_tab_01(section)

# Assessments 02-05 - PADRÃO
def process_forms_tab_02(section='perfil'):  # Com sufixo
    ...
```

**Impacto:**
- Código especial no `load_assessment_module()` para tratar exceção
- Confusão sobre qual nome usar
- Dificuldade de manutenção

### **2. Código Duplicado no main.py**

**Problema:**
Cada assessment (01-04) tinha um bloco `elif` específico com ~70 linhas de código quase idêntico:

```python
if assessment_id == "01":
    # 70 linhas de código específico
elif assessment_id == "02":
    # 70 linhas de código quase idêntico
elif assessment_id == "03":
    # 70 linhas de código quase idêntico
elif assessment_id == "04":
    # 70 linhas de código quase idêntico
else:
    # Código genérico
```

**Impacto:**
- ~280 linhas de código duplicado
- Difícil manutenção (mudança precisa ser feita em 4 lugares)
- Risco de inconsistências entre assessments

### **3. Configurações Espalhadas**

**Problema:**
- Mapeamento de módulos no `load_assessment_module()`
- Seções hardcoded em cada bloco `elif`
- Chaves de session_state espalhadas pelo código

**Impacto:**
- Difícil localizar configurações
- Risco de esquecer alguma configuração ao adicionar novo assessment

---

## ✅ Solução Implementada

### **1. Arquivo de Configuração Centralizado**

Criado `paginas/assessment_config.py` com todas as configurações:

```python
ASSESSMENT_CONFIG = {
    "01": {
        "form_module": "form_model_01",
        "results_module": "resultados_01",
        "sections": {
            "📋 Parte 1": "perfil",
            "✏️ Parte 2": "comportamento",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,
        "menu_title": "#### 📋 Selecione a Parte que deseja",
        "menu_message": "IMPORTANTE: precisa responder tanto a Parte 1 quanto a Parte 2",
        "selector_key": "disc10_section_selector",
        "selector_bottom_key": "disc10_section_selector_bottom",
        "target_section_key": "target_section_01"
    },
    # ... outros assessments
}
```

### **2. Função Genérica para Menus**

Criada `render_section_menu()` que funciona para todos os assessments:

```python
def render_section_menu(assessment_id, config, process_forms_tab):
    """
    Renderiza menu genérico de seleção de seções para um assessment.
    Funciona para todos os assessments que têm has_menu=True
    """
    sections = config.get("sections", {})
    selector_key = config.get("selector_key")
    # ... lógica genérica usando configuração
```

### **3. Padronização de Nomes**

- Removida função wrapper `process_forms_tab()` do `form_model_01.py`
- Todos os assessments agora usam `process_forms_tab_XX()` (incluindo 01)
- Função `get_function_name()` padroniza o nome

### **4. Refatoração do show_assessment_execution()**

**Antes:** ~280 linhas com múltiplos blocos `elif`  
**Depois:** ~40 linhas usando configuração dinâmica

```python
def show_assessment_execution():
    # Obter configuração
    config = get_assessment_config(assessment_id)
    
    # Carregar módulo
    process_forms_tab, show_results, assessment_name = load_assessment_module(assessment_id)
    
    # Renderizar menu ou executar diretamente
    if has_menu(assessment_id):
        render_section_menu(assessment_id, config, process_forms_tab)
    else:
        process_forms_tab()
```

---

## 🏗️ Arquitetura da Solução

### **Componentes Principais**

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (Orquestrador)                   │
│  - show_assessment_execution()                              │
│  - load_assessment_module()                                 │
│  - render_section_menu()                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Usa
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          assessment_config.py (Configuração)                │
│  - ASSESSMENT_CONFIG (dicionário centralizado)             │
│  - get_assessment_config()                                  │
│  - get_function_name()                                       │
│  - has_menu()                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Define estrutura de
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Módulos Específicos por Assessment             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ form_model_  │  │ form_model_  │  │ form_model_  │    │
│  │   01.py      │  │   02.py      │  │   03.py      │    │
│  │              │  │              │  │              │    │
│  │ process_     │  │ process_     │  │ process_     │    │
│  │ forms_tab_   │  │ forms_tab_   │  │ forms_tab_   │    │
│  │ 01()         │  │ 02()         │  │ 03()         │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ resultados_  │  │ resultados_  │  │ resultados_  │    │
│  │   01.py      │  │   02.py      │  │   03.py      │    │
│  │              │  │              │  │              │    │
│  │ show_        │  │ show_        │  │ show_        │    │
│  │ results()    │  │ results()    │  │ results()    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### **Fluxo de Execução**

```
1. Usuário seleciona assessment
   ↓
2. show_assessment_execution() é chamado
   ↓
3. get_assessment_config(assessment_id) busca configuração
   ↓
4. load_assessment_module() carrega módulos dinamicamente
   ├─ get_form_module_name() → "form_model_XX"
   ├─ get_results_module_name() → "resultados_XX"
   └─ get_function_name() → "process_forms_tab_XX"
   ↓
5. Verifica se tem menu (has_menu())
   ├─ SIM → render_section_menu() (usa configuração)
   └─ NÃO → process_forms_tab() diretamente
   ↓
6. process_forms_tab_XX(section) executa o assessment
```

---

## 📊 Organograma de Estrutura

### **Estrutura de Arquivos por Assessment**

```
Plataforma_CH/
│
├── main.py                          ← Orquestrador principal
│   ├── show_assessment_execution()  ← Função genérica (usa config)
│   ├── load_assessment_module()     ← Carrega módulos dinamicamente
│   └── render_section_menu()         ← Renderiza menu genérico
│
├── paginas/
│   │
│   ├── assessment_config.py         ← ⭐ CONFIGURAÇÃO CENTRALIZADA
│   │   └── ASSESSMENT_CONFIG        ← Dicionário com todos os assessments
│   │
│   ├── form_model_01.py            ← Assessment 01 - Formulário
│   │   ├── new_user()               ← Inicializa dados do usuário
│   │   └── process_forms_tab_01()   ← Processa seções do assessment
│   │
│   ├── resultados_01.py             ← Assessment 01 - Resultados
│   │   ├── new_user()               ← Inicializa resultados
│   │   └── show_results()           ← Exibe análises e gráficos
│   │
│   ├── form_model_02.py            ← Assessment 02 - Formulário
│   │   ├── new_user()
│   │   └── process_forms_tab_02()
│   │
│   ├── resultados_02.py             ← Assessment 02 - Resultados
│   │   ├── new_user()
│   │   └── show_results()
│   │
│   ├── form_model_03.py            ← Assessment 03 - Formulário
│   │   └── ...
│   │
│   ├── resultados_03.py             ← Assessment 03 - Resultados
│   │   └── ...
│   │
│   ├── form_model_04.py            ← Assessment 04 - Formulário
│   │   └── ...
│   │
│   ├── resultados_04.py             ← Assessment 04 - Resultados
│   │   └── ...
│   │
│   ├── form_model_05.py            ← Assessment 05 - Formulário
│   │   └── ...
│   │
│   └── resultados_05.py             ← Assessment 05 - Resultados
│       └── ...
│
└── data/
    └── calcrh2.db                   ← Banco de dados
        ├── forms_tab_01             ← Tabela do Assessment 01
        ├── forms_tab_02             ← Tabela do Assessment 02
        ├── forms_tab_03             ← Tabela do Assessment 03
        ├── forms_tab_04             ← Tabela do Assessment 04
        ├── forms_tab_05             ← Tabela do Assessment 05
        ├── forms_resultados_01      ← Resultados do Assessment 01
        ├── forms_resultados_02      ← Resultados do Assessment 02
        └── ... (outras tabelas)
```

### **Agrupamento por Assessment**

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT 01                             │
│                  (DISC Essencial)                           │
├─────────────────────────────────────────────────────────────┤
│ Configuração: assessment_config.py → "01"                  │
│                                                              │
│ Módulos:                                                     │
│   ├── form_model_01.py                                      │
│   │   └── process_forms_tab_01(section)                    │
│   │       ├── section='perfil'                             │
│   │       ├── section='comportamento'                       │
│   │       └── section='resultado'                          │
│   │                                                          │
│   └── resultados_01.py                                      │
│       └── show_results(tabela, titulo, user_id)            │
│                                                              │
│ Tabelas BD:                                                  │
│   ├── forms_tab_01 (dados do formulário)                   │
│   └── forms_resultados_01 (resultados calculados)          │
│                                                              │
│ Interface:                                                   │
│   ├── Menu: Sim (has_menu=True)                            │
│   ├── Seções: 📋 Parte 1 | ✏️ Parte 2 | 📊 Resultados     │
│   └── Variáveis: perfil | comportamento | resultado        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT 02                             │
│                  (DISC Integral)                            │
├─────────────────────────────────────────────────────────────┤
│ Configuração: assessment_config.py → "02"                  │
│                                                              │
│ Módulos:                                                     │
│   ├── form_model_02.py                                      │
│   │   └── process_forms_tab_02(section)                    │
│   │                                                          │
│   └── resultados_02.py                                      │
│       └── show_results(tabela, titulo, user_id)            │
│                                                              │
│ Tabelas BD:                                                  │
│   ├── forms_tab_02                                          │
│   └── forms_resultados_02                                  │
│                                                              │
│ Interface:                                                   │
│   ├── Menu: Sim (has_menu=True)                            │
│   └── Seções: 📋 Parte 1 | ✏️ Parte 2 | 📊 Resultados     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT 03                             │
│              (Âncoras de Carreira)                          │
├─────────────────────────────────────────────────────────────┤
│ Configuração: assessment_config.py → "03"                  │
│                                                              │
│ Módulos:                                                     │
│   ├── form_model_03.py                                      │
│   │   └── process_forms_tab_03(section)                    │
│   │       ├── section='ancoras_p1'                          │
│   │       ├── section='ancoras_p2'                          │
│   │       └── section='resultado'                           │
│   │                                                          │
│   └── resultados_03.py                                      │
│       └── show_results(tabela, titulo, user_id)            │
│                                                              │
│ Tabelas BD:                                                  │
│   ├── forms_tab_03                                          │
│   └── forms_resultados_03                                  │
│                                                              │
│ Interface:                                                   │
│   ├── Menu: Sim (has_menu=True)                            │
│   └── Seções: 📋 Parte 1 | ✏️ Parte 2 | 📊 Resultados     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT 04                             │
│           (Armadilhas do Empresário)                        │
├─────────────────────────────────────────────────────────────┤
│ Configuração: assessment_config.py → "04"                  │
│                                                              │
│ Módulos:                                                     │
│   ├── form_model_04.py                                      │
│   │   └── process_forms_tab_04(section)                    │
│   │       ├── section='armadilhas_p1'                       │
│   │       ├── section='armadilhas_p2'                      │
│   │       └── section='resultado'                          │
│   │                                                          │
│   └── resultados_04.py                                      │
│       └── show_results(tabela, titulo, user_id)            │
│                                                              │
│ Tabelas BD:                                                  │
│   ├── forms_tab_04                                          │
│   └── forms_resultados_04                                  │
│                                                              │
│ Interface:                                                   │
│   ├── Menu: Sim (has_menu=True)                            │
│   └── Seções: 📋 Parte 1 | ✏️ Parte 2 | 📊 Resultados     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT 05                             │
│            (Anamnese Completa)                               │
├─────────────────────────────────────────────────────────────┤
│ Configuração: assessment_config.py → "05"                  │
│                                                              │
│ Módulos:                                                     │
│   ├── form_model_05.py                                      │
│   │   └── process_forms_tab_05(section)                    │
│   │       ├── section='anamnese_p1'                        │
│   │       ├── section='anamnese_p2'                        │
│   │       └── section='resultado'                          │
│   │                                                          │
│   └── resultados_05.py                                      │
│       └── show_results(tabela, titulo, user_id)            │
│                                                              │
│ Tabelas BD:                                                  │
│   ├── forms_tab_05                                          │
│   └── forms_resultados_05                                  │
│                                                              │
│ Interface:                                                   │
│   ├── Menu: Não (has_menu=False)                           │
│   └── Execução: Direta (sem seleção de seções)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Lógica de Funcionamento

### **1. Carregamento Dinâmico de Módulos**

```python
def load_assessment_module(assessment_id):
    # 1. Busca configuração centralizada
    config = get_assessment_config(assessment_id)
    
    # 2. Obtém nomes dos módulos da configuração
    form_module_name = get_form_module_name(assessment_id)      # "form_model_01"
    results_module_name = get_results_module_name(assessment_id) # "resultados_01"
    
    # 3. Carrega módulos dinamicamente
    form_module = importlib.import_module(f"paginas.{form_module_name}")
    results_module = importlib.import_module(f"paginas.{results_module_name}")
    
    # 4. Obtém função padronizada (todos usam process_forms_tab_XX)
    function_name = get_function_name(assessment_id)  # "process_forms_tab_01"
    process_forms_tab = getattr(form_module, function_name)
    
    # 5. Retorna funções e nome do assessment
    return process_forms_tab, show_results, assessment_name
```

### **2. Renderização de Menu Genérico**

```python
def render_section_menu(assessment_id, config, process_forms_tab):
    # 1. Extrai configurações do dicionário
    sections = config.get("sections")           # {"📋 Parte 1": "perfil", ...}
    selector_key = config.get("selector_key")   # "disc10_section_selector"
    menu_title = config.get("menu_title")       # "#### 📋 Selecione..."
    menu_message = config.get("menu_message")    # "IMPORTANTE: ..."
    
    # 2. Verifica se há seção alvo (do menu do final da página)
    target_section = st.session_state.get(config.get("target_section_key"))
    
    # 3. Renderiza radio buttons usando configuração
    selected_section = st.radio(
        menu_message,
        options=list(sections.keys()),
        key=selector_key,
        horizontal=True
    )
    
    # 4. Mapeia rótulo selecionado para variável interna
    section_value = sections[selected_section]  # "perfil"
    
    # 5. Executa função do assessment com seção selecionada
    process_forms_tab(section_value)
```

### **3. Execução do Assessment**

```python
def show_assessment_execution():
    # 1. Validações iniciais
    assessment_id = st.session_state.get("selected_assessment_id")
    if not assessment_id:
        return
    
    # 2. Verifica acesso do usuário
    if not check_assessment_access(user_id, assessment_id):
        return
    
    # 3. Busca configuração
    config = get_assessment_config(assessment_id)
    
    # 4. Carrega módulos dinamicamente
    process_forms_tab, show_results, assessment_name = load_assessment_module(assessment_id)
    
    # 5. Decisão: Menu ou Execução Direta
    if has_menu(assessment_id):
        # Assessment com menu de seções (01-04)
        render_section_menu(assessment_id, config, process_forms_tab)
    else:
        # Assessment sem menu (05)
        process_forms_tab()
```

### **4. Padronização de Nomes**

**Antes:**
```python
# Exceção para 01
if assessment_id == "01":
    function_name = "process_forms_tab"  # Sem sufixo
else:
    function_name = f"process_forms_tab_{assessment_id}"  # Com sufixo
```

**Depois:**
```python
# Todos padronizados
function_name = get_function_name(assessment_id)  # Sempre "process_forms_tab_XX"
# Retorna: "process_forms_tab_01", "process_forms_tab_02", etc.
```

---

## ➕ Como Adicionar Novo Assessment

### **Passo a Passo Simplificado**

#### **1. Adicionar Configuração**

Editar `paginas/assessment_config.py`:

```python
ASSESSMENT_CONFIG = {
    # ... assessments existentes ...
    
    "06": {  # ← Novo assessment
        "form_module": "form_model_06",
        "results_module": "resultados_06",
        "sections": {
            "📋 Parte 1": "secao_1",
            "✏️ Parte 2": "secao_2",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,  # ou False se não precisar de menu
        "menu_title": "#### 📋 Selecione a Parte que deseja",
        "menu_message": "Escolha a seção:",
        "selector_key": "assessment_06_section_selector",
        "selector_bottom_key": "assessment_06_section_selector_bottom",
        "target_section_key": "target_section_06"
    }
}
```

#### **2. Criar Módulo de Formulário**

Criar `paginas/form_model_06.py`:

```python
def new_user(cursor, user_id):
    """Inicializa registros para novo usuário."""
    cursor.execute("""
        SELECT COUNT(*) FROM forms_tab_06 WHERE user_id = ?
    """, (user_id,))
    # ... copia dados do user_id 0 ...

def process_forms_tab_06(section='secao_1'):
    """Processa seções do assessment 06."""
    # ... implementação específica ...
```

#### **3. Criar Módulo de Resultados**

Criar `paginas/resultados_06.py`:

```python
def new_user(cursor, user_id: int, tabela: str):
    """Inicializa resultados para novo usuário."""
    # ... implementação ...

def show_results(tabela_escolhida: str, titulo_pagina: str, user_id: int):
    """Exibe resultados do assessment 06."""
    # ... implementação ...
```

#### **4. Criar Tabelas no Banco de Dados**

```sql
CREATE TABLE forms_tab_06 (
    ID_element INTEGER PRIMARY KEY AUTOINCREMENT,
    name_element TEXT NOT NULL,
    -- ... outros campos ...
);

CREATE TABLE forms_resultados_06 (
    -- estrutura específica do assessment
);
```

#### **5. Pronto!**

✅ **Não precisa modificar `main.py`!**  
✅ O sistema detecta automaticamente o novo assessment  
✅ Menu é renderizado automaticamente (se `has_menu=True`)  
✅ Tudo funciona através da configuração centralizada

---

## 🎁 Benefícios da Refatoração

### **1. Modularidade**
- Cada assessment é independente
- Adicionar novo assessment não afeta os existentes
- Configuração isolada e clara

### **2. Consistência**
- ✅ Todos os assessments seguem as mesmas regras
- ✅ Nomes de funções padronizados
- ✅ Estrutura uniforme

### **3. Manutenibilidade**
- ✅ Código centralizado e organizado
- ✅ Fácil localizar e corrigir problemas
- ✅ Mudanças em um lugar afetam todos os assessments

### **4. Escalabilidade**
- ✅ Adicionar novo assessment = ~5 minutos
- ✅ Não precisa modificar código central
- ✅ Sistema cresce sem complexidade adicional

### **5. Redução de Código**
- ✅ **Antes:** ~280 linhas duplicadas
- ✅ **Depois:** ~40 linhas genéricas
- ✅ **Redução:** ~85% menos código

### **6. Facilidade de Testes**
- ✅ Cada assessment pode ser testado isoladamente
- ✅ Configuração clara facilita testes
- ✅ Menos pontos de falha

---

## 📝 Notas Técnicas

### **Padrões Seguidos**

1. **Nomenclatura:**
   - Funções: `process_forms_tab_XX()` (sempre com sufixo)
   - Módulos: `form_model_XX.py`, `resultados_XX.py`
   - Tabelas: `forms_tab_XX`, `forms_resultados_XX`

2. **Estrutura de Configuração:**
   - Todas as configurações em `assessment_config.py`
   - Dicionário `ASSESSMENT_CONFIG` como fonte única de verdade
   - Funções helper para acessar configurações

3. **Carregamento Dinâmico:**
   - Uso de `importlib` para carregar módulos em runtime
   - `getattr()` para obter funções dinamicamente
   - Tratamento de erros robusto

4. **Separação de Responsabilidades:**
   - `main.py`: Orquestração e UI
   - `assessment_config.py`: Configuração
   - `form_model_XX.py`: Lógica do formulário
   - `resultados_XX.py`: Lógica de resultados

---

## 🔗 Referências

- **Guia de Implementação:** `docs/guia_implementacao_assessments.md`
- **Arquivo de Configuração:** `paginas/assessment_config.py`
- **Código Principal:** `main.py` (funções `show_assessment_execution()`, `load_assessment_module()`, `render_section_menu()`)

---

**Criado em:** 09/11/2025  
**Autor:** Sistema de Refatoração  
**Versão:** 1.0

