# Data: 10/09/2025 - Hora: 10:00
# IDE Cursor - Auto
# comando: streamlit run main.py
# 7 Armadilhas do Eu Empresário
# .\env\Scripts\Activate      
# streamlit run main.py

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import time
import sys
from config import DB_PATH, DATA_DIR
import os
import streamlit.components.v1 as components

from paginas.form_model import process_forms_tab
from paginas.monitor import registrar_acesso, main as show_monitor
from paginas.crude import show_crud
from paginas.diagnostico import show_diagnostics
from paginas.resultados import show_results
from paginas.resultados_adm import show_resultados_adm


# Adicione esta linha logo no início do arquivo, após os imports
# os.environ['RENDER'] = 'true'

# Configuração da página - deve ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="7Armadilhas - v1.0",  # Título na Aba do Navegador
    page_icon="📊",
    layout="centered",
    menu_items={
        'About': """
        ### Sobre o Sistema - 7 Armadilhas do Eu Empresário
        
        7 perguntas Diretas e 7 perguntas Invertidas.
        Versão: 1.0 - 10/09/2025
        
        Este assessment foi criado pela Erika Rossi - EAR Consultoria.
        
        © 2025 Todos os direitos reservados.
        """,
        'Get Help': None,
        'Report a bug': None
    },
    initial_sidebar_state="collapsed"
)

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

def verificar_email_duplicado(email):
    """Verifica se o e-mail já existe no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM usuarios WHERE LOWER(email) = LOWER(?)
        """, (email.strip(),))
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None
    except Exception as e:
        st.error(f"Erro ao verificar e-mail: {str(e)}")
        return True  # Em caso de erro, assume que existe para evitar duplicação

def cadastrar_usuario():
    """Função para cadastrar novos usuários"""
    st.markdown("### 📝 Cadastro de Novo Usuário")
    
    # Informações sobre o perfil padrão
    st.info("""
    **ℹ️ Informações importantes:**
    - Todos os novos usuários recebem o perfil **'usuario'** por padrão
    - Este perfil permite acesso às funcionalidades básicas da ferramenta
    - Para alterações de perfil, entre em contato com o administrador
    """)
    
    with st.form("cadastro_form"):
        nome = st.text_input("Nome Completo", key="cadastro_nome")
        email = st.text_input("E-mail", key="cadastro_email")
        senha = st.text_input("Senha", type="password", key="cadastro_senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", key="cadastro_confirmar_senha")
        empresa = st.text_input("Empresa (opcional)", key="cadastro_empresa")
        
        aceite_termos_cadastro = st.checkbox(
            'Declaro que li e aceito os [termos de uso da ferramenta](https://ag93eventos.com.br/ear/Termos_Uso_DISC.pdf)',
            key='aceite_termos_cadastro'
        )
        
        cadastro_button = st.form_submit_button("Cadastrar", use_container_width=True)
        
        if cadastro_button:
            # Validações
            if not nome.strip():
                st.error("Nome é obrigatório.")
                return False
                
            if not email.strip():
                st.error("E-mail é obrigatório.")
                return False
                
            if not senha.strip():
                st.error("Senha é obrigatória.")
                return False
                
            if senha != confirmar_senha:
                st.error("As senhas não coincidem.")
                return False
                
            if not aceite_termos_cadastro:
                st.error("Você deve aceitar os termos de uso para continuar.")
                return False
            
            # Verificar se e-mail já existe
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verificar e-mail duplicado
                cursor.execute("""
                    SELECT id FROM usuarios WHERE LOWER(email) = LOWER(?)
                """, (email.strip(),))
                
                if cursor.fetchone():
                    st.error("Este e-mail já está cadastrado. Tente fazer login ou use outro e-mail.")
                    conn.close()
                    return False
                
                # Obter próximo user_id disponível
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
                    senha.strip(),
                    'usuario',  # Perfil padrão
                    empresa.strip() if empresa.strip() else None
                ))
                
                conn.commit()
                conn.close()
                
                # Registrar o cadastro no log
                registrar_acesso(
                    user_id=novo_user_id,
                    programa="main.py",
                    acao="cadastro_usuario"
                )
                
                st.success("✅ Usuário cadastrado com sucesso!")
                st.info("Agora você pode fazer login com suas credenciais.")
                
                # Limpar o formulário
                time.sleep(2)
                st.rerun()
                
                return True
                
            except Exception as e:
                st.error(f"Erro ao cadastrar usuário: {str(e)}")
                if 'conn' in locals():
                    conn.close()
                return False
    
    return False

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
        st.error(f"Banco de dados não encontrado em {DB_PATH}")
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
            
        st.markdown("""
            <p style='text-align: center; font-size: 35px;'>Plataforma Comportamental</p>
        """, unsafe_allow_html=True)
        
        # Tabs para Login e Cadastro
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])
        
        with tab1:
            # Formulário de login na área principal
            with st.form("login_form"):
                email = st.text_input("E-mail", key="email")
                password = st.text_input("Senha", type="password", key="password")

                aceite_termos = st.checkbox(
                    'Declaro que li e aceito os [termos de uso da ferramenta](https://ag93eventos.com.br/ear/Termos_Uso_DISC.pdf)',
                    key='aceite_termos'
                )

                login_button = st.form_submit_button("Entrar", use_container_width=True)
            
                if login_button:
                    if not aceite_termos:
                        st.warning("Você deve aceitar os termos de uso para continuar.")
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
                            st.error("E-mail ou senha inválidos. Por favor, verifique seus dados e tente novamente.")
        
        with tab2:
            # Formulário de cadastro
            cadastrar_usuario()

    return st.session_state.get("logged_in", False), st.session_state.get("user_profile", None)

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
    
    st.markdown("""
        <p style='text-align: center; font-size: 30px; font-weight: bold;'>As 7 Armadilhas do Eu Empresário</p>
        
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
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;">Propósito</p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>Esta ferramenta, desenvolvida por Erika Rossi da EAR Consultoria, tem como objetivo identificar sua vulnerabilidade em relação às Sete Armadilhas do Eu Empresário. Criada para palestras e grupos de empreendedores, ela fornece uma pontuação de risco que reflete o seu perfil em diversas dimensões da jornada empreendedora.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Coluna 2: Identidade
    with col2:
        st.markdown(f"""
            <div style="background-color: #53a7a9; padding: 20px; border-radius: 8px; height: 100%;">
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;"></p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>Esta é uma jornada de autoconhecimento prático que revela os pontos onde armadilhas como sobrecarga, solidão, dificuldades de delegação, dependência total do dono ou falta de tempo para o futuro podem estar impactando sua rotina e as decisões do seu negócio. As devolutivas são classificadas por níveis de risco (Baixo Risco, Atenção, Alto Risco ou Crítico), guiando você na reflexão sobre estes pontos para identificar áreas que merecem atenção e ajustes.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Coluna 3: Funções
    with col3:
        modulos_html = """
            <div style="background-color: #8eb0ae; padding: 20px; border-radius: 8px; height: 100%;">
                <p style="color: #ffffff; font-size: 24px; font-weight: bold;"></p>
                <div style="color: #ffffff; font-size: 16px;">
                    <p>Mais do que um diagnóstico, esta ferramenta é um ponto de partida essencial para fortalecer suas práticas, repensar processos, buscar apoio e criar estratégias mais sólidas. O objetivo é promover o equilíbrio entre vida pessoal e profissional, evitar a exaustão, a estagnação ou até a falência, e garantir a sustentabilidade e autonomia do seu negócio, transformando desafios em oportunidades de evolução com propósito.</p>
                    <p></p>                    
                    <p></p>                    
                </div>
            </div>
        """
        
        st.markdown(modulos_html, unsafe_allow_html=True)

def trocar_senha():
    """Função para permitir que o usuário logado troque sua senha"""
    
    st.markdown("""
        <p style='text-align: center; font-size: 30px; font-weight: bold;'>
            Trocar Senha
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background-color:#f0f0f0;padding:15px;border-radius:5px;margin-bottom:20px;'>
            <p style='font-size:16px;color:#333;'>
                <strong>Instruções:</strong><br>
                • Digite sua senha atual para confirmar sua identidade<br>
                • Digite a nova senha desejada<br>
                • Confirme a nova senha para evitar erros de digitação
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulário de troca de senha
    with st.form("trocar_senha_form"):
        senha_atual = st.text_input("Senha Atual", type="password", key="senha_atual")
        nova_senha = st.text_input("Nova Senha", type="password", key="nova_senha")
        confirmar_senha = st.text_input("Confirmar Nova Senha", type="password", key="confirmar_senha")
        
        submit_button = st.form_submit_button("Alterar Senha", use_container_width=True)
        
        if submit_button:
            # Validações
            if not senha_atual or not nova_senha or not confirmar_senha:
                st.error("Todos os campos são obrigatórios!")
                return
            
            if nova_senha != confirmar_senha:
                st.error("As senhas não coincidem! Digite a mesma senha nos dois campos.")
                return
            
            if nova_senha == senha_atual:
                st.error("A nova senha deve ser diferente da senha atual!")
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
                    st.error("Senha atual incorreta! Verifique e tente novamente.")
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
                
                st.success("✅ Senha alterada com sucesso!")
                st.info("A nova senha será válida no próximo login.")
                
                # Limpar os campos do formulário
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao alterar senha: {str(e)}")
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
        st.markdown("""
            <div style='background-color:#fff3cd;padding:10px;border-radius:5px;margin-bottom:15px;border-left:4px solid #ffc107;'>
                <p style='margin:0;font-size:14px;'>
                    <strong>🔍 Modo Administrativo:</strong> Visualizando análise de <strong>{}</strong>
                </p>
            </div>
        """.format(admin_user_name), unsafe_allow_html=True)
        
        # Botão para voltar ao módulo administrativo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️ **Voltar ao Módulo Administrativo**", use_container_width=True, type="secondary"):
                # Limpar dados administrativos
                st.session_state.pop("admin_view_user_id", None)
                st.session_state.pop("admin_view_user_name", None)
                
                # Definir flag para retornar ao módulo administrativo
                st.session_state["return_to_admin"] = True
                st.rerun()
        
        st.markdown("---")
        
        # Exibir análise do usuário selecionado
        show_results(
            tabela_escolhida="forms_resultados", 
            titulo_pagina=f"Análise Administrativa - {admin_user_name}", 
            user_id=admin_user_id
        )
    else:
        # Visualização normal do próprio usuário
        show_results(
            tabela_escolhida="forms_resultados", 
            titulo_pagina="Análise das Avaliações", 
            user_id=current_user_id
        )

def zerar_value_element():
    """Função para zerar todos os value_element do usuário logado na tabela forms_tab onde type_element é input, formula ou formulaH"""
    # Inicializa o estado do checkbox se não existir
    if 'confirma_zeragem' not in st.session_state:
        st.session_state.confirma_zeragem = False
    
    # Checkbox para confirmação
    confirma = st.checkbox("Confirmar zeragem dos valores?", 
                                 value=st.session_state.confirma_zeragem,
                                 key='confirma_zeragem')
    
    if st.button("Zerar Valores"):
        if confirma:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Atualiza value_element para 0.0 para os tipos especificados
                cursor.execute("""
                    UPDATE forms_tab 
                    SET value_element = 0.0 
                    WHERE user_id = ? 
                    AND value_element IS NOT NULL
                    AND type_element IN ('input', 'formula', 'formulaH', 'selectbox')
                """, (st.session_state["user_id"],))
                
                registros_afetados = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                # Registra a ação no monitor
                registrar_acesso(
                    user_id=st.session_state["user_id"],
                    programa="main.py",
                    acao="zerar_valores"
                )
                
                st.success(f"Valores zerados com sucesso! ({registros_afetados} registros atualizados)")
                
                # Força a atualização da página após 1 segundo
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao zerar valores: {str(e)}")
                if 'conn' in locals():
                    conn.close()
        else:
            st.warning("Confirme a operação para prosseguir")

def main():
    """Gerencia a navegação entre as páginas do sistema."""
    # Verifica se o diretório data existe
    if not DATA_DIR.exists():
        st.error(f"Pasta '{DATA_DIR}' não encontrada. O programa não pode continuar.")
        st.stop()
        
    # Verifica se o banco existe
    if not DB_PATH.exists():
        st.error(f"Banco de dados '{DB_PATH}' não encontrado. O programa não pode continuar.")
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
        st.markdown("""
            <p style='text-align: center; font-size: 30px; font-weight: bold;'>
                Plataforma CHAVE  - Desenvolvimento Humano, Automações com IA
            </p>
        """, unsafe_allow_html=True)
        with st.expander("Informações do Usuário / Logout", expanded=False):
            st.markdown(f"""
                **Usuário:** {st.session_state.get('user_name')}  
                **ID:** {st.session_state.get('user_id')}  
                **Perfil:** {st.session_state.get('user_profile')}
            """)
            if st.button("Logout"):
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
    
    # --- NAVEGAÇÃO ---
    
    # Mapeamento de páginas para suas funções de handler
    page_handlers = {
        "Bem-vindo": show_welcome,
        "Direta": lambda: process_forms_tab("fdireta"),
        "Invertida": lambda: process_forms_tab("finvertida"),
        "Resultados": lambda: process_forms_tab("resultado"),
        "das Avaliações": lambda: show_analysis_with_admin_controls(),
        "Info Tabelas (CRUD)": show_crud,
        "Monitor de Uso": show_monitor,
        "Diagnóstico": show_diagnostics,
        "Análises de Usuários": show_resultados_adm,
        "Trocar Senha": trocar_senha,
        "Zerar Valores": zerar_value_element,
    }
    
    # Criando grupos de menu
    menu_groups = {
        "Abertura": ["Bem-vindo"],
        "Avaliação": [
            "Direta",
            "Invertida",
            "Resultados"
        ],
        "Análise": [
            "das Avaliações",
        ],
        "Administração": []  # Iniciando vazio para adicionar itens na ordem correta
    }
    
    # Adicionar opções administrativas na ordem desejada
    if user_profile and user_profile.lower() in ["adm", "master"]:
        menu_groups["Administração"].append("Análises de Usuários")
    if user_profile and user_profile.lower() == "master":
        menu_groups["Administração"].append("Info Tabelas (CRUD)")
    if user_profile and user_profile.lower() == "master":
        menu_groups["Administração"].append("Diagnóstico")
    if user_profile and user_profile.lower() in ["adm", "master"]:
        menu_groups["Administração"].append("Monitor de Uso")
    # Adicionar Trocar Senha (disponível para todos os perfis)
    menu_groups["Administração"].append("Trocar Senha")
    # Adicionar Zerar Valores por último
    menu_groups["Administração"].append("Zerar Valores")
    
    # Se não houver opções de administração, remover o grupo
    if not menu_groups["Administração"]:
        menu_groups.pop("Administração")
    
    # Criar seletores de navegação na página principal
    nav_cols = st.columns(2)
    with nav_cols[0]:
        selected_group = st.selectbox(
            "Selecione o Módulo:",
            options=list(menu_groups.keys()),
            key="group_selection"
        )
    
    with nav_cols[1]:
        section = st.radio(
            "Selecione a Função:",
            menu_groups[selected_group],
            key="menu_selection",
            horizontal=True
        )

    # Verificar se há retorno ao módulo administrativo
    if st.session_state.get("return_to_admin", False):
        st.session_state["return_to_admin"] = False
        # Exibir módulo administrativo diretamente
        show_resultados_adm()
        return
    
    # Verificar se houve mudança de página
    if st.session_state.get("previous_page") != section:
        st.session_state["previous_page"] = section

    # Verificar se há redirecionamento pendente de análise administrativa
    if st.session_state.get("redirect_to_analysis", False):
        # Limpar flag de redirecionamento
        st.session_state["redirect_to_analysis"] = False
        
        # Exibir análise administrativa diretamente sem modificar widgets
        show_analysis_with_admin_controls()
        return
    
    # Processa a seção selecionada usando o dicionário de handlers
    handler = page_handlers.get(section)
    if handler:
        handler()
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
