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

def search_manual_comprehensive(query, manual_path="Manual_Geral_Nexus_2021_formatado.md"):
    """
    Busca abrangente e precisa: busca em todo o manual com máxima precisão e completude
    """
    results = []
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        query_lower = query.lower()
        
        # 1. BUSCA POR SEÇÕES ESPECÍFICAS COMPLETAS
        section_patterns = {
            # Seções introdutórias completas
            'O que é NEXUS': r'1\. O NEXUS.*?(?=\n1\. Requisitos para entrada no NEXUS|\nVai se formando assim|\Z)',
            'Introdução Completa': r'SEJA BEM-VINDO AO NEXUS.*?(?=\n1\. Requisitos para entrada no NEXUS|\Z)',
            'Filosofia e Networking': r'O NEXUS FN é mais que um grupo de networking\..*?(?=\n</PAGE|\nVai se formando|\Z)',
            
            # Sistema de pontuação completo
            'Tabela de Indexadores Completa': r'\*\* Tabela de Indexadores \*\*.*?(?=\n\*\* Sistema de pontuação por cores|\n## Exemplo Geral|\nPAGE|\Z)',
            'Sistema de Cores Completo': r'\*\* Sistema de pontuação por cores \*\*.*?(?=\n</PAGE|\nPAGE|\Z)',
            'Exemplo de Pontuação': r'## Exemplo Geral do uso da Tabela.*?(?=\n## Importância|\nPAGE|\Z)',
            'Importância das Contribuições': r'## Importância das Contribuições.*?(?=\n</PAGE|\nPAGE|\Z)',
            
            # Seções de regras e procedimentos
            'Requisitos Entrada Completo': r'1\. Requisitos para entrada no NEXUS.*?(?=\n2\. Taxas e mensalidades|\Z)',
            'Taxas e Mensalidades Completo': r'2\. Taxas e mensalidades.*?(?=\n3\. Solicitação|\n</PAGE|\Z)',
            'Suspensão de Cadeira': r'3\. Solicitação de suspensão da cadeira.*?(?=\n4\. Fatores|\n</PAGE|\Z)',
            'Exclusão Automática': r'4\. Fatores de suspensão/exclusão automática.*?(?=\n5\. Sobre|\n</PAGE|\Z)',
            'Exclusividade Completa': r'5\. Sobre a exclusividade.*?(?=\n6\. Introdução|\n</PAGE|\Z)',
            'Introdução Novo Membro': r'6\. Introdução – Após ingresso.*?(?=\n7\. Sua 1ª|\n</PAGE|\Z)',
            'Primeira Semana': r'7\. Sua 1ª\. semana no NEXUS.*?(?=\n8\. Sua primeira|\n</PAGE|\Z)',
            'Primeira Reunião': r'8\. Sua primeira reunião oficial.*?(?=\n9\. Regras|\n</PAGE|\Z)',
            
            # Regras básicas completas
            'Regras Básicas Completas': r'9\. Regras Básicas.*?(?=\n10\. Contribuições|\Z)',
            'Horários Detalhados': r'A\. Horários.*?(?=\nB\. Sobre horário|\n</PAGE|\Z)',
            'Faltas e Atrasos': r'B\. Sobre horário de chegada.*?(?=\nC\. Sistema de avaliação|\n</PAGE|\Z)',
            'Sistema Performance': r'C\. Sistema de avaliação de performance.*?(?=\n10\. Contribuições|\n</PAGE|\Z)',
            
            # Contribuições detalhadas
            'Contribuições Completas': r'10\. Contribuições.*?(?=\nA\. Convidados|\Z)',
            'Convidados e Novos Membros': r'A\. Convidados e Novos Membros.*?(?=\nB\. RDNs|\n</PAGE|\Z)',
            'RDNs Detalhadas': r'B\. RDNs – Reuniões de Negócios.*?(?=\nC\. Indicações|\n</PAGE|\Z)',
            'Indicações Completas': r'C\. Indicações de Negócios.*?(?=\nD\. Negócios|\n</PAGE|\Z)',
            'Negócios Fechados Completo': r'D\. Negócios Fechados.*?(?=\nE\. Convidado que vira|\n</PAGE|\Z)',
            'Conversão de Membros': r'E\. Convidado que vira membro.*?(?=\nF\. Ausência|\n</PAGE|\Z)',
            'Ausência e Presença': r'F\. Ausência.*?(?=\nG\. Outras Formas|\n</PAGE|\Z)',
            'Outras Contribuições': r'G\. Outras Formas de Contribuir.*?(?=\n11\. Liderança|\n</PAGE|\Z)',
            
            # Liderança completa
            'Liderança Completa': r'11\. Liderança e Suas Funções.*?(?=\nDinâmica das Reuniões|\n</PAGE|\Z)',
            'Presidente Função': r'• Presidente:.*?(?=\n• Vice-Presidente|\n</PAGE|\Z)',
            'VP Crescimento': r'• Vice-Presidente de Crescimento:.*?(?=\n• Vice-Presidente de Conhecimento|\n</PAGE|\Z)',
            'VP Conhecimento': r'• Vice-Presidente de Conhecimento:.*?(?=\n• Recepção|\n</PAGE|\Z)',
            'Recepção Função': r'• Recepção:.*?(?=\n• Mentoria|\n</PAGE|\Z)',
            'Mentoria Função': r'• Mentoria:.*?(?=\n• Marketing|\n</PAGE|\Z)',
            
            # Dinâmica das reuniões
            'Dinâmica Reuniões': r'Dinâmica das Reuniões.*?(?=\nTempos da Apresentação|\n</PAGE|\Z)',
            'Tempos Apresentação': r'Tempos da Apresentação.*?(?=\nRespeite o tempo|\n</PAGE|\Z)',
            'Dicas Apresentação': r'DICAS para uma boa apresentação.*?(?=\nApresentação de Convidado|\n</PAGE|\Z)',
            'Apresentação Convidados': r'Apresentação de Convidado.*?(?=\nRodada de Performance|\n</PAGE|\Z)',
            'Rodada Performance': r'Rodada de Performance.*?(?=\nFuncionamento interno|\n</PAGE|\Z)',
            
            # Dicas e boas práticas
            'Dicas de Ouro Completas': r'Dicas de Ouro NEXUS.*?(?=\nAS REGRAS PARA BOA CONVIVÊNCIA|\n</PAGE|\Z)',
            'Visibilidade Importância': r'O porquê da VISIBILIDADE.*?(?=\nComo construir sua VISIBILIDADE|\n</PAGE|\Z)',
            'Como Construir Visibilidade': r'Como construir sua VISIBILIDADE.*?(?=\nPorque CREDIBILIDADE|\n</PAGE|\Z)',
            'Credibilidade Importância': r'Porque CREDIBILIDADE é importante.*?(?=\nComo construir CREDIBILIDADE|\n</PAGE|\Z)',
            'Como Construir Credibilidade': r'Como construir CREDIBILIDADE.*?(?=\nAS REGRAS PARA BOA CONVIVÊNCIA|\n</PAGE|\Z)',
            
            # Convivência e conflitos
            'Conflitos no Grupo': r'A\. Conflitos no grupo.*?(?=\nB\. Erros Comuns|\n</PAGE|\Z)',
            'Erros Comuns': r'B\. Erros Comuns a Evitar.*?(?=\nC\. Assuntos Proibidos|\n</PAGE|\Z)',
            'Assuntos Proibidos': r'C\. Assuntos Proibidos.*?(?=\nD\. Dicas de Boas|\n</PAGE|\Z)',
            'Boas Práticas Convivência': r'D\. Dicas de Boas Práticas.*?(?=\nE POR FIM|\n</PAGE|\Z)',
        }
        
        # Buscar seções específicas que podem ser relevantes
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(0)
                # Verificar se a query tem relação com esta seção
                relevance_score = calculate_relevance(query_lower, section_content.lower(), section_name.lower())
                if relevance_score > 0.2:  # Relevância mínima mais baixa para capturar mais conteúdo
                    results.append({
                        'content': section_content,
                        'source': f'Manual NEXUS - {section_name}',
                        'relevance': relevance_score
                    })
        
        # 2. BUSCA CONTEXTUAL INTELIGENTE (respeitando limites de palavras)
        query_words = [word.strip() for word in re.split(r'[^\w]+', query_lower) if len(word.strip()) > 2]
        
        if len(query_words) > 0:
            for word in query_words:
                # Buscar a palavra no texto
                word_pattern = rf'\b{re.escape(word)}\b'
                word_matches = re.finditer(word_pattern, content, re.IGNORECASE)
                
                for word_match in word_matches:
                    word_start = word_match.start()
                    word_end = word_match.end()
                    
                    # Expandir para capturar contexto respeitando limites de palavras
                    # Buscar início de frase/parágrafo (até 800 chars antes)
                    context_start = max(0, word_start - 800)
                    text_before = content[context_start:word_start]
                    
                    # Encontrar último início de frase antes da palavra
                    sentence_starts = [m.end() for m in re.finditer(r'[.!?]\s+|^\s*', text_before)]
                    if sentence_starts:
                        actual_start = context_start + sentence_starts[-1]
                    else:
                        # Se não encontrar início de frase, buscar início de palavra
                        word_boundary = re.search(r'\b\w', text_before[::-1])
                        if word_boundary:
                            actual_start = word_start - word_boundary.start()
                        else:
                            actual_start = context_start
                    
                    # Buscar fim de frase/parágrafo (até 800 chars depois)
                    context_end = min(len(content), word_end + 800)
                    text_after = content[word_end:context_end]
                    
                    # Encontrar primeiro fim de frase depois da palavra
                    sentence_end = re.search(r'[.!?]\s+|\n\n', text_after)
                    if sentence_end:
                        actual_end = word_end + sentence_end.end()
                    else:
                        # Se não encontrar fim de frase, buscar fim de palavra
                        word_boundary = re.search(r'\w\b', text_after)
                        if word_boundary:
                            actual_end = word_end + word_boundary.end()
                        else:
                            actual_end = context_end
                    
                    # Extrair snippet completo
                    snippet = content[actual_start:actual_end].strip()
                    
                    if len(snippet) > 100:  # Apenas snippets substanciais
                        relevance = calculate_text_relevance(query_lower, snippet.lower())
                        if relevance > 0.3:
                            # Limpar snippet para garantir que não há cortes no meio de palavras
                            snippet_clean = clean_snippet(snippet)
                            results.append({
                                'content': snippet_clean,
                                'source': f'Contexto inteligente para "{word}"',
                                'relevance': relevance
                            })
        
        # 3. BUSCA POR PARÁGRAFOS COMPLETOS
        paragraphs = re.split(r'\n\n+', content)
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 100:  # Apenas parágrafos substanciais
                relevance = calculate_text_relevance(query_lower, paragraph.lower())
                if relevance > 0.5:  # Alta relevância para parágrafos
                    results.append({
                        'content': paragraph.strip(),
                        'source': f'Parágrafo relevante #{i+1}',
                        'relevance': relevance
                    })
        
        # Remover duplicatas e ordenar por relevância
        unique_results = []
        seen_content = set()
        for result in sorted(results, key=lambda x: x['relevance'], reverse=True):
            content_key = result['content'][:200]  # Usar primeiros 200 chars como chave
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
                if len(unique_results) >= 6:  # Limitar a 6 resultados de alta qualidade
                    break
        
        return unique_results
        
    except Exception as e:
        print(f"# Debug - Erro na busca abrangente: {str(e)}")
        return []

def clean_snippet(snippet):
    """Limpa snippet para garantir que não há palavras cortadas"""
    if not snippet or len(snippet) < 10:
        return snippet
    
    # Remover caracteres de controle e limpar espaços
    snippet = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', snippet)
    snippet = snippet.strip()
    
    # Se o snippet não começa com letra maiúscula ou número, 
    # tentar encontrar o início de uma palavra ou frase
    if snippet and not re.match(r'^[A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ0-9]', snippet):
        # Buscar primeiro início de palavra válido
        first_word = re.search(r'\b[A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ0-9]', snippet)
        if first_word:
            snippet = snippet[first_word.start():]
    
    # Se o snippet não termina com pontuação adequada,
    # tentar encontrar uma terminação natural
    if snippet and not re.search(r'[.!?:;]\s*$', snippet):
        # Buscar último fim de frase/palavra válido
        last_punct = None
        for match in re.finditer(r'[.!?:;]\s*', snippet):
            last_punct = match
        
        if last_punct:
            snippet = snippet[:last_punct.end()].strip()
        else:
            # Se não encontrar pontuação, terminar em fim de palavra
            words = snippet.split()
            if len(words) > 1:
                # Remover última palavra se pode estar incompleta
                snippet = ' '.join(words[:-1]) + '.'
    
    # Limpar espaços extras e quebras de linha desnecessárias
    snippet = re.sub(r'\s+', ' ', snippet)
    snippet = re.sub(r'\n\s*\n', '\n\n', snippet)
    
    return snippet.strip()

def calculate_relevance(query, text, section_name=""):
    """Calcula relevância baseada em correspondências de palavras"""
    query_words = set(re.split(r'[^\w]+', query.lower()))
    text_words = set(re.split(r'[^\w]+', text.lower()))
    section_words = set(re.split(r'[^\w]+', section_name.lower()))
    
    # Palavras em comum
    common_words = query_words.intersection(text_words)
    
    # Bonus para correspondência no nome da seção
    section_bonus = len(query_words.intersection(section_words)) * 0.2
    
    # BONUS ESPECIAL para perguntas introdutórias/gerais
    intro_bonus = 0.0
    query_lower = query.lower()
    
    # Detectar perguntas sobre "o que é" NEXUS
    intro_queries = [
        'o que é', 'que é', 'o que são', 'define', 'definição', 'conceito', 
        'sobre o nexus', 'sobre nexus', 'explique nexus', 'nexus é',
        'finalidade', 'propósito', 'objetivo', 'missão'
    ]
    
    is_intro_query = any(intro_term in query_lower for intro_term in intro_queries)
    
    if is_intro_query:
        intro_sections = ['o que é nexus', 'introdução nexus', 'filosofia nexus']
        if any(intro_sec in section_name.lower() for intro_sec in intro_sections):
            intro_bonus = 0.4  # Bonus alto para seções introdutórias em perguntas gerais
        elif 'tabela' in section_name.lower() or 'indexadores' in section_name.lower():
            intro_bonus = -0.3  # Penalidade para seções técnicas em perguntas gerais
    
    # Calcular score baseado na proporção de palavras encontradas
    if len(query_words) > 0:
        base_score = len(common_words) / len(query_words)
        total_score = base_score + section_bonus + intro_bonus
        return min(0.95, max(0.0, total_score))
    
    return 0.0

def calculate_text_relevance(query, text):
    """Calcula relevância para busca textual com maior precisão"""
    query_words = [w for w in re.split(r'[^\w]+', query.lower()) if len(w) > 2]
    text_lower = text.lower()
    
    if len(query_words) == 0:
        return 0.0
    
    relevance = 0.0
    total_words = len(query_words)
    
    # Pontuação base por palavra encontrada
    words_found = 0
    for word in query_words:
        count = text_lower.count(word.lower())
        if count > 0:
            words_found += 1
            # Pontuação progressiva: primeira ocorrência vale mais
            word_score = 0.2 + min(0.2, (count - 1) * 0.05)
            relevance += word_score
    
    # Bonus por densidade de palavras encontradas
    word_density = words_found / total_words
    density_bonus = word_density * 0.3
    
    # Bonus para textos que contêm múltiplas palavras próximas
    proximity_bonus = 0.0
    if len(query_words) >= 2:
        for i in range(len(query_words) - 1):
            word1 = query_words[i]
            word2 = query_words[i + 1]
            # Buscar palavras em sequência ou próximas (até 50 caracteres)
            pattern = rf'{re.escape(word1)}.{{0,50}}{re.escape(word2)}'
            if re.search(pattern, text_lower, re.IGNORECASE):
                proximity_bonus += 0.2
    
    # Bonus especial para correspondências exatas de frases
    query_phrases = [phrase.strip() for phrase in query.split(' ') if len(phrase.strip()) > 4]
    for phrase in query_phrases:
        if phrase.lower() in text_lower:
            relevance += 0.25
    
    total_relevance = relevance + density_bonus + proximity_bonus
    return min(0.95, total_relevance)

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
    Busca informações específicas no manual NEXUS usando busca abrangente.
    Ideal para encontrar informações sobre pontuação, regras e procedimentos.
    """
    print(f"# Debug - Busca abrangente executada para: {query}")
    
    # Usar busca abrangente
    results = search_manual_comprehensive(query)
    
    if not results:
        return "Não encontrei informações específicas sobre sua consulta no manual NEXUS."
    
    # Montar resposta com os melhores resultados
    response_parts = []
    for i, result in enumerate(results[:3]):  # Top 3 resultados
        response_parts.append(f"**{result['source']}:**\n{result['content'][:800]}...")
        
    response = "\n\n".join(response_parts)
    print(f"# Debug - Busca abrangente encontrou {len(results)} resultados")
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
                "Você é um assistente especializado no manual completo do NEXUS - Fábrica de Negócios.",
                "Seu objetivo é fornecer informações PRECISAS, COMPLETAS e CORRETAS sobre o funcionamento, regras e metodologia do NEXUS.",
                
                # QUALIDADE DO PORTUGUÊS
                "SEMPRE responda em português brasileiro IMPECÁVEL, utilizando gramática correta e linguagem clara.",
                "Use concordância verbal e nominal adequada, tempos verbais corretos e pontuação apropriada.",
                "Evite erros de digitação, acentuação e concordância.",
                "Utilize linguagem formal mas acessível, apropriada para contexto empresarial.",
                
                # PRECISÃO E COMPLETUDE
                "SEMPRE busque informações na base de conhecimento antes de responder.",
                "Use EXCLUSIVAMENTE informações do manual NEXUS oficial para suas respostas.",
                "Forneça respostas COMPLETAS e DETALHADAS, não resumos superficiais.",
                "Quando encontrar informação relevante, inclua TODOS os detalhes importantes, não apenas partes.",
                "Cite especificamente as seções, páginas ou partes do manual de onde as informações foram extraídas.",
                
                # CONTEÚDO DO MANUAL
                "O manual NEXUS é um documento abrangente com as seguintes seções principais:",
                "- INTRODUÇÃO: Definição, filosofia e propósito do NEXUS (páginas 1-2)",
                "- REQUISITOS: Critérios para entrada, taxas, suspensão e exclusão (páginas 2-4)",
                "- REGRAS BÁSICAS: Horários, faltas, sistema de performance (páginas 6-8)",
                "- CONTRIBUIÇÕES: Tabela de indexadores, sistema de cores, pontuação detalhada (páginas 9-9b)",
                "- ATIVIDADES: RDNs, convidados, indicações, negócios fechados (páginas 10-13)",
                "- LIDERANÇA: Funções, responsabilidades, organograma (páginas 16-22)",
                "- REUNIÕES: Dinâmica, apresentações, performance (páginas 23-26)",
                "- PROCEDIMENTOS: Entrada de novos membros, fluxogramas (páginas 27-29)",
                "- DICAS DE SUCESSO: Visibilidade, credibilidade, networking (páginas 30-32)",
                "- CONVIVÊNCIA: Conflitos, boas práticas, assuntos proibidos (páginas 33-36)",
                
                # DIRETRIZES ESPECÍFICAS
                "Para perguntas sobre 'o que é NEXUS': Use as informações introdutórias completas das páginas 1-2.",
                "Para perguntas sobre pontuação: Inclua detalhes da Tabela de Indexadores E do Sistema de Cores.",
                "Para perguntas sobre regras: Forneça informações completas, incluindo exceções e exemplos.",
                "Para perguntas sobre procedimentos: Detalhe todos os passos e responsabilidades envolvidas.",
                
                # FORMATO DAS RESPOSTAS
                "Estruture suas respostas de forma lógica e organizada.",
                "Use parágrafos bem estruturados para facilitar a leitura.",
                "Quando apropriado, use listas para enumerar itens ou passos.",
                "Sempre conclua verificando se a resposta está completa e precisa.",
                
                # LIMITAÇÕES
                "Se não encontrar informações específicas na base de conhecimento, declare explicitamente: 'Esta informação não está disponível no manual NEXUS consultado.'",
                "NUNCA invente ou suponha informações que não estejam no manual.",
                "NUNCA use HTML, markdown ou formatação especial - apenas texto simples e bem estruturado.",
                "Seja sempre profissional, educado e focado em ajudar o usuário a compreender o NEXUS completamente."
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
            # Teste simples da busca abrangente
            test_results = search_manual_comprehensive("pontuação")
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
            if st.button("🔍 Teste Busca Abrangente"):
                with st.spinner("🔍 Testando busca abrangente..."):
                    try:
                        # Testar busca abrangente diretamente
                        test_query = "sistema de pontuação"
                        results = search_manual_comprehensive(test_query)
                        
                        if results:
                            st.success(f"✅ Busca abrangente encontrou {len(results)} resultados")
                            for i, result in enumerate(results[:2]):
                                st.text(f"Fonte: {result['source']}")
                                st.text(f"Relevância: {result['relevance']:.2f}")
                                # Limpar conteúdo de teste também
                                clean_content = clean_snippet(result['content'])
                                preview = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
                                st.text(f"Conteúdo: {preview}")
                                st.divider()
                        else:
                            st.warning("⚠️ Busca abrangente não encontrou resultados")
                            
                    except Exception as e:
                        st.error(f"❌ Erro na busca abrangente: {str(e)}")
                        print(f"# Debug - Erro na busca abrangente: {str(e)}")
    
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
                # Sempre tentar busca abrangente primeiro
                print(f"# Debug - Tentando busca abrangente...")
                comprehensive_results = search_manual_comprehensive(user_input.strip())
                print(f"# Debug - Busca abrangente encontrou {len(comprehensive_results) if comprehensive_results else 0} resultados")
                
                # Estratégia de resposta mais robusta
                if comprehensive_results:
                    # Verificar se temos resultados de alta relevância
                    high_relevance_results = [r for r in comprehensive_results if r['relevance'] >= 0.5]
                    medium_relevance_results = [r for r in comprehensive_results if 0.3 <= r['relevance'] < 0.5]
                    
                    if high_relevance_results:
                        print(f"# Debug - Usando resultados de alta relevância (>= 0.5)")
                        response_parts = []
                        for result in high_relevance_results[:2]:  # Top 2 de alta relevância
                            # Limpar e truncar conteúdo de forma inteligente
                            clean_content = clean_snippet(result['content'])
                            # Truncar em frase completa se necessário
                            if len(clean_content) > 1200:
                                sentences = re.split(r'[.!?]\s+', clean_content)
                                truncated = ''
                                for sentence in sentences:
                                    if len(truncated + sentence + '. ') <= 1200:
                                        truncated += sentence + '. '
                                    else:
                                        break
                                clean_content = truncated.strip()
                            
                            response_parts.append(f"**{result['source']}:**\n\n{clean_content}")
                        
                        content = "\n\n---\n\n".join(response_parts)
                        content += "\n\nEssas informações foram extraídas diretamente do manual NEXUS."
                        
                    elif medium_relevance_results:
                        print(f"# Debug - Usando resultados de média relevância (0.3-0.5)")
                        response_parts = []
                        for result in medium_relevance_results[:2]:  # Top 2 de média relevância
                            # Limpar e truncar conteúdo de forma inteligente
                            clean_content = clean_snippet(result['content'])
                            # Truncar em frase completa se necessário
                            if len(clean_content) > 1000:
                                sentences = re.split(r'[.!?]\s+', clean_content)
                                truncated = ''
                                for sentence in sentences:
                                    if len(truncated + sentence + '. ') <= 1000:
                                        truncated += sentence + '. '
                                    else:
                                        break
                                clean_content = truncated.strip()
                            
                            response_parts.append(f"**{result['source']}:**\n\n{clean_content}")
                        
                        content = "\n\n---\n\n".join(response_parts)
                        content += "\n\nEssas informações foram encontradas no manual NEXUS e podem responder sua consulta."
                        
                    else:
                        # Usar agente + busca como fallback
                        print(f"# Debug - Relevância baixa, combinando agente + busca...")
                        response = agent.run(user_input.strip(), stream=False)
                        agent_content = clean_message_content(response.content)
                        
                        # Combinar resposta do agente com melhor resultado da busca
                        if comprehensive_results:
                            best_result = comprehensive_results[0]
                            # Limpar o conteúdo adicional
                            additional_content = clean_snippet(best_result['content'])
                            if len(additional_content) > 600:
                                # Truncar em frase completa
                                sentences = re.split(r'[.!?]\s+', additional_content)
                                truncated = ''
                                for sentence in sentences:
                                    if len(truncated + sentence + '. ') <= 600:
                                        truncated += sentence + '. '
                                    else:
                                        break
                                additional_content = truncated.strip()
                            
                            content = f"{agent_content}\n\n---\n\nInformação adicional do manual:\n\n**{best_result['source']}:**\n{additional_content}"
                        else:
                            content = agent_content
                        
                else:
                    # Usar apenas agente se busca não encontrou nada
                    print(f"# Debug - Busca não encontrou resultados, usando apenas agente...")
                    response = agent.run(user_input.strip(), stream=False)
                    content = clean_message_content(response.content)
                
                # Verificação final: remover qualquer HTML restante
                if re.search(r'<[^>]+>', content):
                    print(f"# Debug - Limpeza final de HTML...")
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'&[a-zA-Z0-9#]+;', '', content)
                    content = content.strip()
                
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