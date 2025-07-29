# Assessment DISC - Assistente NEXUS
# Função: Assistente com conhecimento do manual NEXUS para ajudar usuários
# Data: 06/06/2025

import os
import shutil
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase, TextReader
import re
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

def search_manual_hybrid(query, manual_path="Manual_Geral_Nexus_2021_formatado.md"):
    """
    Busca híbrida: combina busca textual direta + busca semântica
    """
    results = []
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Termos relacionados a pontuação
        pontuacao_terms = [
            'pontos', 'pontuação', 'indexadores', 'performance', 'contribuições',
            'ausência', 'faltar', 'presença', 'RDN', 'convidados', 'negócios fechados',
            'tabela de indexadores', 'sistema de pontuação', 'cores', 'preto', 'vermelho',
            'amarelo', 'azul', 'verde', '5 pontos', '10 pontos', '15 pontos', '20 pontos'
        ]
        
        # Buscar termos relacionados na query
        query_lower = query.lower()
        relevant_terms = [term for term in pontuacao_terms if term in query_lower]
        
        # Se encontrou termos de pontuação, buscar seções específicas
        if any(term in query_lower for term in ['pontos', 'pontuação', 'indexadores', 'performance']):
            # Buscar seção da Tabela de Indexadores
            tabela_match = re.search(r'\*\* Tabela de Indexadores \*\*.*?(?=\n---|\n# |\nPAGE|\Z)', content, re.DOTALL | re.IGNORECASE)
            if tabela_match:
                results.append({
                    'content': tabela_match.group(0),
                    'source': 'Tabela de Indexadores',
                    'relevance': 0.95
                })
            
            # Buscar sistema de pontuação por cores
            cores_match = re.search(r'\*\* Sistema de pontuação por cores \*\*.*?(?=\n---|\n# |\nPAGE|\Z)', content, re.DOTALL | re.IGNORECASE)
            if cores_match:
                results.append({
                    'content': cores_match.group(0),
                    'source': 'Sistema de Cores',
                    'relevance': 0.90
                })
            
            # Buscar contribuições específicas
            contrib_match = re.search(r'10\. Contribuições.*?(?=\n11\.|\n---|\nPAGE|\Z)', content, re.DOTALL | re.IGNORECASE)
            if contrib_match:
                results.append({
                    'content': contrib_match.group(0),
                    'source': 'Seção Contribuições',
                    'relevance': 0.85
                })
        
        # Busca textual para termos específicos
        for term in relevant_terms:
            pattern = rf'.{{0,200}}{re.escape(term)}.{{0,200}}'
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                snippet = match.group(0).strip()
                if len(snippet) > 50:  # Filtrar snippets muito pequenos
                    results.append({
                        'content': snippet,
                        'source': f'Busca por "{term}"',
                        'relevance': 0.75
                    })
        
        # Remover duplicatas e ordenar por relevância
        unique_results = []
        seen_content = set()
        for result in sorted(results, key=lambda x: x['relevance'], reverse=True):
            content_key = result['content'][:100]  # Usar primeiros 100 chars como chave
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
                if len(unique_results) >= 5:  # Limitar a 5 resultados
                    break
        
        return unique_results
        
    except Exception as e:
        print(f"# Debug - Erro na busca híbrida: {str(e)}")
        return []

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

def search_nexus_manual(query: str) -> str:
    """
    Busca informações específicas no manual NEXUS usando busca híbrida.
    Ideal para encontrar informações sobre pontuação, regras e procedimentos.
    """
    print(f"# Debug - Busca híbrida executada para: {query}")
    
    # Usar busca híbrida
    results = search_manual_hybrid(query)
    
    if not results:
        return "Não encontrei informações específicas sobre sua consulta no manual NEXUS."
    
    # Montar resposta com os melhores resultados
    response_parts = []
    for i, result in enumerate(results[:3]):  # Top 3 resultados
        response_parts.append(f"**{result['source']}:**\n{result['content'][:800]}...")
        
    response = "\n\n".join(response_parts)
    print(f"# Debug - Busca híbrida encontrou {len(results)} resultados")
    return response

# A função search_nexus_manual será usada diretamente pelo agente através das instruções

# Inicializar base de conhecimento do NEXUS
def initialize_nexus_knowledge():
    """Inicializa a base de conhecimento do manual NEXUS de forma automática e robusta"""
    try:
        # Garantir que diretório tmp existe
        os.makedirs("tmp", exist_ok=True)
        
        # Verificar se o arquivo do manual existe
        manual_path = "Manual_Geral_Nexus_2021_formatado.md"
        if not os.path.exists(manual_path):
            st.error(f"❌ Arquivo do manual não encontrado: {manual_path}")
            return None
        
        # Debug: informações sobre o arquivo
        file_size = os.path.getsize(manual_path)
        print(f"# Debug - Arquivo manual: {manual_path}")
        print(f"# Debug - Tamanho do arquivo: {file_size} bytes")
        
        # Verificar se o arquivo pode ser lido
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"# Debug - Arquivo lido com sucesso: {len(content)} caracteres")
                print(f"# Debug - Primeiros 200 caracteres: {content[:200]}...")
        except Exception as read_e:
            print(f"# Debug - Erro ao ler arquivo: {str(read_e)}")
            st.error(f"❌ Erro ao ler arquivo do manual: {str(read_e)}")
            return None
        
        # Garantir que a base seja criada limpa sempre
        chroma_path = "tmp/nexus_chromadb"
        if os.path.exists(chroma_path):
            try:
                shutil.rmtree(chroma_path)
                print(f"# Debug - Diretório ChromaDB antigo removido")
            except Exception as remove_e:
                print(f"# Debug - Aviso: Não foi possível remover diretório antigo: {str(remove_e)}")
        
        # Configurar banco de dados vetorial sempre limpo
        vector_db = ChromaDb(
            collection="nexus_manual_auto", 
            path=chroma_path
        )
        
        # Configurar leitor de texto com configurações otimizadas
        text_reader = TextReader(
            chunk=True,
            chunk_size=1500,  # Tamanho otimizado
            separators=["\n\n", "\n", ". ", " "]  # Separadores hierárquicos
        )
        
        # Configurar base de conhecimento com o manual NEXUS
        knowledge = TextKnowledgeBase(
            path=manual_path,
            vector_db=vector_db,
            reader=text_reader
        )
        
        # Forçar carregamento da base de conhecimento sempre limpa
        print(f"# Debug - Carregando base de conhecimento (sempre nova)...")
        knowledge.load(recreate=True)
        print(f"# Debug - Base de conhecimento carregada com sucesso!")
        
        # Verificar se documentos foram criados com timeout
        try:
            import time
            time.sleep(1)  # Aguardar processamento
            test_docs = vector_db.search("NEXUS", limit=3)
            doc_count = len(test_docs) if test_docs else 0
            print(f"# Debug - Teste de busca encontrou: {doc_count} documentos")
            
            if doc_count == 0:
                print(f"# Debug - Nenhum documento encontrado, tentando busca alternativa...")
                # Tentar busca por termos diferentes
                test_docs2 = vector_db.search("pontuação", limit=3)
                doc_count2 = len(test_docs2) if test_docs2 else 0
                print(f"# Debug - Busca alternativa encontrou: {doc_count2} documentos")
                
        except Exception as search_e:
            print(f"# Debug - Erro ao testar busca: {str(search_e)}")
        
        return knowledge
        
    except Exception as e:
        print(f"# Debug - Erro geral ao inicializar base: {str(e)}")
        st.error(f"❌ Erro ao inicializar base de conhecimento: {str(e)}")
        return None

# Inicializar agente NEXUS
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
                "SEMPRE busque informações na base de conhecimento antes de responder.",
                "Use APENAS informações do manual NEXUS para suas respostas.",
                "Se não encontrar informações específicas, diga claramente que não encontrou.",
                "Seja preciso e cite as seções ou páginas do manual quando possível.",
                "Forneça respostas detalhadas usando as informações exatas do manual.",
                "Seja educado e profissional em suas respostas.",
                "Foque em ajudar o usuário a entender melhor o NEXUS e suas práticas.",
                "IMPORTANTE: NUNCA use HTML, markdown ou formatação especial em suas respostas.",
                "Responda apenas com texto simples e claro, sem tags ou códigos.",
                "Quando perguntado sobre regras específicas, sempre consulte o manual completo."
            ],
            description="Assistente especializado no manual do NEXUS para ajudar membros e interessados",
            add_history_to_messages=True,
            search_knowledge=True,
            num_history_runs=3,
            debug_mode=True
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
    
    # Inicializar agente sempre novo para garantir funcionamento
    with st.spinner("🔄 Inicializando assistente NEXUS..."):
        # Sempre inicializar novo agente para garantir base atualizada
        if "nexus_agent" not in st.session_state or st.session_state.get("force_reload", False):
            print("# Debug - Inicializando novo agente...")
            st.session_state.nexus_agent = initialize_nexus_agent()
            st.session_state.force_reload = False
        agent = st.session_state.nexus_agent
    
    if agent is None:
        st.error("❌ Não foi possível inicializar o assistente. Verifique as configurações.")
        st.stop()
    
    # Verificação automática da base de conhecimento
    auto_check_status = "🔄 Verificando"
    try:
        # Testar se a base está funcionando
        if hasattr(agent, 'knowledge') and agent.knowledge:
            # Teste simples da busca híbrida
            test_results = search_manual_hybrid("pontuação")
            if test_results:
                auto_check_status = "✅ Base funcionando"
                print(f"# Debug - Verificação automática: {len(test_results)} resultados encontrados")
            else:
                auto_check_status = "⚠️ Base vazia"
                print(f"# Debug - Verificação automática: nenhum resultado encontrado")
        else:
            auto_check_status = "❌ Base não carregada"
            print(f"# Debug - Verificação automática: base de conhecimento não carregada")
    except Exception as check_e:
        auto_check_status = "❌ Erro na verificação"
        print(f"# Debug - Erro na verificação automática: {str(check_e)}")
    
    st.success(f"✅ Assistente NEXUS inicializado com sucesso! ({auto_check_status})")
    
    # Opções de administração simplificadas (apenas para emergência)
    with st.expander("🔧 Opções Avançadas (apenas se necessário)"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Forçar Reinicialização"):
                with st.spinner("🔄 Forçando reinicialização completa..."):
                    try:
                        # Limpar completamente a sessão
                        if "nexus_agent" in st.session_state:
                            del st.session_state.nexus_agent
                        if "chat_history" in st.session_state:
                            del st.session_state.chat_history
                        
                        # Marcar para recarregar
                        st.session_state.force_reload = True
                        
                        st.success("✅ Reinicialização forçada. Recarregando...")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao reinicializar: {str(e)}")
        
        with col2:
            if st.button("🔍 Teste Busca Híbrida"):
                with st.spinner("🔍 Testando busca híbrida..."):
                    try:
                        # Testar busca híbrida diretamente
                        test_query = "sistema de pontuação"
                        results = search_manual_hybrid(test_query)
                        
                        if results:
                            st.success(f"✅ Busca híbrida encontrou {len(results)} resultados")
                            for i, result in enumerate(results[:2]):
                                st.text(f"Fonte: {result['source']}")
                                st.text(f"Relevância: {result['relevance']}")
                                st.text(f"Conteúdo: {result['content'][:150]}...")
                                st.divider()
                        else:
                            st.warning("⚠️ Busca híbrida não encontrou resultados")
                            
                    except Exception as e:
                        st.error(f"❌ Erro na busca híbrida: {str(e)}")
                        print(f"# Debug - Erro na busca híbrida: {str(e)}")
    
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
                # Primeiro, tentar busca híbrida para perguntas sobre pontuação
                hybrid_results = None
                query_lower = user_input.strip().lower()
                
                # Verificar se é uma pergunta sobre pontuação/sistema
                if any(term in query_lower for term in ['pontos', 'pontuação', 'indexadores', 'performance', 'contribuições', 'sistema', 'faltar', 'ausência']):
                    print(f"# Debug - Detectada pergunta sobre pontuação, usando busca híbrida...")
                    hybrid_results = search_manual_hybrid(user_input.strip())
                    print(f"# Debug - Busca híbrida encontrou {len(hybrid_results) if hybrid_results else 0} resultados")
                
                # Se a busca híbrida encontrou resultados, usar eles
                if hybrid_results:
                    print(f"# Debug - Usando resultados da busca híbrida")
                    response_parts = []
                    for result in hybrid_results[:2]:  # Top 2 resultados
                        response_parts.append(f"Baseado na {result['source']}:\n\n{result['content'][:600]}")
                    
                    content = "\n\n---\n\n".join(response_parts)
                    content += "\n\nEssas informações foram extraídas diretamente do manual NEXUS."
                    
                else:
                    # Usar agente normal se não for sobre pontuação ou busca híbrida falhou
                    print(f"# Debug - Usando agente normal...")
                    response = agent.run(user_input.strip(), stream=False)
                    
                    # Debug: mostrar resposta original
                    print(f"# Debug - Resposta original do agente: {response.content[:300]}...")
                    
                    # Limpar conteúdo da resposta
                    content = clean_message_content(response.content)
                    
                    # Verificação final: remover qualquer HTML restante
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
        st.info("""
        **📋 Sobre Membros**
        
        - Quais são os requisitos para ser membro?
        - Como funciona o sistema de pontuação?
        - Quais são as regras de exclusividade?
        - Como funciona a suspensão de cadeira?
        """)
    
    with col2:
        st.info("""
        **🤝 Sobre Contribuições**
        
        - Como funcionam as RDNs?
        - Como registrar indicações de negócios?
        - Como funciona o sistema de convidados?
        - Como registrar negócios fechados?
        """)
    
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