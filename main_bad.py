# Data: 07/11/2025
# IDE Cursor - Auto Agent
# uv run streamlit run main.py
# Plataforma com varios assessments
# Multi-lingua - Seletor de idioma na tela de login

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import time
import sys
from config import DB_PATH, DATA_DIR
import os
import streamlit.components.v1 as components
from texto_manager import get_texto, set_user_language

from paginas.form_model import process_forms_tab
from paginas.monitor import registrar_acesso, main as show_monitor
from paginas.crude import show_crud, manage_assessment_permissions
from paginas.diagnostico import show_diagnostics
from paginas.resultados import show_results
from paginas.resultados_adm import show_resultados_adm

# Importações dinâmicas para multi-assessment
import importlib


# Adicione esta linha logo no início do arquivo, após os imports
# os.environ['RENDER'] = 'true'

# Configuração da página - deve ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="C.H.A.V.E. Comportamental - v2.0",  # Título na Aba do Navegador
    page_icon="🔑",
    layout="centered",
    menu_items={
        'About': """
        ### Plataforma de Assessments Comportamentais e de Valores
        
        Versão 2.0 - 04/11/2025
        
        © 2025 Todos os direitos reservados.
        """,
        'Get Help': None,
        'Report a bug': None
    },
    initial_sidebar_state="collapsed"
)

# Inicializar sistema de textos após set_page_config
from texto_manager import inicializar_textos
inicializar_textos()

# Adicionar verificação e carregamento do logo
import os

# Obtém o caminho absoluto do diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "Logo_2a.jpg")

# --- CSS Global ---
# Adiciona CSS para ocultar o botão de fullscreen das imagens globalmente
st.markdown("""
    <style>
        /* Oculta o botão baseado no aria-label identificado na inspeção */
        button[aria-label="Fullscreen"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)
# --- Fim CSS Global ---

def controlar_cadastro_usuarios():
    """
    Função administrativa para controlar se novos usuários podem se cadastrar
    e quais assessments serão liberados automaticamente
    Disponível apenas para usuários com perfil 'master'
    """
    st.markdown("### 🔐 Controle de Cadastro de Usuários")
    
    st.info("""
    ℹ️ **Função Administrativa:** 
    Esta função permite habilitar ou desabilitar o cadastro de novos usuários na plataforma
    e configurar quais assessments serão liberados automaticamente para novos usuários.
    """)
    
    # Verificar status atual
    cadastro_habilitado = verificar_cadastro_habilitado()
    
    # Mostrar status atual
    if cadastro_habilitado:
        st.success("✅ **Status Atual:** Cadastro de novos usuários está **HABILITADO**")
        st.info("💡 Novos usuários podem se cadastrar na plataforma através da aba 'Cadastro' na tela de login.")
    else:
        st.warning("⚠️ **Status Atual:** Cadastro de novos usuários está **DESABILITADO**")
        st.info("💡 Apenas usuários existentes podem fazer login. A aba 'Cadastro' não aparece na tela de login.")
    
    st.markdown("---")
    
    # Buscar assessments disponíveis
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT assessment_id, assessment_name FROM assessments 
            ORDER BY assessment_id
        """)
        assessments_disponiveis = cursor.fetchall()
        conn.close()
        
        if not assessments_disponiveis:
            st.warning("⚠️ Nenhum assessment encontrado no sistema.")
            return
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar assessments: {str(e)}")
        return
    
    # Buscar assessments padrão configurados
    assessments_padrao = obter_assessments_padrao()
    
    st.markdown("#### 🎯 Configuração de Assessments Padrão")
    st.info("""
    **Configure quais assessments serão liberados automaticamente para novos usuários:**
    - Selecione os assessments que novos usuários terão acesso imediatamente
    - Esta configuração se aplica apenas a usuários cadastrados após a configuração
    """)
    
    # Interface para seleção de assessments
    assessments_selecionados = []
    
    if assessments_disponiveis:
        st.markdown("**Assessments Disponíveis:**")
        
        # Criar checkboxes para cada assessment
        for i, (assessment_id, assessment_name) in enumerate(assessments_disponiveis):
            assessment_name = normalize_assessment_name(assessment_id, assessment_name)
            chave = f"assessment_{assessment_id}_{i}"
            selecionado = st.checkbox(
                f"**{assessment_id} - {assessment_name}**",
                value=assessment_id in assessments_padrao,
                key=chave
            )
            if selecionado:
                assessments_selecionados.append(assessment_id)
    
    st.markdown("---")
    
    # Controles de alteração
    st.markdown("#### ⚙️ Alterar Configuração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Habilitar Cadastro", use_container_width=True, type="primary"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Atualizar configuração de cadastro
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracoes (chave, valor, descricao)
                    VALUES ('cadastro_habilitado', 'true', 'Controla se novos usuários podem se cadastrar')
                """)
                
                # Salvar assessments padrão
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracoes (chave, valor, descricao)
                    VALUES ('assessments_padrao', ?, 'Assessments liberados automaticamente para novos usuários')
                """, (','.join(assessments_selecionados),))
                
                conn.commit()
                conn.close()
                
                st.success("✅ **Cadastro habilitado com sucesso!**")
                st.info(f"💡 A aba 'Cadastro' agora aparecerá na tela de login para novos usuários.")
                if assessments_selecionados:
                    st.info(f"🎯 **Assessments padrão configurados:** {len(assessments_selecionados)} assessment(s) selecionado(s)")
                
                # Registrar ação no log
                registrar_acesso(
                    user_id=st.session_state.get("user_id"),
                    programa="main.py",
                    acao="habilitar_cadastro"
                )
                
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao habilitar cadastro: {str(e)}")
                if 'conn' in locals():
                    conn.close()
    
    with col2:
        if st.button("❌ Desabilitar Cadastro", use_container_width=True, type="secondary"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Atualizar configuração de cadastro
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracoes (chave, valor, descricao)
                    VALUES ('cadastro_habilitado', 'false', 'Controla se novos usuários podem se cadastrar')
                """)
                
                conn.commit()
                conn.close()
                
                st.success("✅ **Cadastro desabilitado com sucesso!**")
                st.info("💡 A aba 'Cadastro' não aparecerá mais na tela de login.")
                
                # Registrar ação no log
                registrar_acesso(
                    user_id=st.session_state.get("user_id"),
                    programa="main.py",
                    acao="desabilitar_cadastro"
                )
                
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao desabilitar cadastro: {str(e)}")
                if 'conn' in locals():
                    conn.close()
    
    # Informações adicionais
    st.markdown("---")
    st.markdown("#### 📊 Informações Importantes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔒 Segurança:**
        - Por padrão, o cadastro vem desabilitado
        - Apenas usuários 'master' podem alterar esta configuração
        - Todas as alterações são registradas no log
        """)
    
    with col2:
        st.markdown("""
        **👥 Impacto:**
        - **Habilitado:** Novos usuários podem se cadastrar
        - **Assessments:** Liberados automaticamente conforme configuração
        - **Desabilitado:** Apenas usuários existentes fazem login
        """)

def obter_assessments_padrao():
    """
    Obtém a lista de assessments que serão liberados automaticamente para novos usuários
    Retorna lista de assessment_ids
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT valor FROM configuracoes WHERE chave = 'assessments_padrao'
        """)
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0].split(',')
        return []
        
    except Exception as e:
        return []

def normalize_assessment_name(assessment_id, assessment_name):
    """
    Padroniza os nomes exibidos para os assessments nos menus.
    01 -> DISC Essencial
    02 -> DISC Integral
    Demais permanecem como estão.
    """
    mapping = {
        "01": "DISC Essencial",
        "02": "DISC Integral",
    }
    return mapping.get(str(assessment_id), assessment_name)

def verificar_cadastro_habilitado():
    """
    Verifica se o cadastro de novos usuários está habilitado
    Retorna True se habilitado, False se desabilitado
    
    NOTA: No Render.com, esta configuração é persistente entre reinicializações
    mas pode ser perdida se o container for recriado completamente.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se existe a tabela de configurações
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='configuracoes'
        """)
        
        if not cursor.fetchone():
            # Se não existe a tabela, criar com cadastro desabilitado por padrão
            cursor.execute("""
                CREATE TABLE configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    descricao TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO configuracoes (chave, valor, descricao)
                VALUES ('cadastro_habilitado', 'false', 'Controla se novos usuários podem se cadastrar')
            """)
            conn.commit()
            conn.close()
            return False
        
        # Buscar configuração
        cursor.execute("""
            SELECT valor FROM configuracoes WHERE chave = 'cadastro_habilitado'
        """)
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0].lower() == 'true'
        
    except Exception as e:
        # Em caso de erro, assumir que está desabilitado por segurança
        # No Render.com, isso garante que o sistema seja seguro por padrão
        return False

def verificar_email_duplicado(email):
    """
    Verifica se o e-mail já existe no banco de dados
    Retorna True se e-mail existe, False se disponível
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM usuarios WHERE LOWER(email) = LOWER(?)
        """, (email.strip(),))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        # Em caso de erro, retornar False para permitir tentativa
        return False

def cadastrar_usuario():
    """
    Interface para cadastro de novos usuários
    """
    # Verificar se o cadastro foi bem-sucedido
    if st.session_state.get("cadastro_sucesso", False):
        # Mostrar tela de sucesso
        st.markdown("### 🎉 Cadastro Realizado com Sucesso!")
        
        st.success(f"""
        **Parabéns, {st.session_state.get('novo_usuario_nome', 'Usuário')}!**
        
        Seu cadastro foi realizado com sucesso na plataforma.
        """)
        
        st.info(f"""
        **📧 E-mail cadastrado:** {st.session_state.get('novo_usuario_email', '')}
        
        **🔐 Próximos passos:**
        1. Vá para a aba "Login" acima
        2. Digite seu e-mail e senha
        3. Comece a usar a plataforma!
        """)
        
        return
    
    st.markdown("### 📝 Cadastro de Novo Usuário")
    
    # Box informativo sobre perfil padrão
    st.info("""
    ℹ️ **Informação importante:** 
    Todos os novos usuários recebem automaticamente o perfil 'usuario' com acesso às funcionalidades básicas da plataforma.
    """)
    
    with st.form("cadastro_form"):
        # Campos do formulário
        nome = st.text_input("Nome Completo *", key="cadastro_nome")
        email = st.text_input("E-mail *", key="cadastro_email")
        senha = st.text_input("Senha *", type="password", key="cadastro_senha")
        confirmar_senha = st.text_input("Confirmar Senha *", type="password", key="cadastro_confirmar_senha")
        empresa = st.text_input("Empresa (opcional)", key="cadastro_empresa")
        
        # Checkbox de aceite dos termos
        aceite_termos = st.checkbox(
            "Declaro que li e aceito os termos de uso *",
            key="cadastro_aceite_termos"
        )
        
        # Verificar senhas se foram preenchidas (apenas para feedback visual)
        if senha and confirmar_senha:
            if senha == confirmar_senha:
                st.success("✅ Senhas coincidem!")
            else:
                st.error("⚠️ As senhas não coincidem")
        
        # Botão de submit
        submit_button = st.form_submit_button("📝 Cadastrar", use_container_width=True)
        
        if submit_button:
            # Validações no submit
            if not nome.strip():
                st.error("❌ Nome completo é obrigatório!")
                return
            
            if not email.strip():
                st.error("❌ E-mail é obrigatório!")
                return
            
            if not senha:
                st.error("❌ Senha é obrigatória!")
                return
            
            if senha != confirmar_senha:
                st.error("❌ As senhas devem coincidir!")
                return
            
            if not aceite_termos:
                st.error("❌ Você deve aceitar os termos de uso!")
                return
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verificação final de e-mail duplicado (dentro da transação)
                cursor.execute("""
                    SELECT id FROM usuarios WHERE LOWER(email) = LOWER(?)
                """, (email.strip(),))
                if cursor.fetchone():
                    st.error("❌ Este e-mail já está cadastrado. Tente fazer login ou use outro e-mail.")
                    conn.close()
                    return
                
                # Gerar novo user_id
                cursor.execute("SELECT MAX(user_id) FROM usuarios")
                max_user_id = cursor.fetchone()[0]
                novo_user_id = (max_user_id or 0) + 1
                
                # Inserir novo usuário
                cursor.execute("""
                    INSERT INTO usuarios (user_id, nome, email, senha, perfil, empresa)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    novo_user_id,
                    nome.strip(),
                    email.strip().lower(),
                    senha,
                    'usuario',  # Perfil padrão
                    empresa.strip() if empresa else None
                ))
                
                # Verificar se a inserção foi bem-sucedida
                cursor.execute("""
                    SELECT id FROM usuarios WHERE user_id = ?
                """, (novo_user_id,))
                if not cursor.fetchone():
                    st.error("❌ Erro: Usuário não foi inserido corretamente.")
                    conn.rollback()
                    conn.close()
                    return
                
                # Liberar assessments padrão para o novo usuário
                assessments_padrao = obter_assessments_padrao()
                if assessments_padrao:
                    for assessment_id in assessments_padrao:
                        cursor.execute("""
                            INSERT OR REPLACE INTO assessments (user_id, assessment_id, assessment_name, access_granted)
                            VALUES (?, ?, ?, ?)
                        """, (novo_user_id, assessment_id, f"Assessment {assessment_id}", 1))
                
                conn.commit()
                conn.close()
                
                # Registrar no log
                registrar_acesso(
                    user_id=novo_user_id,
                    programa="main.py",
                    acao="cadastro_usuario"
                )
                
                st.success("🎉 **Cadastro realizado com sucesso!**")
                if assessments_padrao:
                    st.info(f"💡 **Próximos passos:** Agora você pode fazer login com seu e-mail e senha. Você terá acesso a {len(assessments_padrao)} assessment(s) automaticamente.")
                else:
                    st.info("💡 **Próximos passos:** Agora você pode fazer login com seu e-mail e senha.")
                
                # Limpar campos do formulário e redirecionar
                st.session_state["cadastro_sucesso"] = True
                st.session_state["novo_usuario_email"] = email.strip().lower()
                st.session_state["novo_usuario_nome"] = nome.strip()
                
                # Limpar campos do formulário
                time.sleep(3)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar usuário: {str(e)}")
                if 'conn' in locals():
                    conn.rollback()
                    conn.close()

def authenticate_user():
    """Autentica o usuário e verifica seu perfil no banco de dados."""
    # Adicionar CSS para a página de login
    if not st.session_state.get("logged_in", False):
        st.markdown("""
            <style>
                /* Oculta a barra lateral na página de login */
                [data-testid="stSidebar"] {
                    display: none;
                }
                /* Estilo para a página de login */
                [data-testid="stAppViewContainer"] {
                    background-color: #cbe7f5;
                }
                
                /* Remove a faixa branca superior */
                [data-testid="stHeader"] {
                    background-color: #cbe7f5;
                }
                
                /* Ajuste da cor do texto para melhor contraste */
                [data-testid="stAppViewContainer"] p {
                    color: black;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # Verifica se o banco existe
    if not DB_PATH.exists():
        st.error(get_texto('main_057', 'Banco de dados não encontrado').format(caminho=DB_PATH))
        return False, None
        
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = None

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    if not st.session_state["logged_in"]:
        # Imagem de capa - Tela 
        st.image("webinar1.jpg", use_container_width=True)
            
        st.markdown(f"""
            <p style='text-align: center; font-size: 35px;'>{get_texto('main_001', 'Plataforma Âncoras de Carreira')}</p>
        """, unsafe_allow_html=True)
        
        # Seletor de idioma
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_language = st.selectbox(
                "🌐 Idioma / Language / Idioma",
                options=[
                    ("pt", "🇧🇷 Português"),
                    ("en", "🇺🇸 English"),
                    ("es", "🇪🇸 Español")
                ],
                format_func=lambda x: x[1],
                key="language_selector"
            )
            selected_language_code = selected_language[0]
        
        # Criar um usuário temporário para carregar textos no idioma selecionado
        temp_user_id = f"temp_{selected_language_code}"
        
        # Verificar se cadastro está habilitado
        cadastro_habilitado = verificar_cadastro_habilitado()
        
        # Sistema de tabs
        if cadastro_habilitado:
            # Verificar qual aba deve estar ativa
            active_tab = st.session_state.get("active_tab", "login")
            
            if active_tab == "login":
                tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
                login_tab = tab1
                cadastro_tab = tab2
            else:
                tab1, tab2 = st.tabs(["📝 Cadastro", "🔐 Login"])
                login_tab = tab2
                cadastro_tab = tab1
            
            with login_tab:
                # Formulário de login
                with st.form("login_form"):
                    email = st.text_input(get_texto('main_002', 'E-mail', user_id=temp_user_id), key="email")
                    password = st.text_input(get_texto('main_003', 'Senha', user_id=temp_user_id), type="password", key="password")

                    aceite_termos = st.checkbox(
                        get_texto('main_004', 'Declaro que li e aceito os termos de uso', user_id=temp_user_id),
                        key='aceite_termos'
                    )

                    login_button = st.form_submit_button(get_texto('main_005', 'Entrar', user_id=temp_user_id), use_container_width=True)
                    
                    if login_button:
                        if not aceite_termos:
                            st.warning(get_texto('main_006', 'Você deve aceitar os termos de uso para continuar.', user_id=temp_user_id))
                        else:
                            clean_email = email.strip()

                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT id, user_id, perfil, nome FROM usuarios WHERE LOWER(email) = LOWER(?) AND senha = ?
                            """, (clean_email, password))
                            user = cursor.fetchone()
                            conn.close()

                            if user:
                                # Salvar idioma escolhido no banco
                                set_user_language(user[1], selected_language_code)
                                
                                st.session_state["logged_in"] = True
                                st.session_state["user_profile"] = user[2]
                                st.session_state["user_id"] = user[1]
                                st.session_state["user_name"] = user[3]
                                
                                # Registrar o acesso bem-sucedido
                                registrar_acesso(
                                    user_id=user[1],
                                    programa="main.py",
                                    acao="login"
                                )
                                st.rerun()
                            else:
                                st.error(get_texto('main_007', 'E-mail ou senha inválidos. Por favor, verifique seus dados e tente novamente.', user_id=temp_user_id))
            
            with cadastro_tab:
                # Formulário de cadastro
                cadastrar_usuario()
        else:
            # Apenas formulário de login (cadastro desabilitado)
            with st.form("login_form"):
                email = st.text_input(get_texto('main_002', 'E-mail', user_id=temp_user_id), key="email")
                password = st.text_input(get_texto('main_003', 'Senha', user_id=temp_user_id), type="password", key="password")

                aceite_termos = st.checkbox(
                    get_texto('main_004', 'Declaro que li e aceito os termos de uso', user_id=temp_user_id),
                    key='aceite_termos'
                )

                login_button = st.form_submit_button(get_texto('main_005', 'Entrar', user_id=temp_user_id), use_container_width=True)
                
                if login_button:
                    if not aceite_termos:
                        st.warning(get_texto('main_006', 'Você deve aceitar os termos de uso para continuar.', user_id=temp_user_id))
                    else:
                        clean_email = email.strip()

                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT id, user_id, perfil, nome FROM usuarios WHERE LOWER(email) = LOWER(?) AND senha = ?
                        """, (clean_email, password))
                        user = cursor.fetchone()
                        conn.close()

                        if user:
                            # Salvar idioma escolhido no banco
                            set_user_language(user[1], selected_language_code)
                            
                            st.session_state["logged_in"] = True
                            st.session_state["user_profile"] = user[2]
                            st.session_state["user_id"] = user[1]
                            st.session_state["user_name"] = user[3]
                            
                            # Registrar o acesso bem-sucedido
                            registrar_acesso(
                                user_id=user[1],
                                programa="main.py",
                                acao="login"
                            )
                            st.rerun()
                        else:
                            st.error(get_texto('main_007', 'E-mail ou senha inválidos. Por favor, verifique seus dados e tente novamente.', user_id=temp_user_id))

    return st.session_state.get("logged_in", False), st.session_state.get("user_profile", None)

def get_user_assessments(user_id):
    """
    Busca assessments disponíveis para o usuário
    Considera perfil master e adm com acesso total
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Primeiro, verificar o perfil do usuário
        cursor.execute("""
            SELECT perfil FROM usuarios WHERE user_id = ?
        """, (user_id,))
        
        user_profile = cursor.fetchone()
        if not user_profile:
            conn.close()
            return []
        
        user_profile = user_profile[0].lower()
        
        # Se for master ou adm, retornar todos os assessments disponíveis
        if user_profile in ["master", "adm"]:
            cursor.execute("""
                SELECT DISTINCT assessment_id, assessment_name, 1 as access_granted
                FROM assessments 
                ORDER BY assessment_id
            """)
        else:
            # Para outros perfis, verificar permissões específicas
            cursor.execute("""
                SELECT assessment_id, assessment_name, access_granted
                FROM assessments 
                WHERE user_id = ? AND access_granted = 1
                ORDER BY assessment_id
            """, (user_id,))
        
        assessments = cursor.fetchall()
        conn.close()
        
        return assessments
    except Exception as e:
        st.error(f"Erro ao buscar assessments: {str(e)}")
        return []

def check_assessment_access(user_id, assessment_id):
    """
    Verifica se o usuário tem acesso ao assessment
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar perfil do usuário
        cursor.execute("""
            SELECT perfil FROM usuarios WHERE user_id = ?
        """, (user_id,))
        
        user_profile = cursor.fetchone()
        if not user_profile:
            conn.close()
            return False
        
        user_profile = user_profile[0].lower()
        
        # Master e adm têm acesso total
        if user_profile in ["master", "adm"]:
            conn.close()
            return True
        
        # Para outros perfis, verificar permissão específica
        cursor.execute("""
            SELECT access_granted FROM assessments 
            WHERE user_id = ? AND assessment_id = ?
        """, (user_id, assessment_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0] == 1
        
    except Exception as e:
        st.error(f"Erro ao verificar acesso: {str(e)}")
        return False

def show_assessment_selector():
    """
    Exibe seletor de assessments disponíveis para o usuário
    """
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Usuário não está logado!")
        return None
    
    # Buscar assessments disponíveis
    assessments = get_user_assessments(user_id)
    
    if not assessments:
        st.warning("Nenhum assessment disponível para seu usuário.")
        return None
    
    st.markdown("### 🎯 Comece sua jornada de autoconhecimento")
    
    # Criar opções para o seletor com opção padrão vazia
    assessment_options = ["Selecione um assessment..."]  # Opção padrão vazia
    assessment_mapping = {}
    
    for assessment_id, assessment_name, _ in assessments:
        assessment_name = normalize_assessment_name(assessment_id, assessment_name)
        option_text = f"{assessment_id} - {assessment_name}"
        assessment_options.append(option_text)
        assessment_mapping[option_text] = assessment_id
    
    # Chave única para o seletor
    unique_key = f"assessment_selector_{user_id}"
    
    selected_assessment = st.selectbox(
        "Selecione o Assessment que deseja responder e avance pelas três etapas — Parte 1, Parte 2 e Resultados.",
        options=assessment_options,
        key=unique_key
    )
    
    # Verificar se uma opção válida foi selecionada (não a opção padrão)
    if selected_assessment and selected_assessment != "Selecione um assessment...":
        assessment_id = assessment_mapping[selected_assessment]
        st.session_state["selected_assessment_id"] = assessment_id
        return assessment_id
    
    # Limpar seleção se voltou para a opção padrão
    if "selected_assessment_id" in st.session_state:
        del st.session_state["selected_assessment_id"]
    
    return None

def load_assessment_module(assessment_id):
    """
    Carrega dinamicamente o módulo do assessment selecionado
    """
    try:
        # Mapeamento de assessments para seus módulos
        assessment_modules = {
            "01": ("form_model_01", "resultados_01"),
            "02": ("form_model_02", "resultados_02"),
            "03": ("form_model_03", "resultados_03"),
            "04": ("form_model_04", "resultados_04"),
            "05": ("form_model_05", "resultados_05")
        }
        
        if assessment_id not in assessment_modules:
            st.error(f"Assessment {assessment_id} não encontrado!")
            return None, None, None
        
        form_module_name, results_module_name = assessment_modules[assessment_id]
        
        # Carregar módulo do formulário
        form_module = importlib.import_module(f"paginas.{form_module_name}")
        
        # Determinar o nome da função baseado no assessment_id
        if assessment_id == "01":
            function_name = "process_forms_tab"
        else:
            function_name = f"process_forms_tab_{assessment_id}"
        
        process_forms_tab = getattr(form_module, function_name, None)
        
        # Carregar módulo de resultados
        results_module = importlib.import_module(f"paginas.{results_module_name}")
        show_results = getattr(results_module, "show_results", None)
        
        # Obter nome do assessment
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT assessment_name FROM assessments 
            WHERE assessment_id = ? LIMIT 1
        """, (assessment_id,))
        result = cursor.fetchone()
        assessment_name = result[0] if result else f"Assessment {assessment_id}"
        assessment_name = normalize_assessment_name(assessment_id, assessment_name)
        conn.close()
        
        return process_forms_tab, show_results, assessment_name
        
    except Exception as e:
        st.error(f"Erro ao carregar módulo do assessment: {str(e)}")
        return None, None, None

def show_assessment_execution():
    """
    Executa o assessment selecionado
    """
    assessment_id = st.session_state.get("selected_assessment_id")
    user_id = st.session_state.get("user_id")
    
    if not assessment_id:
        st.warning("Por favor, selecione um assessment primeiro.")
        return
    
    # Verificar se o usuário tem acesso ao assessment
    if not check_assessment_access(user_id, assessment_id):
        st.error("❌ **Acesso negado.** Você não tem permissão para acessar este assessment.")
        st.info("💡 **Solução:** Entre em contato com o administrador para solicitar acesso.")
        return
    
    # Carregar módulo do assessment
    process_forms_tab, show_results, assessment_name = load_assessment_module(assessment_id)
    
    if not process_forms_tab:
        st.error("❌ **Erro:** Não foi possível carregar o módulo do assessment.")
        return
    
    st.markdown(f"### 🎯 {assessment_name}")
    
    # Para DISC Essencial (assessment "01"), usar seções específicas
    if assessment_id == "01":
        # Mapeamento específico para DISC Essencial 
        st.markdown("#### 📋 Selecione a Parte que deseja")
        
        # Adiciona um ID para facilitar o scroll
        st.markdown('<div id="menu-selecao-parte"></div>', unsafe_allow_html=True)
        
        # Usar radio buttons como no original
        section_options = {
            "🎯 Parte 1": "perfil",
            "📊 Parte 2": "comportamento", 
            "📈 Resultados": "resultado"
        }
        
        selected_section = st.radio(
            "IMPORTANTE: precisa responder tanto a Parte 1 quanto a Parte 2",
            options=list(section_options.keys()),
            key="disc10_section_selector",
            horizontal=True
        )
        
        # Executar a seção selecionada
        if selected_section:
            section_value = section_options[selected_section]
            process_forms_tab(section_value)
    
    # Para DISC 20 (assessment "02"), usar seções específicas
    elif assessment_id == "02":
        # Mapeamento específico para DISC 20 - usar seções corretas
        st.markdown("#### 📋 Selecione a seção que deseja responder")
        
        # Usar radio buttons como no original
        section_options = {
            "🎯 Parte 1": "perfil",
            "📊 Parte 2": "comportamento", 
            "📈 Resultados": "resultado"
        }
        
        selected_section = st.radio(
            "Escolha a seção:",
            options=list(section_options.keys()),
            key="disc20_section_selector",
            horizontal=True
        )
        
        # Executar a seção selecionada
        if selected_section:
            section_value = section_options[selected_section]
            process_forms_tab(section_value)
    
    # Para Âncoras de Carreira (assessment "03"), usar seções específicas
    elif assessment_id == "03":
        # Mapeamento específico para Âncoras - usar seções corretas
        st.markdown("#### 📋 Selecione a Parte que deseja")
        
        # Usar radio buttons como no original
        section_options = {
            "🎯 Parte 1": "ancoras_p1",
            "📊 Parte 2": "ancoras_p2", 
            "📈 Resultados": "resultado"
        }
        
        selected_section = st.radio(
            "IMPORTANTE: Precisa responder tanto a Parte 1 quanto a Parte 2",
            options=list(section_options.keys()),
            key="ancoras_section_selector",
            horizontal=True
        )
        
        # Executar a seção selecionada
        if selected_section:
            section_value = section_options[selected_section]
            process_forms_tab(section_value)
    
    # Para Armadilhas do Empresário (assessment "04"), usar seções específicas
    elif assessment_id == "04":
        # Mapeamento específico para Armadilhas - usar seções corretas
        st.markdown("#### 📋 Selecione a Parte que deseja")
        
        # Usar radio buttons como no original
        section_options = {
            "🎯 Parte 1": "armadilhas_p1",
            "📊 Parte 2": "armadilhas_p2", 
            "📈 Resultados": "resultado"
        }
        
        selected_section = st.radio(
            "IMPORTANTE: Precisa responder tanto a Parte 1 quanto a Parte 2",
            options=list(section_options.keys()),
            key="armadilhas_section_selector",
            horizontal=True
        )
        
        # Executar a seção selecionada
        if selected_section:
            section_value = section_options[selected_section]
            process_forms_tab(section_value)
    
    else:
        # Para outros assessments, executar normalmente
        process_forms_tab()

def show_assessment_results():
    """
    Mostra resultados do assessment selecionado
    """
    assessment_id = st.session_state.get("selected_assessment_id")
    user_id = st.session_state.get("user_id")
    
    if not assessment_id:
        st.warning("Por favor, selecione um assessment primeiro.")
        return
    
    # Verificar se o usuário tem acesso ao assessment
    if not check_assessment_access(user_id, assessment_id):
        st.error("❌ **Acesso negado.** Você não tem permissão para acessar este assessment.")
        st.info("💡 **Solução:** Entre em contato com o administrador para solicitar acesso.")
        return
    
    # Carregar módulo do assessment
    process_forms_tab, show_results, assessment_name = load_assessment_module(assessment_id)
    
    if not show_results:
        st.error("❌ **Erro:** Não foi possível carregar o módulo de resultados.")
        return
    
    st.markdown(f"### 📊 Resultados - {assessment_name}")
    
    # Mostrar resultados
    tabela_escolhida = f"forms_resultados_{assessment_id}"
    titulo_pagina = f"Análise das Avaliações - {assessment_name}"
    
    show_results(tabela_escolhida, titulo_pagina, user_id)

def show_admin_menu():
    """
    Exibe menu administrativo
    """
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Usuário não está logado!")
        return
    
    # Verificar perfil do usuário
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT perfil FROM usuarios WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    user_profile = result[0] if result else None
    conn.close()
    
    # Verificar se é administrador para funções administrativas
    is_admin = user_profile and user_profile.lower() in ["adm", "master"]
    
    if not is_admin:
        st.info("ℹ️ **Acesso limitado:** Algumas funções administrativas não estão disponíveis para seu perfil.")
        st.info("🔐 **Disponível para todos:** Trocar Senha")
    else:
        st.success("✅ **Acesso completo:** Todas as funções administrativas estão disponíveis.")
    
    st.markdown("### ⚙️ Módulo Administrativo")
    
    # Criar botões para as opções administrativas (apenas para administradores)
    if is_admin:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Análise de Usuários", use_container_width=True):
                st.session_state["admin_function"] = "Análise de Usuários"
        
        with col2:
            if st.button("🗃️ CRUD - Gerenciar Dados", use_container_width=True):
                st.session_state["admin_function"] = "CRUD - Gerenciar Dados"
        
        with col3:
            if st.button("📈 Monitor de Uso", use_container_width=True):
                st.session_state["admin_function"] = "Monitor de Uso"
        
        with col4:
            if st.button("🔐 Controle de Assessments", use_container_width=True):
                st.session_state["admin_function"] = "Controle de Assessments"
    
    # Adicionar botão para Controle de Cadastro (apenas para master)
    if user_profile and user_profile.lower() == "master":
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥 Controle de Cadastro", use_container_width=True):
                st.session_state["admin_function"] = "Controle de Cadastro"
    
    # Adicionar botão para Trocar Senha (disponível para todos os perfis)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔐 Trocar Senha", use_container_width=True):
            st.session_state["admin_function"] = "Trocar Senha"
    
    
    # Processar função administrativa selecionada
    admin_function = st.session_state.get("admin_function")
    if admin_function == "Análise de Usuários" and is_admin:
        show_resultados_adm()
    elif admin_function == "CRUD - Gerenciar Dados" and is_admin:
        show_crud()
    elif admin_function == "Monitor de Uso" and is_admin:
        show_monitor()
    elif admin_function == "Controle de Assessments" and is_admin:
        manage_assessment_permissions()
    elif admin_function == "Controle de Cadastro" and user_profile and user_profile.lower() == "master":
        controlar_cadastro_usuarios()
    elif admin_function == "Trocar Senha":
        trocar_senha()

def get_timezone_offset():
    """
    Determina se é necessário aplicar offset de timezone baseado no ambiente
    """
    is_production = os.getenv('RENDER') is not None
    
    if is_production:
        # Se estiver no Render, ajusta 3 horas para trás
        return datetime.now() - timedelta(hours=3)
    return datetime.now()  # Se local, usa hora atual

def show_welcome():
    
    st.markdown(f"""
        <p style='text-align: center; font-size: 30px; font-weight: bold;'>{get_texto('main_008', 'Plataforma CHAVE')}</p>
        
    """, unsafe_allow_html=True)
    
    # Buscar dados do usuário
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, empresa 
        FROM usuarios 
        WHERE user_id = ?
    """, (st.session_state.get('user_id'),))
    user_info = cursor.fetchone()
    
    # Removemos a consulta de contagem de formulários
    conn.close()
    
    empresa = user_info[1] if user_info[1] is not None else "Não informada"
    
    # Layout em colunas usando st.columns
    col1, col2, col3 = st.columns(3)
    
    # Coluna 1: Propósito
    with col1:
        st.markdown(f"""
            <div style="background-color: #007a7d; padding: 20px; border-radius: 8px; height: 100%;">
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;">{get_texto('main_009', 'Propósito')}</p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>{get_texto('main_010', 'Este Web App tem como objetivo identificar suas âncoras de carreira predominantes.')}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Coluna 2: Identidade
    with col2:
        st.markdown(f"""
            <div style="background-color: #53a7a9; padding: 20px; border-radius: 8px; height: 100%;">
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;">{get_texto('main_009b', 'Como fazemos')}</p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>{get_texto('main_011', 'Ao identificar suas âncoras, você ativa uma jornada de autoconhecimento profissional aplicado.')}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Coluna 3: Funções
    with col3:
        modulos_html = f"""
            <div style="background-color: #8eb0ae; padding: 20px; border-radius: 8px; height: 100%;">
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;">{get_texto('main_009c', 'O que fazemos')}</p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>{get_texto('main_012', 'Mais do que um diagnóstico, é um ponto de partida para evoluir com propósito.')}</p>
                    <p></p>                    
                    <p></p>                    
                </div>
            </div>
        """
        
        st.markdown(modulos_html, unsafe_allow_html=True)

def trocar_senha():
    """Função para permitir que o usuário logado troque sua senha"""
    
    st.markdown(f"""
        <p style='text-align: center; font-size: 30px; font-weight: bold;'>
            {get_texto('main_019', 'Trocar Senha')}
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style='background-color:#f0f0f0;padding:15px;border-radius:5px;margin-bottom:20px;'>
            <p style='font-size:16px;color:#333;'>
                {get_texto('main_020', 'Instruções para trocar senha')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulário de troca de senha
    with st.form("trocar_senha_form"):
        senha_atual = st.text_input(get_texto('main_021', 'Senha Atual'), type="password", key="senha_atual")
        nova_senha = st.text_input(get_texto('main_022', 'Nova Senha'), type="password", key="nova_senha")
        confirmar_senha = st.text_input(get_texto('main_023', 'Confirmar Nova Senha'), type="password", key="confirmar_senha")
        
        submit_button = st.form_submit_button(get_texto('main_024', 'Alterar Senha'), use_container_width=True)
        
        if submit_button:
            # Validações
            if not senha_atual or not nova_senha or not confirmar_senha:
                st.error(get_texto('main_025', 'Todos os campos são obrigatórios!'))
                return
            
            if nova_senha != confirmar_senha:
                st.error(get_texto('main_026', 'As senhas não coincidem! Digite a mesma senha nos dois campos.'))
                return
            
            if nova_senha == senha_atual:
                st.error(get_texto('main_027', 'A nova senha deve ser diferente da senha atual!'))
                return
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verificar se a senha atual está correta
                cursor.execute("""
                    SELECT id FROM usuarios 
                    WHERE user_id = ? AND senha = ?
                """, (st.session_state["user_id"], senha_atual))
                
                if not cursor.fetchone():
                    st.error(get_texto('main_028', 'Senha atual incorreta! Verifique e tente novamente.'))
                    conn.close()
                    return
                
                # Atualizar a senha
                cursor.execute("""
                    UPDATE usuarios 
                    SET senha = ? 
                    WHERE user_id = ?
                """, (nova_senha, st.session_state["user_id"]))
                
                conn.commit()
                conn.close()
                
                # Registrar a ação no monitor
                registrar_acesso(
                    user_id=st.session_state["user_id"],
                    programa="main.py",
                    acao="trocar_senha"
                )
                
                st.success(get_texto('main_029', '✅ Senha alterada com sucesso!'))
                st.info(get_texto('main_030', 'A nova senha será válida no próximo login.'))
                
                # Limpar os campos do formulário
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(get_texto('main_031', 'Erro ao alterar senha: {erro}').format(erro=str(e)))
                if 'conn' in locals():
                    conn.close()

def show_analysis_with_admin_controls():
    """Wrapper para exibir análises com controles administrativos quando necessário"""
    
    # Verificar se é visualização administrativa
    admin_user_id = st.session_state.get("admin_view_user_id")
    admin_user_name = st.session_state.get("admin_view_user_name")
    current_user_id = st.session_state.get("user_id")
    
    if admin_user_id and admin_user_id != current_user_id:
        # É visualização administrativa
        st.markdown(f"""
            <div style='background-color:#fff3cd;padding:10px;border-radius:5px;margin-bottom:15px;border-left:4px solid #ffc107;'>
                <p style='margin:0;font-size:14px;'>
                    {get_texto('main_037', '🔍 **Modo Administrativo:** Visualizando análise de **{{usuario}}**').format(usuario=admin_user_name)}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão para voltar ao módulo administrativo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(get_texto('main_038', '⬅️ **Voltar ao Módulo Administrativo**'), use_container_width=True, type="secondary"):
                # Limpar dados administrativos
                st.session_state.pop("admin_view_user_id", None)
                st.session_state.pop("admin_view_user_name", None)
                st.session_state.pop("admin_selected_assessment", None)
                
                # Definir flag para retornar ao módulo administrativo
                st.session_state["return_to_admin"] = True
                st.rerun()
        
        st.markdown("---")
        
        # Verificar se há um assessment específico selecionado
        selected_assessment = st.session_state.get("admin_selected_assessment")
        
        if selected_assessment:
            # Mostrar análise do assessment específico selecionado
            try:
                # Carregar módulo do assessment selecionado
                process_forms_tab, show_results, assessment_name = load_assessment_module(selected_assessment)
                
                if show_results:
                    tabela_escolhida = f"forms_resultados_{selected_assessment}"
                    titulo_pagina = f"Análise Administrativa - {admin_user_name} - {assessment_name}"
                    show_results(tabela_escolhida, titulo_pagina, admin_user_id)
                else:
                    st.error("❌ **Erro:** Não foi possível carregar o módulo de resultados.")
            except Exception as e:
                st.error(f"❌ **Erro ao carregar análise:** {str(e)}")
        else:
            # Se não há assessment selecionado, mostrar mensagem
            st.warning("⚠️ **Nenhum assessment selecionado.**")
            st.info("💡 **Orientação:** Volte ao módulo administrativo e selecione um assessment específico para visualizar.")
    
    else:
        # Visualização normal do próprio usuário
        assessment_id = st.session_state.get("selected_assessment_id")
        if not assessment_id:
            st.warning("Por favor, selecione um assessment primeiro.")
            return
        
        # Carregar módulo do assessment
        process_forms_tab, show_results, assessment_name = load_assessment_module(assessment_id)
        
        if not show_results:
            st.error("❌ **Erro:** Não foi possível carregar o módulo de resultados.")
            return
        
        # Mostrar resultados do assessment selecionado
        tabela_escolhida = f"forms_resultados_{assessment_id}"
        titulo_pagina = f"Análise das Avaliações - {assessment_name}"
        
        show_results(tabela_escolhida, titulo_pagina, current_user_id)


def main():
    """Gerencia a navegação entre as páginas do sistema."""
    # Verifica se o diretório data existe
    if not DATA_DIR.exists():
        st.error(get_texto('main_058', 'Pasta \'{pasta}\' não encontrada. O programa não pode continuar.').format(pasta=DATA_DIR))
        st.stop()
        
    # Verifica se o banco existe
    if not DB_PATH.exists():
        st.error(get_texto('main_059', 'Banco de dados \'{banco}\' não encontrado. O programa não pode continuar.').format(banco=DB_PATH))
        st.stop()
        
    logged_in, user_profile = authenticate_user()
    
    if not logged_in:
        st.stop()
    
    # Armazenar página anterior para comparação
    if "previous_page" not in st.session_state:
        st.session_state["previous_page"] = None

    # --- HEADER ---
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
    
    with col2:
        st.markdown(f"""
            <p style='text-align: center; font-size: 30px; font-weight: bold;'>
                {get_texto('main_013', 'Plataforma CHAVE')}
            <p style='text-align: center; font-size: 20px; font-weight: normal;'>
                {get_texto('main_013a', 'Subtítulo')}
            </p>
        """, unsafe_allow_html=True)
        with st.expander(get_texto('main_014', 'Informações do Usuário / Logout'), expanded=False):
            st.markdown(f"""
                {get_texto('main_015', '**Usuário:**')} {st.session_state.get('user_name')}  
                {get_texto('main_016', '**ID:**')} {st.session_state.get('user_id')}  
                {get_texto('main_017', '**Perfil:**')} {st.session_state.get('user_profile')}
            """)
            if st.button(get_texto('main_018', 'Logout')):
                if "user_id" in st.session_state:
                    registrar_acesso(
                        user_id=st.session_state["user_id"],
                        programa="main.py",
                        acao="logout"
                    )
                for key in ['logged_in', 'user_profile', 'user_id', 'user_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- MENU PRINCIPAL ---
    
    st.markdown("### 🏠 Menu Principal")
    st.info("💡 **Escolha uma das opções abaixo para continuar.**")
    
    # Criar botões para as opções principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Bem-vindo", use_container_width=True):
            st.session_state["selected_function"] = "Bem-vindo"
    
    with col2:
        if st.button("🎯 Assessment", use_container_width=True):
            st.session_state["selected_function"] = "Assessment"
    
    with col3:
        if st.button("📈 Análises", use_container_width=True):
            st.session_state["selected_function"] = "Análises"
    
    with col4:
        if st.button("⚙️ Administração", use_container_width=True):
            st.session_state["selected_function"] = "Administração"
    
    # Verificar qual função foi selecionada
    selected_function = st.session_state.get("selected_function")
    if not selected_function:
        st.info("💡 **Selecione uma opção acima para continuar.**")
        return

    # Verificar se há retorno ao módulo administrativo
    if st.session_state.get("return_to_admin", False):
        st.session_state["return_to_admin"] = False
        # Exibir módulo administrativo diretamente
        show_resultados_adm()
        return
    
    # Verificar se há redirecionamento para análise administrativa
    if st.session_state.get("redirect_to_analysis", False):
        st.session_state["redirect_to_analysis"] = False
        # Exibir análise administrativa diretamente
        show_analysis_with_admin_controls()
        return
    
    # Processar a função selecionada
    if selected_function == "Bem-vindo":
        show_welcome()
    elif selected_function == "Assessment":
        # Mostrar seletor de assessment apenas quando necessário
        assessment_id = show_assessment_selector()
        if not assessment_id:
            return
        
        # Mostrar opções do assessment selecionado
        st.markdown("### 📋 Opções do Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Realizar Assessment", use_container_width=True):
                st.session_state["assessment_action"] = "Realizar Assessment"
        
        with col2:
            if st.button("📈 Ver Análises", use_container_width=True):
                st.session_state["assessment_action"] = "Ver Análises"
        
        # Processar ação do assessment
        assessment_action = st.session_state.get("assessment_action")
        if assessment_action == "Realizar Assessment":
            show_assessment_execution()
        elif assessment_action == "Ver Análises":
            show_analysis_with_admin_controls()
            
    elif selected_function == "Análises":
        # Para análises, precisa selecionar um assessment primeiro
        assessment_id = show_assessment_selector()
        if not assessment_id:
            return
        
        # Mostrar análises do assessment selecionado
        show_analysis_with_admin_controls()
        
    elif selected_function == "Administração":
        show_admin_menu()
    else:
        st.error("Função não encontrada.")

    # --- FOOTER ---
    st.markdown("<br>" * 1, unsafe_allow_html=True)
    
    # Logo do rodapé
    footer_logo_path = os.path.join(current_dir, "Logo_1b.jpg")
    if os.path.exists(footer_logo_path):
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image(
                footer_logo_path,
                width=200, 
                use_container_width=False
            )

if __name__ == "__main__":
    main()
