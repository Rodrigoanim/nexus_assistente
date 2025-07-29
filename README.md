# 🌍 Assessment DISC - Equipe Multi-idioma

Sistema de roteamento inteligente para respostas em múltiplos idiomas usando OpenAI e Streamlit.

## 🚀 Funcionalidades

- **Roteamento Multi-idioma**: Suporte para Inglês, Chinês e Francês
- **Interface Web**: Interface amigável com Streamlit
- **Segurança**: Configuração segura de chaves API
- **Deploy Automático**: Configuração para Render.com

## 📋 Pré-requisitos

- Python 3.13+
- Conta OpenAI (para API key)
- Conta Tavily (opcional, para pesquisa)

## 🔧 Configuração Local

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd curso-agno
```

### 2. Instale as dependências
```bash
uv sync
```

### 3. Configure as variáveis de ambiente

**IMPORTANTE**: Nunca commite suas chaves API no GitHub!

Crie um arquivo `.env` na raiz do projeto (baseado no `env_example.txt`):
```bash
# OpenAI API Key (obrigatório)
OPENAI_API_KEY=sua_chave_openai_aqui

# Tavily API Key (opcional)
TAVILY_API_KEY=sua_chave_tavily_aqui

# Configurações do Ambiente
ENVIRONMENT=development
DEBUG=True
```

**⚠️ Segurança**: O arquivo `.env` está no `.gitignore` e não será commitado.

### 4. Execute a aplicação
```bash
# Aplicação principal (Streamlit)
uv run streamlit run main_app.py

# Teste da equipe multi-idioma
uv run 41_teams.py
```

## 🌐 Deploy no Render.com

### 1. Preparação do Repositório

Certifique-se de que os seguintes arquivos estão no repositório:
- ✅ `main_app.py` (aplicação principal)
- ✅ `requirements.txt` (dependências)
- ✅ `render.yaml` (configuração do Render)
- ✅ `.gitignore` (proteção de arquivos sensíveis)

### 2. Configuração no Render.com

1. **Crie uma nova conta** no [Render.com](https://render.com)
2. **Conecte seu repositório GitHub**
3. **Crie um novo Web Service**
4. **Configure as variáveis de ambiente**:
   - `OPENAI_API_KEY`: Sua chave OpenAI
   - `TAVILY_API_KEY`: Sua chave Tavily (opcional)
   - `ENVIRONMENT`: production
   - `DEBUG`: false

### 3. Configuração Automática

O arquivo `render.yaml` já está configurado para:
- ✅ Instalar dependências automaticamente
- ✅ Executar a aplicação Streamlit
- ✅ Configurar variáveis de ambiente
- ✅ Usar porta dinâmica do Render

## 🔒 Segurança

### Arquivos Protegidos
- ✅ `.env` (não commitado)
- ✅ `*.db` (banco de dados)
- ✅ `tpm/` (arquivos temporários)
- ✅ `__pycache__/` (cache Python)

### Variáveis de Ambiente
- ✅ Chaves API não expostas no código
- ✅ Configuração via arquivo `.env` local
- ✅ Configuração via painel do Render.com

## 📁 Estrutura do Projeto

```
curso-agno/
├── main_app.py              # Aplicação principal Streamlit
├── 41_teams.py             # Sistema de equipes multi-idioma
├── requirements.txt         # Dependências para deploy
├── render.yaml             # Configuração Render.com
├── .gitignore              # Proteção de arquivos
├── README.md               # Este arquivo
└── .env                    # Variáveis de ambiente (não commitado)
```

## 🛠️ Desenvolvimento

### Executar Localmente
```bash
# Aplicação principal
uv run streamlit run main_app.py

# Teste da equipe
uv run 41_teams.py

# Outros testes
uv run 13_own_tools.py
```

### Estrutura de Código
- **main_app.py**: Interface Streamlit principal
- **41_teams.py**: Sistema de equipes multi-idioma
- **13_own_tools.py**: Ferramentas personalizadas
- **render.yaml**: Configuração de deploy

## 📝 Logs de Alterações

### Versão 1.0 (06/06/2025)
- ✅ Migração de Groq para OpenAI
- ✅ Configuração segura de chaves API
- ✅ Interface Streamlit moderna
- ✅ Deploy automático no Render.com
- ✅ Documentação completa

## 🆘 Suporte

### Problemas Comuns

1. **Erro de chave API**:
   - Verifique se as variáveis de ambiente estão configuradas
   - No Render.com: vá em Environment → Add Environment Variable

2. **Erro de dependências**:
   - Execute `uv sync` para instalar dependências
   - Verifique se o Python 3.13+ está instalado

3. **Erro de deploy**:
   - Verifique se todos os arquivos estão commitados
   - Confirme se o `render.yaml` está correto

### Contato
Para suporte técnico, abra uma issue no GitHub ou entre em contato com a equipe de desenvolvimento.

## 📄 Licença

Este projeto é parte do Assessment DISC e está sob licença proprietária.

---

**🌍 Assessment DISC - Transformando comunicação multi-idioma com IA**
