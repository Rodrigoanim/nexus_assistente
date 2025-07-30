# 🚀 Guia Completo de Deploy - Assistente NEXUS

## 📦 Arquivos para Enviar ao Git

### ✅ **ARQUIVOS OBRIGATÓRIOS**

```bash
# Aplicação principal
nexus_assistant.py                          # Aplicação Streamlit
Manual_Geral_Nexus_2021_formatado.md        # Base de conhecimento NEXUS

# Configuração
requirements.txt                            # Dependências Python
render.yaml                                # Configuração Render.com
pyproject.toml                             # Configuração projeto
.python-version                            # Versão Python
.gitignore                                 # Arquivos a ignorar
env.example                                # Exemplo de variáveis

# Documentação
README.md                                  # Documentação principal
melhorias_busca_nexus.md                   # Documentação técnica
docs/                                      # Pasta de documentação
```

### ❌ **ARQUIVOS QUE NÃO DEVEM SUBIR**

```bash
# Temporários/Cache
tmp/                                       # Pasta temporária
tpm/                                       # Pasta temporária
__pycache__/                              # Cache Python
.venv/                                    # Ambiente virtual
uv.lock                                   # Lock file (muito grande)

# Sensíveis
.env                                      # Variáveis locais
*.db                                      # Banco de dados
api.txt                                   # Chaves API

# Desenvolvimento
.cursorrules                              # Configuração Cursor
alteracoes_*.txt                          # Logs de alterações
rasc/                                     # Rascunhos
main_app.py                               # Versão antiga
21_pdf_agent.py                           # Arquivo teste
correcao_*.txt                           # Logs temporários
teste_*.txt                              # Logs de teste
melhorias_*.txt                          # Logs de melhorias
```

## 🛠️ Comandos para Deploy

### 1. **Preparar Repositório Git**

```bash
# Verificar status do git
git status

# Adicionar arquivos obrigatórios
git add nexus_assistant.py
git add Manual_Geral_Nexus_2021_formatado.md
git add requirements.txt
git add render.yaml
git add pyproject.toml
git add .python-version
git add .gitignore
git add env.example
git add README.md
git add melhorias_busca_nexus.md
git add docs/
git add DEPLOY.md

# Verificar se nenhum arquivo sensível foi adicionado
git status

# Commit das mudanças
git commit -m "🚀 Deploy: Assistente NEXUS - Sistema completo otimizado"

# Enviar para GitHub
git push origin main
```

### 2. **Configurar Render.com**

#### **Passo 1: Criar Serviço**
1. Acesse [render.com](https://render.com)
2. Faça login/cadastro
3. Clique em "New" → "Web Service"
4. Conecte seu repositório GitHub
5. Selecione o repositório do projeto

#### **Passo 2: Configurações Automáticas**
O arquivo `render.yaml` já configura automaticamente:
- ✅ **Runtime**: Python
- ✅ **Build Command**: `pip install -r requirements.txt`  
- ✅ **Start Command**: `streamlit run nexus_assistant.py --server.port $PORT --server.address 0.0.0.0`

#### **Passo 3: Variáveis de Ambiente**
Configure no painel do Render:

```bash
OPENAI_API_KEY = sua_chave_openai_aqui         # ✅ OBRIGATÓRIO
ENVIRONMENT = production                        # ✅ OBRIGATÓRIO  
DEBUG = false                                  # ✅ OBRIGATÓRIO
TAVILY_API_KEY = sua_chave_tavily_aqui         # ⚠️ OPCIONAL
```

### 3. **Deploy Automático**

Após configurar:
1. ✅ Render detecta o `render.yaml`
2. ✅ Instala dependências automaticamente
3. ✅ Inicia aplicação Streamlit
4. ✅ Aplicação fica disponível na URL fornecida

## 🔐 Segurança

### **Arquivos Protegidos (.gitignore)**
```bash
# Nunca vão para o GitHub
__pycache__/                              # Cache Python
.venv                                     # Ambiente virtual
.env                                      # Variáveis locais
.env.local                               # Variáveis locais
.env.production                          # Variáveis produção
*.db                                     # Banco dados
tmp/                                     # Temporários
tpm/                                     # Temporários
*.log                                    # Logs
.vscode/                                 # IDE
.idea/                                   # IDE
.DS_Store                                # macOS
Thumbs.db                                # Windows
```

### **Variáveis de Ambiente**
- ✅ **Local**: Arquivo `.env` (não commitado)
- ✅ **Produção**: Painel do Render.com
- ❌ **NUNCA** colocar chaves API no código

## 📋 Checklist Final

### **Antes do Deploy**
- [ ] Arquivo `nexus_assistant.py` funcionando localmente
- [ ] `requirements.txt` com todas dependências
- [ ] `render.yaml` configurado corretamente
- [ ] `.gitignore` protegendo arquivos sensíveis
- [ ] `env.example` com exemplo de variáveis
- [ ] README.md atualizado

### **Durante o Deploy**
- [ ] Repositório GitHub atualizado
- [ ] Render.com conectado ao repositório
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy iniciado automaticamente

### **Após o Deploy**
- [ ] Aplicação acessível via URL do Render
- [ ] Teste: "O que é NEXUS?" funcionando
- [ ] Teste: Sistema de pontuação funcionando
- [ ] Logs sem erros críticos

## 🎯 URL Final

Após deploy bem-sucedido:
```
https://assistente-nexus.onrender.com
```

## 🆘 Troubleshooting

### **Erro: Chave API não configurada**
- Verificar variável `OPENAI_API_KEY` no Render.com
- Verificar se a chave está válida

### **Erro: Módulo não encontrado**
- Verificar `requirements.txt`
- Adicionar dependência faltante

### **Erro: Aplicação não inicia**
- Verificar logs no Render.com
- Verificar `render.yaml` configuração

### **Erro: Base de conhecimento não carrega**
- Verificar se `Manual_Geral_Nexus_2021_formatado.md` foi enviado
- Verificar permissões de arquivo

## ✅ Status: Pronto para Deploy

O projeto está **100% preparado** para deploy no Render.com com todas as otimizações implementadas!