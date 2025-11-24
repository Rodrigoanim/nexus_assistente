# resultados_04.py
# Data: 15/11/2025 
# Pagina de resultados e Analises - Dashboard.
# Tabela: forms_resultados_04

try:
    import reportlab
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        KeepTogether,
        PageBreak
    )
except ImportError as e:
    print(f"Erro ao importar ReportLab: {e}")

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import io
import tempfile
import matplotlib.pyplot as plt
import traceback
import re
import os
from paginas.monitor import registrar_acesso
import time

from config import DB_PATH  # Adicione esta importação

# Dicionário de títulos para cada tabela
TITULOS_TABELAS = {
    "forms_resultados_04": "Análise: Armadilhas do Empresário"
}

# Dicionário de subtítulos para cada tabela
SUBTITULOS_TABELAS = {
    "forms_resultados_04": "Análise:Armadilhas do Empresário"
}

def format_br_number(value):
    """
    Formata um número para o padrão brasileiro
    
    Args:
        value: Número a ser formatado
        
    Returns:
        str: Número formatado como string
        
    Notas:
        - Valores >= 1: sem casas decimais
        - Valores < 1: 3 casas decimais
        - Usa vírgula como separador decimal
        - Usa ponto como separador de milhar
        - Retorna "0" para valores None ou inválidos
    """
    try:
        if value is None:
            return "0"
        
        float_value = float(value)
        if abs(float_value) >= 1:
            return f"{float_value:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')  # Duas casas decimais com separador de milhar
        else:
            return f"{float_value:.3f}".replace('.', ',')  # 3 casas decimais
    except:
        return "0"

def parse_br_number(value):
    """
    Converte um valor em formato brasileiro (vírgula decimal) para float
    
    Args:
        value: Valor a ser convertido (string, float ou int)
        
    Returns:
        float: Valor convertido para float
        
    Notas:
        - Se valor já for float ou int, retorna diretamente
        - Se for string, trata formato brasileiro (vírgula como decimal)
        - Remove pontos de milhar e converte vírgula para ponto
        - Retorna 0.0 para valores inválidos
    """
    try:
        if value is None:
            return 0.0
        
        # Se já for float ou int, retorna diretamente
        if isinstance(value, (float, int)):
            return float(value)
        
        # Converte para string e remove espaços
        str_value = str(value).strip()
        
        # Se string vazia
        if not str_value:
            return 0.0
        
        # Remove pontos de milhar e substitui vírgula por ponto decimal
        str_value = str_value.replace('.', '').replace(',', '.')
        
        # Converte para float
        return float(str_value)
        
    except Exception as e:
        print(f"# Debug: Erro ao converter valor brasileiro '{value}': {str(e)}")
        return 0.0

def titulo(cursor, element):
    """
    Exibe títulos formatados na interface com base nos valores do banco de dados.
    """
    try:
        name = element[0]        # name_element
        type_elem = element[1]   # type_element
        msg = element[3]         # msg_element
        value = element[4]       # value_element (já é REAL do SQLite)
        str_value = element[6]   # str_element
        col = element[7]         # e_col
        row = element[8]         # e_row
        
        # Verifica se a coluna é válida
        if col > 6:
            st.error(f"Posição de coluna inválida para o título {name}: {col}. Deve ser entre 1 e 6.")
            return
        
        # Se for do tipo 'titulo', usa o str_element do próprio registro
        if type_elem == 'titulo':
            if str_value:
                # Se houver um valor numérico para exibir
                if value is not None:
                    # Formata o valor para o padrão brasileiro
                    value_br = format_br_number(value)
                    # Substitui {value} no str_value pelo valor formatado
                    str_value = str_value.replace('{value}', value_br)
                st.markdown(str_value, unsafe_allow_html=True)
            else:
                st.markdown(msg, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Erro ao processar título: {str(e)}")

def pula_linha(cursor, element):
    """
    Adiciona uma linha em branco na interface quando o type_element é 'pula linha'
    """
    try:
        type_elem = element[1]  # type_element
        
        if type_elem == 'pula linha':
            st.markdown("<br>", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Erro ao processar pula linha: {str(e)}")

def new_user(cursor, user_id: int, tabela: str):
    """
    Cria registros iniciais para um novo usuário na tabela especificada,
    copiando os dados do template (user_id = 0)
    
    Args:
        cursor: Cursor do banco de dados
        user_id: ID do usuário
        tabela: Nome da tabela para criar os registros
    """
    try:
        # Verifica se já existem registros para o usuário
        cursor.execute(f"""
            SELECT COUNT(*) FROM {tabela} 
            WHERE user_id = ?
        """, (user_id,))
        
        if cursor.fetchone()[0] == 0:
            # Copia dados do template (user_id = 0) para o novo usuário
            cursor.execute(f"""
                INSERT INTO {tabela} (
                    user_id, name_element, type_element, math_element,
                    msg_element, value_element, select_element, str_element,
                    e_col, e_row, section
                )
                SELECT 
                    ?, name_element, type_element, math_element,
                    msg_element, value_element, select_element, str_element,
                    e_col, e_row, section
                FROM {tabela}
                WHERE user_id = 0
            """, (user_id,))
            
            cursor.connection.commit()
            st.success("Dados iniciais criados com sucesso!")
            
    except Exception as e:
        st.error(f"Erro ao criar dados do usuário: {str(e)}")

def call_dados(cursor, element, tabela_destino: str):
    """
    Busca dados na tabela forms_tab_04 e atualiza o value_element do registro atual.
    
    Args:
        cursor: Cursor do banco de dados
        element: Tupla com dados do elemento
        tabela_destino: Nome da tabela onde o valor será atualizado
    """
    try:
        name = element[0]        # name_element
        type_elem = element[1]   # type_element
        str_value = element[6]   # str_element
        user_id = element[10]    # user_id
        
        if type_elem == 'call_dados':
            # Busca o valor com CAST para garantir precisão decimal
            cursor.execute("""
                SELECT CAST(value_element AS DECIMAL(20, 8))
                FROM forms_tab_04 
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (str_value, user_id))
            
            result = cursor.fetchone()
            
            if result:
                value = float(result[0]) if result[0] is not None else 0.0
                
                # Atualiza usando a tabela passada como parâmetro
                cursor.execute(f"""
                    UPDATE {tabela_destino}
                    SET value_element = CAST(? AS DECIMAL(20, 8))
                    WHERE name_element = ? 
                    AND user_id = ?
                """, (value, name, user_id))
                
                cursor.connection.commit()
            else:
                st.warning(f"Valor não encontrado na tabela forms_tab_04 para {str_value} (user_id: {user_id})")
                
    except Exception as e:
        st.error(f"Erro ao processar call_dados: {str(e)}")

def grafico_barra(cursor, element):
    """
    Cria um gráfico de barras verticais com dados da tabela específica.
    
    Args:
        cursor: Cursor do banco de dados SQLite
        element: Tupla contendo os dados do elemento tipo 'grafico'
            [0] name_element: Nome do elemento
            [1] type_element: Tipo do elemento (deve ser 'grafico')
            [3] msg_element: Título/mensagem do gráfico
            [5] select_element: Lista de type_names separados por '|'
            [6] str_element: Lista de rótulos separados por '|'
            [9] section: Cor do gráfico (formato hex)
            [10] user_id: ID do usuário
    
    Configurações do Gráfico:
        - Título do gráfico usando msg_element
        - Barras verticais sem hover (tooltip)
        - Altura fixa de 400px
        - Largura responsiva
        - Sem legenda e títulos dos eixos
        - Fonte tamanho 14px
        - Valores no eixo Y formatados com separador de milhar
        - Cor das barras definida pela coluna 'section'
        - Sem barra de ferramentas do Plotly
    """
    try:
        # Extrai informações do elemento
        type_elem = element[1]   # type_element
        msg = element[3]         # msg_element (título do gráfico)
        select = element[5]      # select_element
        rotulos = element[6]     # str_element
        section = element[9]     # section (cor do gráfico)
        user_id = element[10]    # user_id
        
        # Validação do tipo e dados necessários
        if type_elem != 'grafico':
            return
            
        if not select or not rotulos:
            st.error("Configuração incompleta do gráfico: select ou rótulos vazios")
            return
            
        # Processa as listas de type_names e rótulos
        type_names = select.split('|')
        labels = rotulos.split('|')
        
        # Lista para armazenar os valores
        valores = []
        
        # Busca os valores para cada type_name no banco
        for type_name in type_names:
            tabela = st.session_state.tabela_escolhida
            cursor.execute(f"""
                SELECT value_element 
                FROM {tabela}
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (type_name.strip(), user_id))
            
            result = cursor.fetchone()
            valor = result[0] if result and result[0] is not None else 0.0
            valores.append(valor)
        
        # Define as cores fixas para cada posição DISC (D, I, S, C)
        cores_disc = ['#B22222', '#DAA520', '#2E8B57', '#4682B4']
        
        # Aplica as cores pela posição (ordem das barras)
        cores = []
        for i in range(len(labels)):
            if i < len(cores_disc):
                cores.append(cores_disc[i])
            else:
                cores.append('#1f77b4')  # cor padrão se houver mais de 4 barras
        

        # Adiciona o título antes do gráfico usando markdown
        if msg:
            st.markdown(f"""
                <p style='
                    text-align: center;
                    font-size: 31px;
                    font-weight: bold;
                    color: #1E1E1E;
                    margin: 15px 0;
                    padding: 10px;
                '>{msg}</p>
            """, unsafe_allow_html=True)
        
        # Cria o gráfico usando Graph Objects para controle total das cores
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=valores,
                marker=dict(color=cores),  # Define cores diretamente
                showlegend=False
            )
        ])
        
        # Configura o layout do gráfico
        fig.update_layout(
            # Remove títulos dos eixos
            xaxis_title=None,
            yaxis_title=None,
            # Remove legenda
            showlegend=False,
            # Define dimensões
            height=400,
            width=None,  # largura responsiva
            # Configuração do eixo X
            xaxis=dict(
                tickfont=dict(size=16),  # mantido tamanho original para web
            ),
            # Configuração do eixo Y
            yaxis=dict(
                tickfont=dict(size=18),  # mantido tamanho original para web
                tickformat=",.",  # formato dos números
                separatethousands=True  # separador de milhar
            ),
            # Desativa o hover (tooltip ao passar o mouse)
            hovermode=False
        )
        
        # Exibe o gráfico no Streamlit com chave única para evitar conflitos de ID
        # config={'displayModeBar': False} remove a barra de ferramentas do Plotly
        name_element = element[0]  # Usa o name_element como chave única
        graph_key = f"grafico_{name_element}_{user_id}"  # Chave única baseada no elemento e usuário
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=graph_key)
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")

def tabela_dados(cursor, element):
    """
    Cria uma tabela estilizada com dados da tabela forms_resultados_04.
    Tabela transposta (vertical) com valores em vez de nomes.
    
    Args:
        cursor: Conexão com o banco de dados
        element: Tupla com os dados do elemento tipo 'tabela'
        
    Configurações do elemento:
        type_element: 'tabela'
        msg_element: título da tabela
        math_element: número de colunas da tabela
        select_element: type_names separados por | (ex: 'N24|N25|N26')
        str_element: rótulos separados por | (ex: 'Energia|Água|GEE')
        
    Nota: 
        - Layout usando três colunas do Streamlit para centralização
        - Proporção de colunas: [1, 8, 1] (10% vazio, 80% tabela, 10% vazio)
        - Valores formatados no padrão brasileiro
        - Tabela transposta (vertical) para melhor leitura
        - Coluna 'Valor' com largura aumentada em 25%
    """
    try:
        # Extrai informações do elemento
        type_elem = element[1]   # type_element
        msg = element[3]         # msg_element (título da tabela)
        select = element[5]      # select_element (type_names separados por |)
        rotulos = element[6]     # str_element (rótulos separados por |)
        user_id = element[10]    # user_id
        
        if type_elem != 'tabela':
            return
            
        # Validações iniciais
        if not select or not rotulos:
            st.error("Configuração incompleta da tabela: select ou rótulos vazios")
            return
            
        # Separa os type_names e rótulos
        type_names = select.split('|')
        rotulos = rotulos.split('|')
        
        # Valida se quantidade de rótulos corresponde aos type_names
        if len(type_names) != len(rotulos):
            st.error("Número de rótulos diferente do número de valores")
            return
            
        # Lista para armazenar os valores
        valores = []
        
        # Busca os valores para cada type_name
        for type_name in type_names:
            cursor.execute("""
                SELECT value_element 
                FROM forms_resultados_04_04 
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (type_name.strip(), user_id))
            
            result = cursor.fetchone()
            valor = format_br_number(result[0]) if result and result[0] is not None else '0,00'
            valores.append(valor)
        
        # Criar DataFrame com os dados
        df = pd.DataFrame({
            'Indicador': rotulos,
            'Valor': valores
        })
        
        # Criar três colunas, usando a do meio para a tabela
        col1, col2, col3 = st.columns([1, 8, 1])
        
        with col2:
            # Espaçamento fixo definido no código
            spacing = 20  # valor em pixels ajustado conforme solicitado
            
            # Adiciona quebras de linha antes do título
            num_breaks = spacing // 20
            for _ in range(num_breaks):
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Exibe o título da tabela a esquerda
            st.markdown(f"<h4 style='text-align: left;'>{msg}</h4>", unsafe_allow_html=True)
            
            # Criar HTML da tabela com estilos inline
            html_table = f"""
            <div style='font-size: 20px; width: 80%;'>
                <table style='width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 10px; overflow: hidden; box-shadow: 0 0 8px rgba(0,0,0,0.1);'>
                    <thead>
                        <tr>
                            <th style='text-align: left; padding: 10px; background-color: #e8f5e9; border-bottom: 2px solid #dee2e6;'>Indicador</th>
                            <th style='text-align: right; padding: 10px; background-color: #e8f5e9; border-bottom: 2px solid #dee2e6;'>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td style='padding: 8px 10px; border-bottom: 1px solid #dee2e6;'>{row['Indicador']}</td><td style='text-align: right; padding: 8px 10px; border-bottom: 1px solid #dee2e6;'>{row['Valor']}</td></tr>" for _, row in df.iterrows())}
                    </tbody>
                </table>
            </div>
            """
            
            # Exibe a tabela HTML
            st.markdown(html_table, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao criar tabela: {str(e)}")

def gerar_dados_tabela(cursor, elemento, height_pct=100, width_pct=100):
    """
    Função auxiliar para gerar dados da tabela para o PDF
    """
    try:
        msg = elemento[3]         # msg_element
        select = elemento[5]      # select_element
        rotulos = elemento[6]     # str_element
        user_id = elemento[10]    # user_id
        
        if not select or not rotulos:
            st.error("Configuração incompleta da tabela: select ou rótulos vazios")
            return None
            
        # Separa os type_names e rótulos
        type_names = str(select).split('|')
        labels = str(rotulos).split('|')
        valores = []
        
        # Busca os valores para cada type_name
        for type_name in type_names:
            cursor.execute(f"""
                SELECT name_element, value_element 
                FROM {st.session_state.tabela_escolhida}
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (type_name.strip(), user_id))
            
            result = cursor.fetchone()
            valor = format_br_number(result[1]) if result and result[1] is not None else '0,00'
            valores.append(valor)
        
        # Retornar dados formatados para a tabela
        return {
            'title': msg if msg else "Tabela de Dados",
            'data': [['Indicador', 'Valor']] + list(zip(labels, valores)),
            'height_pct': height_pct,
            'width_pct': width_pct
        }
        
    except Exception as e:
        st.error(f"Erro ao gerar dados da tabela: {str(e)}")
        return None

def gerar_dados_grafico(cursor, elemento, tabela_escolhida: str, height_pct=100, width_pct=100):
    try:
        msg = elemento[3]         # msg_element
        select = elemento[5]      # select_element
        rotulos = elemento[6]     # str_element
        section = elemento[9]     # section (cor do gráfico)
        user_id = elemento[10]    # user_id
        if not select or not rotulos:
            return None
        type_names = str(select).split('|')
        labels = str(rotulos).split('|')
        valores = []
        # Busca os valores para cada type_name
        for type_name in type_names:
            cursor.execute(f"""
                SELECT value_element 
                FROM {tabela_escolhida}
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (type_name.strip(), user_id))
            result = cursor.fetchone()
            valor = float(result[0]) if result and result[0] is not None else 0.0
            valores.append(valor)
        # Define as cores fixas para cada posição DISC (D, I, S, C)
        cores_disc = ['#B22222', '#DAA520', '#2E8B57', '#4682B4']
        
        # Aplica as cores pela posição (ordem das barras)
        cores = []
        for i in range(len(labels)):
            if i < len(cores_disc):
                cores.append(cores_disc[i])
            else:
                cores.append('#1f77b4')  # cor padrão se houver mais de 4 barras
        # Ajustar base_width para ocupar mais da largura da página A4
        base_width = 250
        base_height = 180
        # largura dos gráficos igual à tabela (usando width_pct)
        adj_width = int(base_width * 2.2 * 0.8 * (width_pct / 100)) + 20  # aumenta 20 na largura
        adj_height = int(base_height * (height_pct / 100)) - 25           # reduz 25 na altura
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=valores,
                marker=dict(color=cores),  # Define cores diretamente
                showlegend=False
            )
        ])
        fig.update_layout(
            showlegend=False,
            height=int(adj_height * 1.5),  # aumentado 50% na altura
            width=adj_width,
            margin=dict(t=30, b=50),
            xaxis=dict(
                title=None,
                tickfont=dict(size=8)  # reduzido 50% (de 16 para 8)
            ),
            yaxis=dict(
                title=None,
                tickfont=dict(size=9),  # reduzido 50% (de 18 para 9)
                tickformat=",.",
                separatethousands=True
            )
        )
        img_bytes = fig.to_image(format="png", scale=3)
        return {
            'title': msg,
            'image': Image(io.BytesIO(img_bytes), 
                         width=adj_width,
                         height=adj_height)
        }
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None

def subtitulo(titulo_pagina: str):
    """
    Exibe o subtítulo da página e o botão de gerar PDF (temporariamente desabilitado)
    """
    try:
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"""
                <p style='
                    text-align: Left;
                    font-size: 36px;
                    color: #000000;
                    margin-top: 10px;
                    margin-bottom: 30px;
                    font-family: sans-serif;
                    font-weight: 500;
                '>{titulo_pagina}</p>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Gerar PDF", type="primary", key="btn_gerar_pdf"):
                try:
                    msg_placeholder = st.empty()
                    msg_placeholder.info("Gerando PDF... Por favor, aguarde.")
                    
                    for _ in range(3):
                        try:
                            conn = sqlite3.connect(DB_PATH, timeout=20)
                            cursor = conn.cursor()
                            break
                        except sqlite3.OperationalError as e:
                            if "database is locked" in str(e):
                                time.sleep(1)
                                continue
                            raise e
                    else:
                        st.error("Não foi possível conectar ao banco de dados. Tente novamente.")
                        return
                    
                    buffer = generate_pdf_content(
                        cursor, 
                        st.session_state.user_id,
                        st.session_state.tabela_escolhida
                    )
                    
                    if buffer:
                        conn.close()
                        msg_placeholder.success("PDF gerado com sucesso!")
                        st.download_button(
                            label="Baixar PDF",
                            data=buffer.getvalue(),
                            file_name="Armadilhas_Empresario_Analise.pdf",
                            mime="application/pdf",
                        )
                    
                except Exception as e:
                    msg_placeholder.error(f"Erro ao gerar PDF: {str(e)}")
                    st.write("Debug: Stack trace completo:", traceback.format_exc())
                finally:
                    if 'conn' in locals() and conn:
                        conn.close()
                    
    except Exception as e:
        st.error(f"Erro ao gerar interface: {str(e)}")

def generate_pdf_content(cursor, user_id: int, tabela_escolhida: str):
    """
    Função para gerar PDF com layout específico: 
    Tabela Perfil → Gráfico Perfil → Tabela Comportamento → Gráfico Comportamento
    """
    try:
        # Configurações de dimensões
        base_width = 400  # largura base para tabelas e gráficos
        base_height = 200 # altura base
        table_width = base_width * 0.8  # largura da tabela
        graph_width = base_width        # largura do gráfico

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        with sqlite3.connect(DB_PATH, timeout=20) as pdf_conn:
            pdf_cursor = pdf_conn.cursor()
            elements = []
            styles = getSampleStyleSheet()

            # Estilos para o PDF
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=26,
                alignment=1,
                textColor=colors.HexColor('#1E1E1E'),
                fontName='Helvetica',
                leading=26,
                spaceBefore=15,
                spaceAfter=20
            )
            
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 16),
                ('TOPPADDING', (0, 1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ])
            
            graphic_title_style = ParagraphStyle(
                'GraphicTitle',
                parent=styles['Heading2'],
                fontSize=18,
                alignment=1,
                textColor=colors.HexColor('#1E1E1E'),
                fontName='Helvetica',
                leading=16,
                spaceBefore=6,
                spaceAfter=8
            )

            # Título principal
            titulo_principal = TITULOS_TABELAS.get(tabela_escolhida, "Análise DISC")
            elements.append(Paragraph(titulo_principal, title_style))
            elements.append(Spacer(1, 20))

            # Buscar todos os elementos (tabelas e gráficos)
            pdf_cursor.execute(f"""
                SELECT name_element, type_element, math_element, msg_element,
                       value_element, select_element, str_element, e_col, e_row,
                       section, user_id
                FROM {tabela_escolhida}
                WHERE (type_element = 'tabela' OR type_element = 'grafico')
                AND user_id = ?
                ORDER BY e_row, e_col
            """, (user_id,))
            elementos = pdf_cursor.fetchall()

            # Separar tabelas e gráficos
            tabelas = [e for e in elementos if e[1] == 'tabela']
            graficos = [e for e in elementos if e[1] == 'grafico']

            # Layout específico: Tabela Perfil → Gráfico Perfil → Tabela Comportamento → Gráfico Comportamento
            
            # 1. TABELA PERFIL (primeira tabela encontrada)
            if len(tabelas) > 0:
                tabela_perfil = tabelas[0]
                dados_tabela_perfil = gerar_dados_tabela(pdf_cursor, tabela_perfil, height_pct=100, width_pct=100)
                if dados_tabela_perfil:
                    # Cria tabela com título "Resultados do Perfil"
                    elements.append(Paragraph("Resultados do Perfil", graphic_title_style))
                    elements.append(Spacer(1, 10))
                    t = Table(dados_tabela_perfil['data'], colWidths=[table_width * 0.6, table_width * 0.4])
                    t.setStyle(table_style)
                    elements.append(Table([[t]], colWidths=[table_width], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
                    elements.append(Spacer(1, 20))

            # 2. GRÁFICO PERFIL (primeiro gráfico encontrado)
            if len(graficos) > 0:
                grafico_perfil = graficos[0]
                dados_grafico_perfil = gerar_dados_grafico(pdf_cursor, grafico_perfil, tabela_escolhida, height_pct=100, width_pct=100)
                if dados_grafico_perfil:
                    # Usa o título do próprio gráfico ou padrão
                    titulo_grafico = dados_grafico_perfil['title'] or "RESULTADOS DE PERFIS"
                    elements.append(Paragraph(titulo_grafico, graphic_title_style))
                    elements.append(Spacer(1, 10))
                    elements.append(Table(
                        [[dados_grafico_perfil['image']]],
                        colWidths=[graph_width],
                        style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]
                    ))
                    elements.append(Spacer(1, 30))

            # 3. TABELA COMPORTAMENTO (segunda tabela ou cópia da primeira)
            if len(tabelas) > 1:
                tabela_comportamento = tabelas[1]
            else:
                tabela_comportamento = tabelas[0] if tabelas else None
                
            if tabela_comportamento:
                dados_tabela_comportamento = gerar_dados_tabela(pdf_cursor, tabela_comportamento, height_pct=100, width_pct=100)
                if dados_tabela_comportamento:
                    # Cria tabela com título "Resultados do Comportamento"
                    elements.append(Paragraph("Resultados do Comportamento", graphic_title_style))
                    elements.append(Spacer(1, 10))
                    t = Table(dados_tabela_comportamento['data'], colWidths=[table_width * 0.6, table_width * 0.4])
                    t.setStyle(table_style)
                    elements.append(Table([[t]], colWidths=[table_width], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
                    elements.append(Spacer(1, 20))

            # 4. GRÁFICO COMPORTAMENTO (segundo gráfico ou cópia do primeiro)
            if len(graficos) > 1:
                grafico_comportamento = graficos[1]
            else:
                grafico_comportamento = graficos[0] if graficos else None
                
            if grafico_comportamento:
                dados_grafico_comportamento = gerar_dados_grafico(pdf_cursor, grafico_comportamento, tabela_escolhida, height_pct=100, width_pct=100)
                if dados_grafico_comportamento:
                    # Força o título para "RESULTADOS DE COMPORTAMENTO"
                    elements.append(Paragraph("RESULTADOS DE COMPORTAMENTO", graphic_title_style))
                    elements.append(Spacer(1, 10))
                    elements.append(Table(
                        [[dados_grafico_comportamento['image']]],
                        colWidths=[graph_width],
                        style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]
                    ))
                    elements.append(Spacer(1, 20))

            # 5. ANÁLISE DETALHADA DO ASSESSMENT
            try:
                analise_texto = analisar_vulnerabilidade_7armadilhas(pdf_cursor, user_id, tabela_escolhida)
                # Verificar se a análise retornou conteúdo válido (não apenas mensagem de erro)
                if analise_texto and not analise_texto.startswith("Análise não disponível"):
                    # Adicionar título da seção
                    elements.append(PageBreak())
                    elements.append(Paragraph("Análise Detalhada do Assessment", title_style))
                    elements.append(Spacer(1, 20))
                    
                    # Converter HTML/Markdown para texto simples para o PDF
                    # Remove tags HTML mas preserva estrutura básica
                    texto_limpo = analise_texto
                    # Remove tags HTML complexas mas preserva quebras de linha
                    texto_limpo = re.sub(r'<br\s*/?>', '\n', texto_limpo, flags=re.IGNORECASE)
                    texto_limpo = re.sub(r'</p>', '\n\n', texto_limpo, flags=re.IGNORECASE)
                    texto_limpo = re.sub(r'</div>', '\n', texto_limpo, flags=re.IGNORECASE)
                    texto_limpo = re.sub(r'<[^>]+>', '', texto_limpo)
                    # Remove emojis mas preserva pontuação básica
                    texto_limpo = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\/\n\r\'\"]', '', texto_limpo)
                    # Normaliza quebras de linha
                    texto_limpo = re.sub(r'\n{3,}', '\n\n', texto_limpo)
                    texto_limpo = texto_limpo.strip()
                    
                    # Dividir em parágrafos e adicionar ao PDF
                    paragrafos = [p.strip() for p in texto_limpo.split('\n\n') if p.strip() and len(p.strip()) > 10]
                    
                    # Estilos para diferentes níveis de texto
                    analise_style = ParagraphStyle(
                        'AnaliseStyle',
                        parent=styles['Normal'],
                        fontSize=10,
                        alignment=0,  # Justificado à esquerda
                        textColor=colors.HexColor('#1E1E1E'),
                        fontName='Helvetica',
                        leading=12,
                        spaceBefore=6,
                        spaceAfter=6
                    )
                    
                    titulo_secao_style = ParagraphStyle(
                        'TituloSecaoStyle',
                        parent=styles['Heading2'],
                        fontSize=14,
                        alignment=0,
                        textColor=colors.HexColor('#1E1E1E'),
                        fontName='Helvetica-Bold',
                        leading=16,
                        spaceBefore=12,
                        spaceAfter=8
                    )
                    
                    for paragrafo in paragrafos:
                        if paragrafo:
                            # Identificar títulos (linhas curtas ou que começam com ##)
                            if paragrafo.startswith('##') or (len(paragrafo) < 80 and paragrafo.isupper()):
                                # É um título
                                titulo_limpo = paragrafo.replace('##', '').strip()
                                if titulo_limpo:
                                    elements.append(Paragraph(titulo_limpo, titulo_secao_style))
                                    elements.append(Spacer(1, 8))
                            else:
                                # É um parágrafo normal
                                # Limitar tamanho do parágrafo para evitar problemas
                                if len(paragrafo) > 800:
                                    # Dividir parágrafos muito longos em frases
                                    frases = re.split(r'[.!?]\s+', paragrafo)
                                    for frase in frases:
                                        if frase.strip():
                                            elements.append(Paragraph(frase.strip() + '.', analise_style))
                                            elements.append(Spacer(1, 4))
                                else:
                                    elements.append(Paragraph(paragrafo, analise_style))
                                    elements.append(Spacer(1, 6))
            except Exception as e:
                # Se houver erro ao gerar a análise, continua sem ela
                print(f"Erro ao adicionar análise ao PDF: {str(e)}")
                pass

            doc.build(elements)
            return buffer
    except Exception as e:
        st.error(f"Erro ao gerar conteúdo do PDF: {str(e)}")
        return None

def show_results(tabela_escolhida: str, titulo_pagina: str, user_id: int):
    """
    Função principal para exibir a interface web
    """
    try:
        if not user_id:
            st.error("Usuário não está logado!")
            return
            
        # Armazena a tabela na sessão para uso em outras funções
        st.session_state.tabela_escolhida = tabela_escolhida
        
        # Adiciona o subtítulo antes do conteúdo principal
        subtitulo(titulo_pagina)
        
        # Estabelece conexão com retry
        for _ in range(3):
            try:
                conn = sqlite3.connect(DB_PATH, timeout=20)
                cursor = conn.cursor()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(1)
                    continue
                raise e
        else:
            st.error("Não foi possível conectar ao banco de dados. Tente novamente.")
            return
            
        # 1. Verifica/inicializa dados na tabela escolhida
        new_user(cursor, user_id, tabela_escolhida)
        conn.commit()
        
        # 2. Registra acesso à página
        registrar_acesso(
            user_id,
            "resultados",
            f"Acesso na simulação {titulo_pagina}"
        )

        # Configuração para esconder elementos durante a impressão e controlar quebra de página
        hide_streamlit_style = """
            <style>
                @media print {
                    [data-testid="stSidebar"] {
                        display: none !important;
                    }
                    .stApp {
                        margin: 0;
                        padding: 0;
                    }
                    #MainMenu {
                        display: none !important;
                    }
                    .page-break {
                        page-break-before: always !important;
                    }
                }
            </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        
        # Buscar todos os elementos ordenados por row e col
        cursor.execute(f"""
            SELECT name_element, type_element, math_element, msg_element,
                   value_element, select_element, str_element, e_col, e_row,
                   section, user_id
            FROM {tabela_escolhida}
            WHERE (type_element = 'titulo' OR type_element = 'pula linha' 
                  OR type_element = 'call_dados' OR type_element = 'grafico'
                  OR type_element = 'tabela')
            AND user_id = ?
            ORDER BY e_row, e_col
        """, (user_id,))
        
        elements = cursor.fetchall()
        
        # Contador para gráficos
        grafico_count = 0
        
        # Agrupar elementos por e_row
        row_elements = {}
        for element in elements:
            e_row = element[8]  # e_row do elemento
            if e_row not in row_elements:
                row_elements[e_row] = []
            row_elements[e_row].append(element)
        
        # Processar elementos por linha
        for e_row in sorted(row_elements.keys()):
            row_data = row_elements[e_row]
            
            # Primeiro processar tabelas em container separado
            tabelas = [elem for elem in row_data if elem[1] == 'tabela']
            for tabela in tabelas:
                with st.container():
                    # Centralizar a tabela usando colunas
                    col1, col2, col3 = st.columns([1, 8, 1])
                    with col2:
                        tabela_dados_sem_titulo(cursor, tabela)
            
            # Depois processar outros elementos em duas colunas
            graficos_na_linha = [elem for elem in row_data if elem[1] == 'grafico']
            for grafico in graficos_na_linha:
                grafico_count += 1
                grafico_barra(cursor, grafico)
                if grafico_count == 2:
                    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

            outros_elementos = [elem for elem in row_data if elem[1] not in ('tabela', 'grafico')]
            if outros_elementos:
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    # Processar elementos não-tabela e não-gráfico
                    for element in outros_elementos:
                        e_col = element[7]  # e_col do elemento
                        
                        if e_col <= 3:
                            with col1:
                                if element[1] == 'titulo':
                                    titulo(cursor, element)
                                elif element[1] == 'pula linha':
                                    pula_linha(cursor, element)
                                elif element[1] == 'call_dados':
                                    call_dados(cursor, element, tabela_escolhida)
                        else:
                            with col2:
                                if element[1] == 'titulo':
                                    titulo(cursor, element)
                                elif element[1] == 'pula linha':
                                    pula_linha(cursor, element)
                                elif element[1] == 'call_dados':
                                    call_dados(cursor, element, tabela_escolhida)
        
        # 5. Gerar e exibir a análise 7 Armadilhas
        with st.expander("Análise Detalhada do Assessment", expanded=True):
            st.markdown("---")
            
            # Chama a função que gera e exibe a análise diretamente
            analisar_vulnerabilidade_7armadilhas_streamlit(cursor, user_id)
            
            st.markdown("---")

    except Exception as e:
        st.error(f"Erro ao carregar resultados: {str(e)}")
    finally:
        if conn:
            conn.close()

def tabela_dados_sem_titulo(cursor, element):
    """Versão da função tabela_dados sem o título"""
    try:
        type_elem = element[1]   # type_element
        select = element[5]      # select_element
        rotulos = element[6]     # str_element
        user_id = element[10]    # user_id
        
        if type_elem != 'tabela':
            return
            
        # Validações iniciais
        if not select or not rotulos:
            st.error("Configuração incompleta da tabela: select ou rótulos vazios")
            return
            
        # Separa os type_names e rótulos
        type_names = select.split('|')
        rotulos = rotulos.split('|')
        
        # Valida se quantidade de rótulos corresponde aos type_names
        if len(type_names) != len(rotulos):
            st.error("Número de rótulos diferente do número de valores")
            return
            
        # Lista para armazenar os valores
        valores = []
        
        # Busca os valores para cada type_name
        for type_name in type_names:
            tabela = st.session_state.tabela_escolhida  # Pega a tabela da sessão
            cursor.execute(f"""
                SELECT value_element 
                FROM {tabela}
                WHERE name_element = ? 
                AND user_id = ?
                ORDER BY ID_element DESC
                LIMIT 1
            """, (type_name.strip(), user_id))
            
            result = cursor.fetchone()
            valor = format_br_number(result[0]) if result and result[0] is not None else '0,00'
            valores.append(valor)
        
        # Criar DataFrame com os dados
        df = pd.DataFrame({
            'Indicador': rotulos,
            'Valor': valores
        })
        
        # Criar três colunas, usando a do meio para a tabela
        col1, col2, col3 = st.columns([1, 8, 1])
        
        with col2:
            # Criar HTML da tabela com estilos inline (sem o título)
            html_table = f"""
            <div style='font-size: 20px; width: 80%;'>
                <table style='width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 10px; overflow: hidden; box-shadow: 0 0 8px rgba(0,0,0,0.1);'>
                    <thead>
                        <tr>
                            <th style='text-align: left; padding: 10px; background-color: #e8f5e9; border-bottom: 2px solid #dee2e6;'>Indicador</th>
                            <th style='text-align: right; padding: 10px; background-color: #e8f5e9; border-bottom: 2px solid #dee2e6;'>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td style='padding: 8px 10px; border-bottom: 1px solid #dee2e6;'>{row['Indicador']}</td><td style='text-align: right; padding: 8px 10px; border-bottom: 1px solid #dee2e6;'>{row['Valor']}</td></tr>" for _, row in df.iterrows())}
                    </tbody>
                </table>
            </div>
            """
            
            # Exibe a tabela HTML
            st.markdown(html_table, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao criar tabela: {str(e)}")

def analisar_vulnerabilidade_7armadilhas_streamlit(cursor, user_id):
    """
    Gera análise de vulnerabilidade das 7 Armadilhas do Eu Empresário na interface Streamlit.
    FUNÇÃO ATUALIZADA - Implementa lógica das 7 Armadilhas.
    """
    try:
        # 1. Buscar dados do usuário
        cursor.execute("""
            SELECT u.nome, u.email, u.empresa 
            FROM usuarios u 
            WHERE u.user_id = ?
        """, (user_id,))
        usuario_info = cursor.fetchone()
        
        # 2. Buscar pontuação das perguntas diretas (M3000)
        cursor.execute("""
            SELECT value_element
            FROM forms_resultados_04
            WHERE user_id = ? AND str_element = 'M3000'
            LIMIT 1
        """, (user_id,))
        result_diretas = cursor.fetchone()
        pontuacao_diretas = float(result_diretas[0]) if result_diretas and result_diretas[0] is not None else 0.0
        
        # 3. Buscar pontuação das perguntas invertidas (N3000)
        cursor.execute("""
            SELECT value_element
            FROM forms_resultados_04
            WHERE user_id = ? AND str_element = 'N3000'
            LIMIT 1
        """, (user_id,))
        result_invertidas = cursor.fetchone()
        pontuacao_invertidas = float(result_invertidas[0]) if result_invertidas and result_invertidas[0] is not None else 0.0
        
        # 4. Calcular vulnerabilidade total
        vulnerabilidade_total = pontuacao_diretas + pontuacao_invertidas
        
        # 5. Determinar faixa de risco e arquivo correspondente
        if vulnerabilidade_total <= 7:
            faixa_risco = "Baixo Risco"
            arquivo_markdown = "1_BaixoRisco.md"
            cor_faixa = "#2E8B57"  # Verde
        elif vulnerabilidade_total <= 14:
            faixa_risco = "Atenção"
            arquivo_markdown = "2_Atencao.md"
            cor_faixa = "#DAA520"  # Amarelo
        elif vulnerabilidade_total <= 21:
            faixa_risco = "Alto Risco"
            arquivo_markdown = "3_AltoRisco.md"
            cor_faixa = "#FF8C00"  # Laranja
        else:
            faixa_risco = "Risco Crítico"
            arquivo_markdown = "4_RiscoCritico.md"
            cor_faixa = "#B22222"  # Vermelho
        
        # 6. Validação: se não encontrou dados
        if not result_diretas and not result_invertidas:
            st.markdown("## ⚠️ Análise de Vulnerabilidade não disponível")
            st.markdown("### 👤 Informações do Usuário:")
            if usuario_info:
                st.markdown(f"**Nome:** {usuario_info[0] or 'Não informado'}")
                st.markdown(f"**Email:** {usuario_info[1] or 'Não informado'}")
                st.markdown(f"**Empresa:** {usuario_info[2] or 'Não informado'}")
            st.markdown("**Problema:** Dados de vulnerabilidade não encontrados para este usuário.")
            return

        # 7. Exibir análise de vulnerabilidade
        st.markdown("## 📊 Análise de Vulnerabilidade - 7 Armadilhas do Eu Empresário")
        st.markdown("### 👤 Informações do Participante")
        
        # Exibir dados do usuário
        if usuario_info:
            info_html = f"""
            <div style='background-color: #f0f8ff; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #0066cc;'>
                <p style='margin: 0; font-size: 16px;'>
                    <strong>👤 Nome:</strong> {usuario_info[0] or 'Não informado'}<br>
                    <strong>📧 Email:</strong> {usuario_info[1] or 'Não informado'}<br>
                    <strong>🏢 Empresa:</strong> {usuario_info[2] or 'Não informado'}
                </p>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
        
        # 8. Exibir pontuações e vulnerabilidade total
        st.markdown("### 📈 Pontuações de Vulnerabilidade")
        
        # Criar colunas para exibir as pontuações
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Perguntas Diretas",
                value=f"{pontuacao_diretas:.1f}",
                help="Soma das 7 perguntas diretas (M3000)"
            )
        
        with col2:
            st.metric(
                label="Perguntas Invertidas", 
                value=f"{pontuacao_invertidas:.1f}",
                help="Soma das 7 perguntas invertidas (N3000)"
            )
        
        with col3:
            st.metric(
                label="Vulnerabilidade Total",
                value=f"{vulnerabilidade_total:.1f}",
                help="Soma total (0-28 pontos)"
            )
        
        # 9. Exibir faixa de risco
        st.markdown("### 🎯 Classificação de Risco")
        
        risco_html = f"""
        <div style='background-color: {cor_faixa}; color: white; padding: 20px; margin: 15px 0; border-radius: 8px; text-align: center;'>
            <h2 style='margin: 0; font-size: 24px;'>{faixa_risco}</h2>
            <p style='margin: 5px 0 0 0; font-size: 16px;'>Pontuação: {vulnerabilidade_total:.1f} de 28 pontos</p>
        </div>
        """
        st.markdown(risco_html, unsafe_allow_html=True)
        
        # 10. Ler e exibir conteúdo do arquivo markdown correspondente
        st.markdown("### 📋 Relatório de Vulnerabilidade")
        
        try:
            # Caminho para o arquivo markdown
            import os
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            arquivo_path = os.path.join(current_dir, "Conteudo", "04", arquivo_markdown)
            
            if os.path.exists(arquivo_path):
                with open(arquivo_path, 'r', encoding='utf-8') as file:
                    conteudo_markdown = file.read()
                
                # Exibir o conteúdo do arquivo
                st.markdown(conteudo_markdown)
            else:
                st.warning(f"Arquivo de relatório não encontrado: {arquivo_markdown}")
                st.info("Por favor, verifique se o arquivo existe na pasta Conteudo/")
                
        except Exception as e:
            st.error(f"Erro ao ler arquivo de relatório: {str(e)}")
        
        # 11. Informações adicionais sobre o assessment
        st.markdown("### ℹ️ Sobre o Assessment")
        
        info_assessment = f"""
        <div style='background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #6c757d;'>
            <p style='margin: 0; font-size: 14px; color: #6c757d;'>
                <strong>Assessment:</strong> 7 Armadilhas do Eu Empresário<br>
                <strong>Desenvolvido por:</strong> Erika Rossi - EAR Consultoria<br>
                <strong>Total de Perguntas:</strong> 14 (7 diretas + 7 invertidas)<br>
                <strong>Escala de Pontuação:</strong> 0 a 28 pontos<br>
                <strong>Data da Análise:</strong> {date.today().strftime('%d/%m/%Y')}
            </p>
        </div>
        """
        st.markdown(info_assessment, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro na análise de vulnerabilidade: {str(e)}")
        import traceback
        st.error(f"Detalhes do erro: {traceback.format_exc()}")

def analisar_vulnerabilidade_7armadilhas(cursor, user_id, tabela_escolhida=None):
    """
    Retorna análise de vulnerabilidade das 7 Armadilhas do Eu Empresário em formato texto.
    """
    try:
        # 1. Buscar dados do usuário
        cursor.execute("""
            SELECT u.nome, u.email, u.empresa 
            FROM usuarios u 
            WHERE u.user_id = ?
        """, (user_id,))
        usuario_info = cursor.fetchone()
        
        # 2. Buscar pontuação das perguntas diretas (M3000)
        if tabela_escolhida:
            tabela = tabela_escolhida
        else:
            tabela = st.session_state.get('tabela_escolhida', 'forms_resultados_04')
        
        cursor.execute(f"""
            SELECT value_element
            FROM {tabela}
            WHERE user_id = ? AND str_element = 'M3000'
            LIMIT 1
        """, (user_id,))
        result_diretas = cursor.fetchone()
        pontuacao_diretas = float(result_diretas[0]) if result_diretas and result_diretas[0] is not None else 0.0
        
        # 3. Buscar pontuação das perguntas invertidas (N3000)
        cursor.execute(f"""
            SELECT value_element
            FROM {tabela}
            WHERE user_id = ? AND str_element = 'N3000'
            LIMIT 1
        """, (user_id,))
        result_invertidas = cursor.fetchone()
        pontuacao_invertidas = float(result_invertidas[0]) if result_invertidas and result_invertidas[0] is not None else 0.0
        
        # 4. Calcular vulnerabilidade total
        vulnerabilidade_total = pontuacao_diretas + pontuacao_invertidas
        
        # 5. Determinar faixa de risco e arquivo correspondente
        if vulnerabilidade_total <= 7:
            faixa_risco = "Baixo Risco"
            arquivo_markdown = "Conteudo/04/1_BaixoRisco.md"
        elif vulnerabilidade_total <= 14:
            faixa_risco = "Atenção"
            arquivo_markdown = "Conteudo/04/2_Atencao.md"
        elif vulnerabilidade_total <= 21:
            faixa_risco = "Alto Risco"
            arquivo_markdown = "Conteudo/04/3_AltoRisco.md"
        else:
            faixa_risco = "Risco Crítico"
            arquivo_markdown = "Conteudo/04/4_RiscoCritico.md"
        
        # 6. Validação: se não encontrou dados
        if not result_diretas and not result_invertidas:
            return "Análise não disponível: dados de vulnerabilidade não encontrados."
        
        # 7. Ler arquivo de análise
        caminhos_possiveis = [
            arquivo_markdown,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), arquivo_markdown),
            os.path.join(os.path.dirname(__file__), arquivo_markdown),
        ]
        
        conteudo_analise = None
        for caminho in caminhos_possiveis:
            try:
                if os.path.exists(caminho):
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo_analise = f.read()
                        break
            except Exception:
                continue
        
        if not conteudo_analise:
            return f"Análise não disponível: arquivo {arquivo_markdown} não encontrado."
        
        # Retornar análise formatada com título e conteúdo
        analise = f"## Análise de Vulnerabilidade - {faixa_risco}\n\n"
        analise += f"**Pontuação Total:** {vulnerabilidade_total:.1f} pontos\n\n"
        analise += conteudo_analise
        
        return analise
        
    except Exception as e:
        traceback.print_exc()
        return f"Ocorreu um erro inesperado ao gerar a análise: {str(e)}"

# Função antiga removida - substituída por analisar_vulnerabilidade_7armadilhas_streamlit

if __name__ == "__main__":
    show_results()

