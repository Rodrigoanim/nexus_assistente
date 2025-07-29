# Assessment DISC - Assistente NEXUS
# Função: Assistente com conhecimento do manual NEXUS para ajudar usuários
# Data: 06/06/2025

import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.storage.sqlite import SqliteStorage

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Assistente NEXUS - Manual",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar se as chaves API estão configuradas
def check_api_keys():
    """Verifica se as chaves API estão configuradas"""
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        st.error("❌ Chave API do OpenAI não configurada!")
        st.info("Configure a variável OPENAI_API_KEY no Render.com ou no arquivo .env")
        return False
    
    return True

def clean_message_content(content):
    """Limpa o conteúdo da mensagem removendo HTML não desejado"""
    import re
    import html
    
    # Debug: mostrar conteúdo original
    print(f"# Debug - Conteúdo original: {content[:200]}...")
    
    # Decodificar entidades HTML
    content = html.unescape(content)
    
    # Remover tags HTML de forma mais agressiva
    content = re.sub(r'<[^>]*>', '', content)
    
    # Remover entidades HTML restantes
    content = re.sub(r'&[a-zA-Z0-9#]+;', '', content)
    
    # Remover caracteres especiais de formatação
    content = re.sub(r'```[^`]*```', '', content)  # Remove blocos de código
    content = re.sub(r'`[^`]*`', '', content)      # Remove código inline
    
    # Limpar espaços extras e quebras de linha
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\n+', '\n', content)
    content = content.strip()
    
    # Debug: mostrar conteúdo limpo
    print(f"# Debug - Conteúdo limpo: {content[:200]}...")
    
    return content

# Inicializar base de conhecimento do NEXUS
@st.cache_resource
def initialize_nexus_knowledge():
    """Inicializa a base de conhecimento do manual NEXUS"""
    try:
        # Configurar banco de dados vetorial
        vector_db = ChromaDb(
            collection="nexus_manual", 
            path="tmp/nexus_chromadb", 
            persistent_client=True
        )
        
        # Configurar base de conhecimento com o manual NEXUS
        knowledge = TextKnowledgeBase(
            path="Manual_Geral_Nexus_2021_formatado.md",
            vector_db=vector_db
        )
        
        return knowledge
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar base de conhecimento: {str(e)}")
        return None

# Inicializar agente NEXUS
@st.cache_resource
def initialize_nexus_agent():
    """Inicializa o agente NEXUS com conhecimento do manual"""
    try:
        # Obter base de conhecimento
        knowledge = initialize_nexus_knowledge()
        
        if knowledge is None:
            return None
        
        # Configurar armazenamento
        db = SqliteStorage(
            table_name="nexus_assistant_session", 
            db_file="tmp/nexus_assistant.db"
        )
        
        # Criar agente NEXUS
        nexus_agent = Agent(
            name="Assistente NEXUS",
            model=OpenAIChat(id='gpt-4o-mini'),
            storage=db,
            knowledge=knowledge,
            instructions=[
                "Você é um assistente especializado no manual do NEXUS - Fábrica de Negócios.",
                "Seu objetivo é ajudar usuários a entenderem o funcionamento, regras e metodologia do NEXUS.",
                "SEMPRE responda em português brasileiro.",
                "Use o conhecimento do manual para fornecer respostas precisas e detalhadas.",
                "Seja educado e profissional em suas respostas.",
                "Foque em ajudar o usuário a entender melhor o NEXUS e suas práticas.",
                "IMPORTANTE: NUNCA use HTML, markdown ou formatação especial em suas respostas.",
                "Responda apenas com texto simples e claro, sem tags ou códigos."
            ],
            description="Assistente especializado no manual do NEXUS para ajudar membros e interessados",
            add_history_to_messages=True,
            search_knowledge=True,
            num_history_runs=5,
            # debug_mode=True
        )
        
        return nexus_agent
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar agente NEXUS: {str(e)}")
        return None

# Interface principal
def main():
    st.markdown("""
        <p style='
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            color: #1f77b4;
        '>📚 Assistente NEXUS - Manual</p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <p style='
            text-align: center;
            font-size: 18px;
            color: #666;
        '>Assistente especializado no manual do NEXUS - Fábrica de Negócios</p>
    """, unsafe_allow_html=True)
    
    # Verificar chaves API
    if not check_api_keys():
        st.stop()
    
    # Inicializar agente
    with st.spinner("🔄 Inicializando assistente NEXUS..."):
        agent = initialize_nexus_agent()
    
    if agent is None:
        st.error("❌ Não foi possível inicializar o assistente. Verifique as configurações.")
        st.stop()
    
    st.success("✅ Assistente NEXUS inicializado com sucesso!")
    
    # Opção para recarregar base de conhecimento
    if st.button("🔄 Recarregar Base de Conhecimento"):
        with st.spinner("🔄 Recarregando base de conhecimento..."):
            try:
                knowledge = initialize_nexus_knowledge()
                if knowledge:
                    knowledge.load(recreate=True)
                    st.success("✅ Base de conhecimento recarregada com sucesso!")
                else:
                    st.error("❌ Erro ao recarregar base de conhecimento")
            except Exception as e:
                st.error(f"❌ Erro ao recarregar: {str(e)}")
    
    # Interface de chat estilo WhatsApp com scroll
    st.markdown("---")
    st.markdown("### 💬 Chat com Assistente NEXUS")
    
    # Inicializar histórico de chat na sessão
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Container principal do chat com altura fixa e scroll
    chat_container = st.container()
    
    with chat_container:
        # Container de chat com altura fixa e scroll usando st.container
        with st.container(height=400):
            # Exibir histórico de mensagens usando componentes nativos
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.container():
                        st.markdown("""
                        <div style='background-color:#e3f2fd;padding:12px;margin:10px 0;border-left:4px solid #2196f3;border-radius:5px;'>
                            <strong>👤 Você:</strong><br>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(message["content"])
                else:
                    with st.container():
                        st.markdown("""
                        <div style='background-color:#f5f5f5;padding:12px;margin:10px 0;border-left:4px solid #4caf50;border-radius:5px;'>
                            <strong>🤖 Assistente NEXUS:</strong><br>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(message["content"])
    
    # Área de entrada fixa no rodapé
    st.markdown("---")
    st.markdown("### 💬 Enviar Mensagem")
    
    # Formulário para entrada de mensagem
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Digite sua pergunta sobre o NEXUS:",
                height=60,
                placeholder="Ex: Como funciona o sistema de pontuação? / Quais são os requisitos para ser membro? / Como funcionam as RDNs?",
                key="user_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            send_button = st.form_submit_button("📤 Enviar", type="primary", use_container_width=True)
    
    # Processar envio de mensagem
    if send_button and user_input.strip():
        # Adicionar mensagem do usuário ao histórico
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip()
        })
        
        # Processar resposta do assistente
        with st.spinner("🔄 Assistente NEXUS está digitando..."):
            try:
                # Obter resposta do agente
                response = agent.run(user_input.strip(), stream=False)
                
                # Debug: mostrar resposta original
                print(f"# Debug - Resposta original do agente: {response.content[:300]}...")
                
                # Limpar conteúdo da resposta
                content = clean_message_content(response.content)
                
                # Verificação final: remover qualquer HTML restante
                import re
                if re.search(r'<[^>]+>', content):
                    print(f"# Debug - HTML ainda encontrado, limpando novamente...")
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'&[a-zA-Z0-9#]+;', '', content)
                
                # Adicionar resposta do assistente ao histórico
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": content
                })
                
                # Forçar atualização da interface
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao processar pergunta: {str(e)}")
    
    elif send_button and not user_input.strip():
        st.warning("⚠️ Por favor, digite uma pergunta.")
    
    # Botão para limpar histórico
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Exemplos de perguntas
    st.markdown("---")
    st.markdown("### 💡 Exemplos de Perguntas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color:#f0f0f0;padding:10px;border-radius:5px;'>
            <h4>📋 Sobre Membros</h4>
            <ul>
                <li>Quais são os requisitos para ser membro?</li>
                <li>Como funciona o sistema de pontuação?</li>
                <li>Quais são as regras de exclusividade?</li>
                <li>Como funciona a suspensão de cadeira?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color:#f0f0f0;padding:10px;border-radius:5px;'>
            <h4>🤝 Sobre Contribuições</h4>
            <ul>
                <li>Como funcionam as RDNs?</li>
                <li>Como registrar indicações de negócios?</li>
                <li>Como funciona o sistema de convidados?</li>
                <li>Como registrar negócios fechados?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Informações sobre o NEXUS
    st.markdown("---")
    st.markdown("### ℹ️ Sobre o NEXUS")
    
    st.info("""
    **NEXUS - Fábrica de Negócios** é uma comunidade de networking empresarial que:
    - Reúne empresários para gerar negócios
    - Utiliza metodologia estruturada de contribuições
    - Promove networking qualificado
    - Oferece ambiente de conhecimento e crescimento
    """)
    
    # Informações do sistema
    st.markdown("---")
    st.markdown("### ℹ️ Informações do Sistema")
    
    env = os.getenv('ENVIRONMENT', 'development')
    debug = os.getenv('DEBUG', 'False')
    
    st.info(f"""
    - **Ambiente**: {env}
    - **Debug**: {debug}
    - **Modelo**: GPT-4o-mini (OpenAI)
    - **Versão**: Assistente NEXUS v1.0
    - **Base de Conhecimento**: Manual NEXUS 2021
    """)

if __name__ == "__main__":
    main() 