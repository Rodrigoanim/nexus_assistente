# Arquivo: form_model.py
# type formula font attribute - somente inteiros
# 10/09/2025 - 08:00 - ajuste função Formula - OK
# Ajuste de títulos

import sqlite3
import streamlit as st
import pandas as pd
import re
import time
# import logging

from config import DB_PATH
from paginas.monitor import registrar_acesso  # Ajustado para incluir o caminho completo

MAX_COLUMNS = 5  # Número máximo de colunas no layout

def format_brazilian_number(value):
    """
    Formata um número conforme padrões brasileiros.
    
    Args:
        value (float): Valor numérico a ser formatado
        
    Returns:
        str: Número formatado segundo as regras:
            - Valores = 0: "0"
            - Valores >= 1: sem casas decimais, separador de milhares com ponto
            - Valores < 1: 3 casas decimais, vírgula como separador decimal
    """
    if value is None or value == 0:
        return "0"
    elif abs(value) >= 1:
        return f"{value:,.0f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    else:
        return f"{value:,.3f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

def clean_quotes(text):
    """
    Remove aspas simples e duplas do início e fim de uma string.
    
    Args:
        text (str): Texto a ser limpo
        
    Returns:
        str: Texto sem aspas ou string vazia se text for None
    """
    if not text:
        return ''
    return text.strip('"').strip("'")

def get_default_formula_style():
    """
    Retorna o estilo HTML padrão para elementos de fórmula.
    
    Returns:
        str: HTML com estilo padrão
    """
    return '<div style="text-align: left; font-size: 16px; margin-bottom: 0;">[valor]</div>'

def render_formula_result(result_value, msg, str_style):
    """
    Renderiza o resultado de uma fórmula no Streamlit com formatação.
    
    Args:
        result_value (float): Valor calculado da fórmula
        msg (str): Mensagem/título opcional
        str_style (str): HTML de formatação com placeholder [valor]
    """
    try:
        # Formata o resultado
        result_br = format_brazilian_number(result_value)
        
        # Limpa aspas dos campos
        clean_msg = clean_quotes(msg)
        clean_style = clean_quotes(str_style)
        
        # Define estilo padrão se necessário
        if not clean_style:
            clean_style = get_default_formula_style()
        
        # Substitui placeholder pelo valor
        formatted_html = clean_style.replace('[valor]', result_br)
        
        # Renderiza mensagem se existir
        if clean_msg:
            st.markdown(clean_msg, unsafe_allow_html=True)
            st.empty()  # Pausa para sincronização do Streamlit
        
        # Renderiza o resultado formatado
        formatted_html = formatted_html.strip()
        st.markdown(formatted_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao renderizar resultado da fórmula: {str(e)}")





def date_to_days(date_str):
    """
    Converte uma data no formato dd/mm/aaaa para número de dias desde 01/01/1900
    """
    try:
        if not date_str:
            return 0
            
        dia, mes, ano = map(int, date_str.split('/'))
        
        # Validação básica da data
        if not (1900 <= ano <= 2100 and 1 <= mes <= 12 and 1 <= dia <= 31):
            return 0
            
        # Cálculo dos dias
        # Anos completos desde 1900
        days = (ano - 1900) * 365
        
        # Adiciona dias dos anos bissextos
        leap_years = sum(1 for y in range(1900, ano) if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0))
        days += leap_years
        
        # Dias dos meses completos no ano atual
        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0):
            days_in_month[2] = 29
            
        days += sum(days_in_month[1:mes])
        
        # Adiciona dias do mês atual
        days += dia - 1
        
        return days
    except Exception as e:
        st.error(f"Erro na conversão de data: {str(e)}")
        return 0

def get_element_value(cursor, name_element, element=None):
    """Busca o valor de um elemento na tabela forms_tab_04."""
    cursor.execute("""
        SELECT value_element 
        FROM forms_tab_04 
        WHERE name_element = ? AND user_id = ?
    """, (name_element, st.session_state.user_id))
    result = cursor.fetchone()
    if result and result[0] is not None:
        return float(result[0])  # Valor já está como REAL no banco
    return 0.0

@st.cache_data(ttl=300)  # Cache por 5 minutos
def _calculate_formula_cached(formula_str, values_dict, user_id):
    """
    Função cacheável para cálculo de fórmulas.
    
    Args:
        formula_str: String da fórmula
        values_dict: Dicionário com valores das células {name: value}
        user_id: ID do usuário (para invalidação do cache)
    
    Returns:
        float: Resultado do cálculo
    """
    try:
        # Se a fórmula for um número direto
        if isinstance(formula_str, (int, float)):
            return float(formula_str)
        
        # Se for string numérica
        if isinstance(formula_str, str):
            formula_clean = formula_str.replace(',', '.')
            if formula_clean.replace('.','',1).isdigit():
                return float(formula_clean)
        
        processed_formula = str(formula_str)
        
        # Processa referências na fórmula
        cell_refs = re.findall(r'(?:Insumos!)?[A-Z]{1,2}[0-9]+', processed_formula)
        
        # Substitui todas as referências pelos valores
        for ref in cell_refs:
            float_value = values_dict.get(ref, 0.0)
            processed_formula = re.sub(r'\b' + re.escape(ref) + r'\b', str(float_value), processed_formula)
        
        # Substitui vírgulas por pontos antes do eval
        processed_formula = processed_formula.replace(',', '.')
        
        # Função de divisão segura
        def safe_div(x, y):
            if abs(float(y)) < 1e-10:
                return 0.0
            return x / y
        
        # Ambiente seguro para eval
        safe_env = {
            'safe_div': safe_div,
            '__builtins__': None
        }
        
        # Substitui divisões pela função segura
        processed_formula = re.sub(r'(\d+\.?\d*|\([^)]+\))\s*/\s*(\d+\.?\d*|\([^)]+\))', r'safe_div(\1, \2)', processed_formula)
        
        result = float(eval(processed_formula, safe_env, {}))
        
        # Formatação do resultado
        if result is None:
            return 0.0
            
        # Formata o número com casas decimais apropriadas
        if abs(result) >= 1:
            formatted_result = f"{result:,.0f}"
        else:
            formatted_result = f"{result:,.3f}"
            
        # Converte para formato brasileiro
        formatted_result = formatted_result.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        
        return float(formatted_result.replace('.', '').replace(',', '.'))
        
    except Exception as e:
        # Para cache, retorna 0.0 em caso de erro (sem exibir erro na UI)
        return 0.0

def calculate_formula(formula, values, cursor):
    """
    Calcula o resultado de uma fórmula com suporte a operações matemáticas e datas.
    Versão otimizada com cache para melhor performance.
    
    Args:
        formula: A fórmula a ser calculada (pode ser número, string ou expressão)
        values: Dicionário com valores das células
        cursor: Cursor do banco de dados
    
    Returns:
        float: O resultado do cálculo
    """
    try:
        # CASOS ESPECIAIS SEM CACHE (processamento direto)
        
        # Se a fórmula for um número direto
        if isinstance(formula, (int, float)):
            return float(formula)
        
        # Se for string numérica
        if isinstance(formula, str):
            formula_clean = formula.replace(',', '.')
            if formula_clean.replace('.','',1).isdigit():
                return float(formula_clean)
        
        processed_formula = str(formula)
        
        # Verifica se é uma fórmula de data (sem cache por ser específica)
        if re.match(r'^\s*[A-Z][0-9]+\s*-\s*[A-Z][0-9]+\s*$', processed_formula):
            refs = re.findall(r'[A-Z][0-9]+', processed_formula)
            if len(refs) == 2:
                data_final = refs[0]
                data_inicial = refs[1]
                
                # Busca as datas no banco
                cursor.execute("""
                    SELECT str_element 
                    FROM forms_tab_04 
                    WHERE name_element = ? AND user_id = ?
                """, (data_final, st.session_state.user_id))
                result = cursor.fetchone()
                data_final_str = result[0] if result and result[0] else None
                
                cursor.execute("""
                    SELECT str_element 
                    FROM forms_tab_04 
                    WHERE name_element = ? AND user_id = ?
                """, (data_inicial, st.session_state.user_id))
                result = cursor.fetchone()
                data_inicial_str = result[0] if result and result[0] else None
                
                # Converte as datas para dias
                dias_final = date_to_days(data_final_str)
                dias_inicial = date_to_days(data_inicial_str)
                
                # Calcula a diferença em dias e converte para meses
                diff_dias = dias_final - dias_inicial
                meses = diff_dias / 30.44
                
                return max(0, meses)
        
        # FÓRMULAS COM CÉLULAS - USA CACHE
        
        # Processa referências na fórmula
        cell_refs = re.findall(r'(?:Insumos!)?[A-Z]{1,2}[0-9]+', processed_formula)
        
        if cell_refs:
            # OTIMIZAÇÃO 1: Consulta em lote
            placeholders = ','.join(['?'] * len(cell_refs))
            cursor.execute(f"""
                SELECT name_element, value_element 
                FROM forms_tab_04 
                WHERE name_element IN ({placeholders}) AND user_id = ?
            """, cell_refs + [st.session_state.user_id])
            
            # Cria dicionário para a função cacheável
            values_dict = dict(cursor.fetchall())
            
            # OTIMIZAÇÃO 2: Usa cache para o cálculo
            return _calculate_formula_cached(
                formula_str=processed_formula,
                values_dict=values_dict,
                user_id=st.session_state.user_id
            )
        
        # Caso não tenha referências, usa cache também
        return _calculate_formula_cached(
            formula_str=processed_formula,
            values_dict={},
            user_id=st.session_state.user_id
        )
        
    except Exception as e:
        if "division by zero" in str(e):
            return 0.0
        st.error(f"Erro no cálculo da fórmula: {str(e)}")
        return 0.0

def condicaoH(cursor, element, conn):
    """
    Atualiza o value_element baseado em um valor de referência e mapeamento.
    """
    # print(f"\nCondicaoH chamada para elemento: {element[0]}")  # Debug
    
    try:
        # Extrai informações da linha atual
        name_element = element[1]  # D151, D152, etc
        math_ref = element[3]      # D15 (vem da coluna math_element)
        select_options = element[6] # String com mapeamento (vem da coluna str_element)
        
        # print(f"  math_ref: {math_ref}")  # Debug
        # print(f"  select_options: {select_options}")  # Debug
        
        # 1. Validações iniciais
        if not all([name_element, math_ref, select_options]):
            # print("  Erro: dados incompletos")  # Debug
            return False
            
        # 2. Busca str_element da referência
        cursor.execute("""
            SELECT str_element 
            FROM forms_tab_04 
            WHERE name_element = ? AND user_id = ?
        """, (math_ref, st.session_state.user_id))
        
        result = cursor.fetchone()
        if not result or result[0] is None:
            # print("  Erro: str_element não encontrado")  # Debug
            return False
            
        str_ref = result[0].strip()  # Remove espaços extras
        # print(f"  str_ref encontrado: {str_ref}")  # Debug
        
        # 3. Processa mapeamento do select_options
        try:
            # Remove aspas duplas do início e fim do select_options
            select_options = select_options.strip('"')
            
            # Divide os pares de valores
            mapeamento = {}
            for par in select_options.split('|'):
                if ':' in par:
                    chave, valor = par.split(':')
                    chave = chave.strip()  # Remove espaços extras da chave
                    valor = valor.strip()  # Remove espaços extras do valor
                    mapeamento[chave] = float(valor)
            
            # print(f"  Mapeamento: {mapeamento}")  # Debug
            
            # Busca valor correspondente
            if str_ref in mapeamento:
                valor_encontrado = mapeamento[str_ref]
                # print(f"  Valor encontrado: {valor_encontrado}")  # Debug
                
                # 4. Atualiza o banco
                cursor.execute("""
                    UPDATE forms_tab_04 
                    SET value_element = ?
                    WHERE name_element = ? AND user_id = ?
                """, (valor_encontrado, name_element, st.session_state.user_id))
                
                conn.commit()
                return True
            
            # print(f"  Erro: str_ref '{str_ref}' não encontrado no mapeamento")  # Debug
            return False
            
        except ValueError:
            # print("  Erro: ValueError ao processar valores")  # Debug
            return False
            
        except sqlite3.Error:
            # print("  Erro: Erro no banco de dados")  # Debug
            conn.rollback()
            return False
        
    except Exception as e:
        # print(f"  Erro inesperado: {str(e)}")  # Debug
        if 'conn' in locals():
            conn.rollback()
        return False

def titulo(cursor, element):
    """
    Exibe títulos formatados na interface com base nos valores do banco de dados.
    Suporte ao placeholder [valor] no str_element que é substituído pelo msg_element.
    """
    try:
        name = element[0]
        type_elem = element[1]
        msg = element[3].strip("'").strip('"')  # Remove aspas simples e duplas
        str_value = element[6].strip("'").strip('"') if element[6] else ''  # Remove aspas simples e duplas
        
        # Se for do tipo 'titulo'
        if type_elem == 'titulo':
            if str_value:
                # Verifica se str_value contém o placeholder [valor]
                if '[valor]' in str_value:
                    # Substitui [valor] pelo conteúdo de msg_element
                    formatted_msg = str_value.replace('[valor]', msg)
                    st.markdown(formatted_msg, unsafe_allow_html=True)
                    return
                else:
                    # Mantém compatibilidade com formato antigo
                    formatted_msg = str_value.replace('✅ Operação concluída com sucesso!', msg)
                    st.markdown(formatted_msg, unsafe_allow_html=True)
                    return
        
        # Para os demais casos
        if str_value and not "Operação concluída" in str_value:
            st.markdown(str_value, unsafe_allow_html=True)
            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.markdown(msg, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Erro ao processar título: {str(e)}")

def new_user(cursor, user_id):
    """
    Inicializa registros para um novo usuário copiando dados do user_id 0.
    """
    try:
        # Verifica se já existem registros para o usuário
        cursor.execute("""
            SELECT COUNT(*) FROM forms_tab_04 WHERE user_id = ?
        """, (user_id,))
        
        if cursor.fetchone()[0] == 0:  # Se não existem registros
            # Copia todos os dados do user_id 0
            cursor.execute("""
                INSERT INTO forms_tab_04 (
                    name_element, type_element, math_element, msg_element,
                    value_element, select_element, str_element, e_col, e_row,
                    section, col_len, user_id
                )
                SELECT 
                    name_element, type_element, math_element, msg_element,
                    value_element, select_element, str_element, e_col, e_row,
                    section, col_len, ? as user_id
                FROM forms_tab_04 
                WHERE user_id = 0
            """, (user_id,))
            
            st.success(f"Registros iniciais criados para o usuário {user_id}")
        
    except Exception as e:
        st.error(f"Erro ao criar registros para novo usuário: {str(e)}")
        raise

def _reset_rerun_locks(section):
    """
    Reset das flags de controle de rerun e timestamps de debounce para permitir novas atualizações.
    
    Args:
        section (str): Seção atual para resetar os locks específicos
    """
    try:
        # Lista todas as chaves de controle da seção
        keys_to_remove = [key for key in st.session_state.keys() 
                         if ((key.startswith(f'rerun_lock_') or key.startswith(f'debounce_time_')) 
                             and section in key)]
        
        # Remove as flags e timestamps antigos
        for key in keys_to_remove:
            del st.session_state[key]
            
    except Exception:
        # Se houver erro, não afeta o funcionamento principal
        pass

def process_forms_tab_04(section='perfil'):
    """
    Processa registros da tabela forms_tab_04 e exibe em layout de grade.
    Versão otimizada com controle de st.rerun().
    
    Args:
        section (str): Seção a ser exibida ('perfil', 'comportamento' ou 'resultado')
    """
    # Define o número de colunas
    max_cols = 5
    
    # OTIMIZAÇÃO 3: Reset de flags de controle de rerun
    _reset_rerun_locks(section)
    
    conn = None
    try:
        # Inicializa flag de log no session_state se não existir
        log_key = f"log_registered_{section}"
        if log_key not in st.session_state:
            st.session_state[log_key] = False
            
        # 1. Verifica se há um usuário logado
        if 'user_id' not in st.session_state:
            st.error("Usuário não está logado!")
            return
            
        # 2. Armazena user_id em variável
        user_id = st.session_state.user_id
        
        # Títulos com estilo baseados na seção
        titles = {
            'armadilhas_p1': "🎯 Armadilhas do Empresário - Parte 1",
            'armadilhas_p2': "📊 Armadilhas do Empresário - Parte 2", 
            'resultado': "📈 Resultados - Armadilhas do Empresário"
        }
        
        title_text = titles.get(section, "Assessment 04 - Armadilhas do Empresário")
        st.markdown(f"""
            <p style='
                text-align: left;
                font-size: 28px;
                font-weight: bold;
                color: #1E1E1E;
                margin: 15px 0;
                padding: 10px;
                background-color: #FFFFFF;
                border-radius: 5px;
            '>{title_text}</p>
        """, unsafe_allow_html=True)
        
        # Inicializa session_state
        if 'form_values' not in st.session_state:
            st.session_state.form_values = {}
        
        # Conexão com o banco
        conn = sqlite3.connect(DB_PATH)  # Atualizado para usar DB_PATH
        cursor = conn.cursor()

        # 3. Garante que existam dados para o usuário
        new_user(cursor, user_id)
        conn.commit()

        # 4. Busca dados específicos do usuário logado e da seção atual
        cursor.execute("""
            SELECT name_element, type_element, math_element, msg_element,
                   value_element, select_element, str_element, e_col, e_row,
                   col_len
            FROM forms_tab_04
            WHERE user_id = ? AND section = ?
            ORDER BY e_row, e_col
        """, (user_id, section))
        elements = cursor.fetchall()

        # Verifica se existem elementos para esta seção
        if not elements:
            st.warning(f"Nenhum elemento encontrado para a seção {section}")
            return

        # Agrupa elementos por linha
        rows = {}
        for element in elements:
            e_row = element[8]
            if e_row not in rows:
                rows[e_row] = []
            rows[e_row].append(element)

        # Processa cada linha
        for row_num in sorted(rows.keys()):
            row_elements = rows[row_num]
            
            # Filtra elementos visíveis
            visible_elements = [e for e in row_elements if not e[1].endswith('H')]
            if not visible_elements:
                continue
                
            # Verifica se é uma linha de espaçamento
            if any(element[1] == 'pula_linha' for element in visible_elements):
                st.markdown("<br>", unsafe_allow_html=True)
                continue
            
            # Para os elementos normais
            # Calcula o total de colunas necessário baseado em col_len
            total_cols = 0
            for element in visible_elements:
                col_len = int(element[9]) if element[9] is not None else 1
                total_cols += col_len

            # Cria lista de larguras relativas respeitando max_cols
            column_widths = []
            remaining_cols = max_cols

            for element in visible_elements:
                col_len = int(element[9]) if element[9] is not None else 1
                # Ajusta a largura para não ultrapassar o espaço restante
                actual_width = min(col_len, remaining_cols)
                column_widths.append(actual_width)
                remaining_cols -= actual_width

            # Adiciona colunas vazias se necessário
            if remaining_cols > 0:
                column_widths.append(remaining_cols)

            # Cria todas as colunas de uma vez com suas larguras relativas
            cols = st.columns(column_widths)
            
            # Processa os elementos dentro das colunas
            for idx, element in enumerate(visible_elements):
                with cols[idx]:
                    name = element[0]
                    type_elem = element[1]
                    math_elem = element[2]
                    msg = element[3]
                    value = element[4]
                    select_options = element[5]
                    str_value = element[6]
                    e_col = element[7] - 1  # Ajusta para índice 0-4
                    
                    # Verifica se a coluna está dentro do limite
                    if e_col >= max_cols:
                        continue  # Pula silenciosamente elementos fora do limite

                    try:
                        # Processa elementos do tipo título
                        if type_elem == 'titulo':
                            titulo(cursor, element)
                            continue

                        # Processa elementos ocultos (condicaoH e call_insumosH)
                        if type_elem.endswith('H'):
                            try:
                                if type_elem == 'condicaoH':
                                    result = condicaoH(cursor, element, conn)
                                elif type_elem == 'call_insumosH':
                                    result = call_insumos(cursor, element)

                                # Atualiza o banco com o resultado
                                if type_elem in ['condicaoH', 'call_insumosH']:
                                    cursor.execute("""
                                        UPDATE forms_tab_04 
                                        SET value_element = ? 
                                        WHERE name_element = ? AND user_id = ?
                                    """, (result, name, st.session_state.user_id))
                                    conn.commit()
                                continue

                            except Exception as e:
                                st.error(f"Falha ao processar elemento oculto {name}: {str(e)}")

                        # Processamento normal para elementos visíveis - Selectbox
                        if type_elem == 'selectbox':
                            try:
                                # Validação das opções do select
                                if not select_options:
                                    st.error(f"Erro: Opções vazias para {name}")
                                    continue
                                
                                options = [opt.strip() for opt in select_options.split('|')]
                                display_msg = msg if msg.strip() else name
                                initial_index = options.index(str_value) if str_value in options else 0
                                
                                # Renderiza o selectbox
                                selected = st.selectbox(
                                    display_msg,
                                    options=options,
                                    key=f"select_{name}_{row_num}_{e_col}",
                                    index=initial_index,
                                    label_visibility="collapsed" if not msg.strip() else "visible"
                                )
                                
                                # Se o valor mudou, atualiza os elementos dependentes
                                if selected != str_value:
                                    try:
                                        # Atualiza o próprio selectbox
                                        cursor.execute("""
                                            UPDATE forms_tab_04 
                                            SET str_element = ?,
                                                value_element = ?
                                            WHERE name_element = ? 
                                            AND user_id = ? 
                                            AND section = ?
                                        """, (selected, 0.0, name, st.session_state.user_id, section))
                                        
                                        # Busca elementos condicaoH que dependem deste selectbox
                                        cursor.execute("""
                                            SELECT * FROM forms_tab_04 
                                            WHERE type_element = 'condicaoH' 
                                            AND math_element = ? 
                                            AND user_id = ?
                                        """, (name, st.session_state.user_id))
                                        
                                        # Para cada elemento encontrado, chama condicaoH
                                        for elemento in cursor.fetchall():
                                            # print(f"Elemento encontrado: {elemento}")  # Debug adicional
                                            condicaoH(cursor, elemento, conn)
                                        
                                        conn.commit()
                                    
                                    except sqlite3.Error as e:
                                        st.error(f"Erro no banco de dados: {str(e)}")
                                        conn.rollback()

                            except Exception as e:
                                st.error(f"Erro no selectbox {name}: {str(e)}")
                                if 'conn' in locals():
                                    conn.rollback()

                        elif type_elem == 'call_insumos':
                            try:
                                result = call_insumos(cursor, element)
                                conn.commit()
                                
                                # Configurações de estilo para métricas
                                FONT_SIZES = {
                                    'small': '12px',
                                    'medium': '16px',
                                    'large': '20px',
                                    'xlarge': '24px'
                                }
                                
                                msg_parts = msg.split('|')
                                display_msg = msg_parts[0].strip()
                                font_size = 'medium'
                                
                                if len(msg_parts) > 1:
                                    for param in msg_parts[1:]:
                                        if param.startswith('size:'):
                                            requested_size = param.split(':')[1].strip()
                                            if requested_size in FONT_SIZES:
                                                font_size = requested_size

                                st.markdown(f"""
                                    <div style='text-align: left;'>
                                        <p style='font-size: {FONT_SIZES[font_size]}; margin-bottom: 0;'>{display_msg}</p>
                                        <p style='font-size: {FONT_SIZES[font_size]}; font-weight: bold;'>{result:.2f}</p>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                            except Exception as e:
                                st.error(f"Erro ao processar call_insumos: {str(e)}")

                        elif type_elem == 'input':
                            try:
                                # Converte o valor REAL do banco para exibição no formato BR
                                if value is not None:
                                    current_value = f"{float(value):.2f}".replace('.', ',')
                                else:
                                    current_value = "0,00"
                                
                                # Usa o nome do elemento como label se msg estiver vazio
                                display_msg = msg if msg.strip() else name
                                input_value = st.text_input(
                                    display_msg,
                                    value=current_value,
                                    key=f"input_{name}_{row_num}_{e_col}",
                                    label_visibility="collapsed" if not msg.strip() else "visible"
                                )
                                
                                try:
                                    # Remove pontos de milhar e converte vírgula para ponto
                                    cleaned_input = input_value.strip().replace('.', '').replace(',', '.')
                                    numeric_value = float(cleaned_input)
                                    
                                    # OTIMIZAÇÃO 3: Controle inteligente de st.rerun() com debounce
                                    old_value = float(value or 0)
                                    tolerance = 1e-6  # Tolerância maior para evitar reruns por flutuação
                                    
                                    if abs(numeric_value - old_value) > tolerance:
                                        # Sistema de debounce
                                        current_time = time.time()
                                        debounce_key = f"debounce_time_{name}_{section}"
                                        last_update = st.session_state.get(debounce_key, 0)
                                        min_interval = 0.5  # Mínimo 500ms entre reruns
                                        
                                        # Evita reruns em cascata
                                        rerun_key = f"rerun_lock_{name}_{section}"
                                        
                                        if (current_time - last_update > min_interval and 
                                            not st.session_state.get(rerun_key, False)):
                                            
                                            # Registra log apenas uma vez por seção
                                            if not st.session_state[log_key]:
                                                registrar_acesso(
                                                    st.session_state.user_id,
                                                    f"forms_{section}",
                                                    f"Alteração em formulário de {section}"
                                                )
                                                st.session_state[log_key] = True
                                            
                                            # Atualiza banco
                                            cursor.execute("""
                                                UPDATE forms_tab_04 
                                                SET value_element = ? 
                                                WHERE name_element = ? AND user_id = ?
                                            """, (numeric_value, name, st.session_state.user_id))
                                            conn.commit()
                                            
                                            # Marca flags para controle
                                            st.session_state[rerun_key] = True
                                            st.session_state[debounce_key] = current_time
                                            st.rerun()
                                        else:
                                            # Atualiza apenas o session_state sem rerun
                                            cursor.execute("""
                                                UPDATE forms_tab_04 
                                                SET value_element = ? 
                                                WHERE name_element = ? AND user_id = ?
                                            """, (numeric_value, name, st.session_state.user_id))
                                            conn.commit()
                                    
                                    st.session_state.form_values[name] = numeric_value
                                    
                                except ValueError:
                                    st.error(f"Por favor, insira apenas números em {msg}")
                                    st.session_state.form_values[name] = float(value or 0)
                            
                            except Exception as e:
                                st.error(f"Erro ao processar input: {str(e)}")

                        elif type_elem == 'formula':
                            try:
                                # 1. Calcula o resultado da fórmula
                                result = calculate_formula(math_elem, st.session_state.form_values, cursor)
                                
                                # 2. Renderiza na interface SOMENTE se str_element não estiver vazio
                                if str_value and str_value.strip():
                                    render_formula_result(result, msg, str_value)
                                
                                # 3. Atualiza o banco com UPDATE direto
                                cursor.execute("""
                                    UPDATE forms_tab_04 
                                    SET value_element = ? 
                                    WHERE name_element = ? AND user_id = ?
                                """, (result, name, st.session_state.user_id))
                                conn.commit()
                                
                            except Exception as e:
                                st.error(f"Erro ao processar elemento de fórmula {name}: {str(e)}")

                        elif type_elem == 'input_data':
                            # Pega o valor atual do str_element
                            current_value = str_value if str_value else ''
                            
                            # Campo de entrada para data
                            input_value = st.text_input(
                                msg,
                                value=current_value,
                                key=f"input_data_{name}_{row_num}_{e_col}",
                                label_visibility="collapsed" if not msg.strip() else "visible"
                            )
                            
                            # Validação do formato da data
                            if input_value:
                                # Regex para validar formato dd/mm/aaaa
                                date_pattern = r'^\d{2}/\d{2}/\d{4}$'
                                if not re.match(date_pattern, input_value):
                                    st.error(f"Por favor, insira a data no formato dd/mm/aaaa em {msg}")
                                else:
                                    try:
                                        dia, mes, ano = map(int, input_value.split('/'))
                                        # Verifica se é uma data válida
                                        if (mes < 1 or mes > 12 or dia < 1 or dia > 31 or
                                            ano < 1900 or ano > 2100 or
                                            (mes in [4, 6, 9, 11] and dia > 30) or
                                            (mes == 2 and dia > 29)):
                                            st.error(f"Data inválida em {msg}")
                                        else:
                                            # Calcula dias desde 01/01/1900
                                            days_since_1900 = date_to_days(input_value)
                                            
                                            # OTIMIZAÇÃO 3: Controle inteligente de st.rerun() para datas com debounce
                                            if input_value != current_value:
                                                # Sistema de debounce para datas
                                                current_time = time.time()
                                                debounce_key = f"debounce_time_date_{name}_{section}"
                                                last_update = st.session_state.get(debounce_key, 0)
                                                min_interval = 0.3  # Intervalo menor para datas (300ms)
                                                
                                                # Evita reruns em cascata para datas
                                                rerun_key = f"rerun_lock_date_{name}_{section}"
                                                
                                                if (current_time - last_update > min_interval and 
                                                    not st.session_state.get(rerun_key, False)):
                                                    
                                                    cursor.execute("""
                                                        UPDATE forms_tab_04 
                                                        SET str_element = ?,
                                                            value_element = ? 
                                                        WHERE name_element = ? AND user_id = ?
                                                    """, (input_value, days_since_1900, name, st.session_state.user_id))
                                                    conn.commit()
                                                    
                                                    # Marca flags para controle
                                                    st.session_state[rerun_key] = True
                                                    st.session_state[debounce_key] = current_time
                                                    st.rerun()
                                                else:
                                                    # Atualiza apenas o banco sem rerun
                                                    cursor.execute("""
                                                        UPDATE forms_tab_04 
                                                        SET str_element = ?,
                                                            value_element = ? 
                                                        WHERE name_element = ? AND user_id = ?
                                                    """, (input_value, days_since_1900, name, st.session_state.user_id))
                                                    conn.commit()
                                            
                                            # Atualiza o form_values com o número de dias
                                            st.session_state.form_values[name] = days_since_1900
                                            
                                    except ValueError:
                                        st.error(f"Data inválida em {msg}")

                        elif type_elem == 'formula_data':
                            # Desabilitado - não faz nada
                            pass

                    except Exception as e:
                        st.error(f"Erro ao processar {name}: {str(e)}")

        # Separador
        st.divider()

    except Exception as e:
        st.error(f"Erro ao processar formulário: {str(e)}")
    finally:
        if conn:
            conn.close()

def call_insumos(cursor, element):
    """
    Busca valor de referência na tabela forms_insumos e atualiza value_element.
    
    Args:
        cursor: Cursor do banco de dados SQLite
        element: Tupla contendo os dados do elemento (name, type, math, msg, value, select, str, col, row)
    
    Returns:
        float: Valor numérico encontrado ou 0.0 em caso de erro
    """
    try:
        name = element[0]  # name_element da forms_tab_04
        str_value = element[6]  # str_element da forms_tab_04 (ex: 'InsumosI15')
        
        # Verifica se há uma referência válida
        if not str_value:
            return 0.0
            
        # Busca o math_element na forms_insumos onde name_element = str_value da forms_tab_04
        cursor.execute("""
            SELECT math_element 
            FROM forms_insumos 
            WHERE name_element = ?
        """, (str_value.strip(),))
        
        result = cursor.fetchone()
        if not result:
            st.warning(f"Referência '{str_value}' não encontrada em forms_insumos")
            return 0.0
            
        try:
            math_value = result[0]
            if not math_value:
                return 0.0
                
            # Processa o valor do math_element
            if '/' in math_value:  # Se for uma fração
                num, den = map(lambda x: float(x.replace(',', '.')), math_value.split('/'))
                if den == 0:
                    st.error(f"Divisão por zero encontrada em '{math_value}'")
                    return 0.0
                final_value = num / den
            else:
                final_value = float(math_value.replace(',', '.'))
            
            # Converte para formato BR antes de salvar
            final_value_br = f"{final_value:.2f}".replace('.', ',')
            
            cursor.execute("""
                UPDATE forms_tab_04 
                SET value_element = ?
                WHERE name_element = ? AND user_id = ?
            """, (final_value_br, name, st.session_state.user_id))
            
            return final_value  # Retorna float para cálculos
            
        except ValueError as e:
            st.error(f"Valor inválido '{result[0]}' para a referência '{str_value}': {str(e)}")
            return 0.0
            
    except sqlite3.Error as e:
        st.error(f"Erro no banco de dados: {str(e)}")
        return 0.0
    except Exception as e:
        st.error(f"Erro inesperado ao processar referência: {str(e)}")
        return 0.0

def process_forms_tab(section='armadilhas_p1'):
    """
    Função wrapper para compatibilidade com main.py
    Chama process_forms_tab_04 com a seção especificada
    """
    return process_forms_tab_04(section)

