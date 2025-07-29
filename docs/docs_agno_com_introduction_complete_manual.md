-----

# **Manual de Boas Práticas e Referência Técnica: Agno & Streamlit**

Este documento serve como um manual completo para a equipe de desenvolvimento sobre como utilizar o framework Agno em conjunto com Python. O foco é a construção de sistemas multi-agentes, utilizando o Streamlit como interface de teste e administração.

### **1. Introdução ao Framework Agno**

#### 1.1. O que é o Agno?

```
1.1.1. Agno é um framework Python de código aberto projetado para a construção de sistemas multi-agentes de nível de produção. Ele fornece os blocos de construção fundamentais para criar, implantar e gerenciar sistemas agenticos, permitindo que os desenvolvedores se concentrem na lógica de negócios principal em vez de na infraestrutura subjacente.
1.1.2. Ele é construído sobre bibliotecas populares como FastAPI, Pydantic e SQLAlchemy, e foi projetado para ser modular, extensível e fácil de usar.
```

#### 1.2. Quem Utiliza o Agno?

```
1.2.1. O Agno é utilizado por engenheiros e pesquisadores de IA para construir sistemas agenticos de alto desempenho. Ele acelera o desenvolvimento ao eliminar a necessidade de código repetitivo (boilerplate) e tempo de pesquisa, permitindo a criação de aplicações complexas e com estado.
```

#### 1.3. Os 5 Níveis de Sistemas Agenticos

```
1.3.1. O Agno permite a construção de agentes em diferentes níveis de complexidade e capacidade, fornecendo um caminho claro para a evolução dos sistemas.
    1.3.1.1. **Nível 1: Agentes com Ferramentas e Instruções.** O nível mais básico, onde os agentes podem executar ações através de ferramentas com base em um conjunto de instruções.
    1.3.1.2. **Nível 2: Agentes com Conhecimento e Armazenamento.** Os agentes podem acessar uma base de conhecimento para responder a perguntas (RAG - Retrieval Augmented Generation) e salvar o histórico da sessão.
    1.3.1.3. **Nível 3: Agentes com Memória e Raciocínio.** Os agentes podem "pensar" antes de agir, analisar os resultados de suas ações e lembrar informações de interações passadas.
    1.3.1.4. **Nível 4: Times de Agentes.** Múltiplos agentes podem colaborar para resolver problemas complexos, cada um com papéis e ferramentas especializados.
    1.3.1.5. **Nível 5: Workflows Agenticos.** Fluxos de trabalho com estado e determinísticos que orquestram múltiplos agentes para executar tarefas complexas de maneira confiável.
```

### **2. Configuração do Ambiente de Desenvolvimento**

#### 2.1. Instalação do Agno

````
2.1.1. Para começar a usar o Agno, instale-o usando o pip, o gerenciador de pacotes do Python. Recomenda-se o uso de um ambiente virtual para evitar conflitos de dependência.
```bash
pip install agno
```
````

#### 2.2. Configuração de Variáveis de Ambiente

````
2.2.1. Para que o Agno e seus modelos de linguagem funcionem, você precisa configurar chaves de API e outras configurações como variáveis de ambiente.
2.2.2. **Para macOS (usando zsh):**
    2.2.2.1. **Sessão Temporária:** Abra o terminal e execute:
    ```bash
    export OPENAI_API_KEY="sua_chave_api_aqui"
    ```
    2.2.2.2. **Sessão Permanente:** Para tornar a variável persistente em todas as sessões do terminal, adicione o comando `export` ao seu arquivo `~/.zshrc` e recarregue a configuração com `source ~/.zshrc`.

2.2.3. **Para Windows (usando PowerShell):**
    2.2.3.1. **Sessão Temporária:**
    ```powershell
    $env:OPENAI_API_KEY = "sua_chave_api_aqui"
    ```
    2.2.3.2. **Sessão Permanente:** Adicione o comando acima ao seu script de perfil do PowerShell (`$PROFILE`) e recarregue o perfil.

2.2.4. **Para Windows (usando Command Prompt):**
    2.2.4.1. **Sessão Temporária:**
    ```cmd
    set OPENAI_API_KEY=sua_chave_api_aqui
    ```
    2.2.4.2. **Sessão Permanente:**
    ```cmd
    setx OPENAI_API_KEY "sua_chave_api_aqui"
    ```
    Nota: `setx` torna a variável disponível em novas sessões do Command Prompt.
````

### **3. Componentes Fundamentais do Agno**

Compreender os componentes principais do Agno é essencial para construir agentes eficazes.

#### 3.1. O Modelo (`Model`)

```
3.1.1. O Modelo é o cérebro do Agente, responsável por controlar o fluxo de execução. Ele determina quando raciocinar, quando usar uma ferramenta e quando responder ao usuário. O Agno suporta modelos da OpenAI, Anthropic, Google, entre outros.
```

#### 3.2. As Ferramentas (`Tools`)

```
3.2.1. Ferramentas são as ações que um agente pode executar. Elas são a forma como os agentes interagem com o mundo exterior (APIs, bancos de dados, etc.). O Agno oferece mais de 80 kits de ferramentas pré-construídos.
```

#### 3.3. As Instruções (`Instructions`)

```
3.3.1. As instruções são a principal forma de programar um agente. Elas guiam o comportamento do modelo, definindo como ele deve usar as ferramentas e como deve responder. Boas instruções são claras, concisas e fornecem exemplos.
```

#### 3.4. O Raciocínio (`Reasoning`)

```
3.4.1. O raciocínio permite que os agentes "pensem" antes de responder e "analisem" os resultados de suas ações. Este processo de pensamento e análise melhora a confiabilidade e a qualidade das respostas, permitindo que o agente se corrija antes de apresentar um resultado final.
```

#### 3.5. O Conhecimento (`Knowledge` - RAG)

```
3.5.1. O conhecimento permite que um agente acesse informações específicas de um domínio em tempo de execução. Isso é feito através da Geração Aumentada por Recuperação (RAG), onde o agente pesquisa em um banco de dados vetorial (como ChromaDB ou Postgres com `pgvector`) para encontrar informações relevantes e usá-las para formular respostas mais precisas.
```

#### 3.6. O Armazenamento (`Storage`)

```
3.6.1. O armazenamento é usado para salvar o histórico da sessão e o estado do agente, tornando-o "stateful". Isso permite conversas de longo prazo, onde o agente pode se referir a interações anteriores. O Agno suporta backends como SQLite, Postgres e Redis.
```

#### 3.7. A Memória (`Memory`)

```
3.7.1. A memória dá aos agentes a capacidade de armazenar e recordar informações sobre um usuário entre sessões. Isso permite um alto grau de personalização, pois o agente pode aprender as preferências do usuário e adaptar seu comportamento ao longo do tempo.
```

### **4. Construindo seu Primeiro Agente (Nível 1)**

#### 4.1. Exemplo Prático: Agente de Raciocínio Financeiro

````
4.1.1. Este exemplo cria um agente que usa a API `yfinance` para buscar dados financeiros e o `ReasoningTools` para analisar e formatar a saída.
4.1.2. **Código Completo:**
```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

# 1. Instancie o Agente com um modelo, ferramentas e instruções.
reasoning_agent = Agent(
    model=Claude(id="claude-sonnet-4-20250514"), # Utiliza o modelo Sonnet da Anthropic
    tools=[
        ReasoningTools(add_instructions=True), # Adiciona a capacidade de "pensar"
        YFinanceTools( # Ferramentas para interagir com o Yahoo Finance
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True,
        ),
    ],
    instructions="Use tables to display data.", # Instrução para formatar saídas
    markdown=True, # Habilita a renderização de Markdown na saída
)

# 2. Interaja com o agente
for chunk in reasoning_agent.stream(
    "What are the analyst recommendations for NVDA and what is the current stock price?"
):
    print(chunk, end="")
```
4.1.3. **Análise do Código:**
    4.1.3.1. `Agent`: A classe principal para criar um agente.
    4.1.3.2. `model`: Especifica o LLM a ser usado. Neste caso, `claude-sonnet-4-20250514`.
    4.1.3.3. `tools`: Uma lista das ferramentas que o agente pode usar. `ReasoningTools` é crucial para o processo de pensamento, e `YFinanceTools` fornece as ações específicas de finanças.
    4.1.3.4. `instructions`: Orienta o agente sobre como se comportar e formatar suas respostas.
    4.1.3.5. `stream()`: Método usado para interagir com o agente e receber a resposta em tempo real (streaming).
````

### **5. Workspaces: Padronizando o Desenvolvimento para Produção**

#### 5.1. O que são Workspaces?

```
5.1.1. Workspaces são bases de código padronizadas e opinativas para a construção de sistemas agenticos prontos para produção. Eles fornecem uma estrutura organizada que inclui uma API, uma interface de administração e um banco de dados.
5.1.2. A principal vantagem é que eles encapsulam anos de aprendizado em engenharia de IA, permitindo que a equipe comece com uma base sólida e escalável.
```

#### 5.2. Estrutura Padrão de um Workspace

```
5.2.1. **RestAPI (FastAPI):** Um servidor para expor os Agentes, Times e Workflows como endpoints de API.
5.2.2. **Aplicação Streamlit:** Funciona como uma interface de administração e playground para testar e interagir com os agentes.
5.2.3. **Banco de Dados (Postgres):** Utilizado para armazenamento de sessão (histórico) e como um banco de dados vetorial para a funcionalidade de Conhecimento (RAG).
```

#### 5.3. Gerenciando Workspaces com a CLI do Agno

````
5.3.1. A Interface de Linha de Comando (CLI) do Agno simplifica a criação e o gerenciamento de workspaces.
5.3.2. **Criar um novo Workspace:**
```bash
ag ws create my-agentic-app
```
5.3.3. **Executar o Workspace localmente (usando Docker):**
```bash
cd my-agentic-app
ag ws up
```
5.3.4. **Templates Recomendados:**
    5.3.4.1. `agent-app`: O template mais completo, inclui a API FastAPI, a interface Streamlit e o banco de dados Postgres. **Este é o template recomendado para a equipe.**
    5.3.4.2. `agent-api`: Uma versão mais leve, apenas com a API FastAPI e o banco de dados Postgres.
````

### **6. Utilizando o Streamlit: Playground e Administração**

#### 6.1. A Função do Streamlit nos Workspaces Agno

```
6.1.1. Dentro de um Workspace Agno, o Streamlit não é apenas para visualização de dados, mas sim uma poderosa ferramenta de administração e depuração para o sistema agentico.
6.1.2. Ele permite:
    - Interagir diretamente com os agentes.
    - Inspecionar o histórico da sessão e a memória do usuário.
    - Visualizar e configurar parâmetros do agente, modelo e ferramentas.
    - Rastrear os "pensamentos" do agente (traços de raciocínio).
```

#### 6.2. Criando um Playground Local com Streamlit

````
6.2.1. O Agno facilita a criação de uma interface de playground com Streamlit para testar múltiplos agentes.
6.2.2. **Exemplo de Código: `playground.py`**
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground # Componente de UI do Streamlit
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Define um arquivo de banco de dados para armazenamento
agent_storage: str = "tmp/agents.db"

# Cria um Agente de Pesquisa Web
web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources"],
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    add_history_to_messages=True, # Habilita o histórico da conversa
    num_history_responses=5,
    markdown=True,
)

# Cria um Agente Financeiro
finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True)],
    instructions=["Always use tables to display data"],
    storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

# Cria a aplicação do Playground com a lista de agentes
playground_app = Playground(agents=[web_agent, finance_agent])
app = playground_app.get_app() # Obtém a aplicação FastAPI/Starlette

# Bloco para servir a aplicação
if __name__ == "__main__":
    # Executa a aplicação com recarregamento automático
    playground_app.serve("playground:app", reload=True)
```
6.2.3. **Para executar este Playground:**
```bash
python playground.py
```
Isto iniciará um servidor local com uma interface Streamlit onde você pode selecionar e interagir com o "Web Agent" ou o "Finance Agent".
````

### **7. Monitoramento e Depuração**

#### 7.1. Monitoramento em Tempo Real

````
7.1.1. O Agno permite o monitoramento de agentes em tempo real através do serviço `app.agno.com`.
7.1.2. **Habilitar por Agente:**
```python
agent = Agent(..., monitoring=True)
```
7.1.3. **Habilitar Globalmente (via variável de ambiente):**
```bash
export AGNO_MONITOR=true
```
````

#### 7.2. Logs de Depuração

````
7.2.1. Para entender o que um agente está fazendo internamente (prompt do sistema, mensagens do usuário, chamadas de ferramentas), ative o modo de depuração.
7.2.2. **Habilitar por Agente:**
```python
agent = Agent(..., debug_mode=True)
```
7.2.3. **Habilitar Globalmente (via variável de ambiente):**
```bash
export AGNO_DEBUG=true
```
````

### **8. Contribuições para o Projeto**

#### 8.1. Fluxo de Trabalho

```
8.1.1. O Agno é um projeto de código aberto e contribuições são bem-vindas. O processo segue o fluxo padrão de "fork" e "pull request" do GitHub.
    8.1.1.1. Faça um "fork" do repositório oficial.
    8.1.1.2. Crie um "branch" para sua nova feature (`git checkout -b minha-feature`).
    8.1.1.3. Implemente sua feature ou correção.
    8.1.1.4. Faça o commit de suas mudanças (`git commit -am 'Adiciona nova feature'`).
    8.1.1.5. Faça o "push" para o seu "branch" (`git push origin minha-feature`).
    8.1.1.6. Crie um novo "Pull Request" a partir do seu "fork".
```