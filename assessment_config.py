# assessment_config.py
# Configuração centralizada de todos os assessments
# Data: 09/11/2025
# Objetivo: Centralizar configurações para facilitar adição de novos assessments
# pgm criado apos pedido para fatorar codigo e facilitar adicao de novos assessments

"""
Configuração centralizada de assessments.

Cada assessment deve ter:
- form_module: Nome do módulo form_model (ex: "form_model_01")
- results_module: Nome do módulo resultados (ex: "resultados_01")
- sections: Dicionário com mapeamento de rótulos da interface para variáveis internas
- has_menu: Se True, exibe menu de seleção de seções; se False, executa diretamente
- menu_title: Título do menu (opcional, usado apenas se has_menu=True)
- menu_message: Mensagem do menu (opcional, usado apenas se has_menu=True)
"""

# Configuração de assessments
ASSESSMENT_CONFIG = {
    "01": {
        "form_module": "form_model_01",
        "results_module": "resultados_01",
        "sections": {
            "📋 Parte 1": "perfil",
            "✏️ Parte 2": "comportamento",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,
        "menu_title": "#### 📋 Selecione a Parte que deseja",
        "menu_message": "IMPORTANTE: precisa responder tanto a Parte 1 quanto a Parte 2",
        "selector_key": "disc10_section_selector",
        "selector_bottom_key": "disc10_section_selector_bottom",
        "target_section_key": "target_section_01"
    },
    "02": {
        "form_module": "form_model_02",
        "results_module": "resultados_02",
        "sections": {
            "📋 Parte 1": "perfil",
            "✏️ Parte 2": "comportamento",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,
        "menu_title": "#### 📋 Selecione a seção que deseja responder",
        "menu_message": "Escolha a seção:",
        "selector_key": "disc20_section_selector",
        "selector_bottom_key": "disc20_section_selector_bottom",
        "target_section_key": "target_section_02"
    },
    "03": {
        "form_module": "form_model_03",
        "results_module": "resultados_03",
        "sections": {
            "📋 Parte 1": "ancoras_p1",
            "✏️ Parte 2": "ancoras_p2",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,
        "menu_title": "#### 📋 Selecione a Parte que deseja",
        "menu_message": "IMPORTANTE: Precisa responder tanto a Parte 1 quanto a Parte 2",
        "selector_key": "ancoras_section_selector",
        "selector_bottom_key": "ancoras_section_selector_bottom",
        "target_section_key": "target_section_03"
    },
    "04": {
        "form_module": "form_model_04",
        "results_module": "resultados_04",
        "sections": {
            "📋 Parte 1": "armadilhas_p1",
            "✏️ Parte 2": "armadilhas_p2",
            "📊 Resultados": "resultado"
        },
        "has_menu": True,
        "menu_title": "#### 📋 Selecione a Parte que deseja",
        "menu_message": "IMPORTANTE: Precisa responder tanto a Parte 1 quanto a Parte 2",
        "selector_key": "armadilhas_section_selector",
        "selector_bottom_key": "armadilhas_section_selector_bottom",
        "target_section_key": "target_section_04"
    },
    "05": {
        "form_module": "form_model_05",
        "results_module": "resultados_05",
        "sections": {
            "📋 Parte 1": "anamnese_p1",
            "✏️ Parte 2": "anamnese_p2",
            "📊 Resultados": "resultado"
        },
        "has_menu": False,  # Sem menu específico - executa diretamente
        "menu_title": None,
        "menu_message": None,
        "selector_key": None,
        "selector_bottom_key": None,
        "target_section_key": None
    }
}

def get_assessment_config(assessment_id):
    """
    Retorna a configuração de um assessment.
    
    Args:
        assessment_id: ID do assessment (ex: "01", "02")
        
    Returns:
        dict: Configuração do assessment ou None se não encontrado
    """
    return ASSESSMENT_CONFIG.get(assessment_id)

def get_all_assessment_ids():
    """
    Retorna lista de todos os IDs de assessments configurados.
    
    Returns:
        list: Lista de IDs de assessments
    """
    return list(ASSESSMENT_CONFIG.keys())

def get_form_module_name(assessment_id):
    """
    Retorna o nome do módulo form_model para um assessment.
    
    Args:
        assessment_id: ID do assessment
        
    Returns:
        str: Nome do módulo ou None se não encontrado
    """
    config = get_assessment_config(assessment_id)
    return config.get("form_module") if config else None

def get_results_module_name(assessment_id):
    """
    Retorna o nome do módulo resultados para um assessment.
    
    Args:
        assessment_id: ID do assessment
        
    Returns:
        str: Nome do módulo ou None se não encontrado
    """
    config = get_assessment_config(assessment_id)
    return config.get("results_module") if config else None

def get_sections(assessment_id):
    """
    Retorna o mapeamento de seções para um assessment.
    
    Args:
        assessment_id: ID do assessment
        
    Returns:
        dict: Mapeamento de rótulos para variáveis internas ou None se não encontrado
    """
    config = get_assessment_config(assessment_id)
    return config.get("sections") if config else None

def has_menu(assessment_id):
    """
    Verifica se um assessment tem menu de seleção de seções.
    
    Args:
        assessment_id: ID do assessment
        
    Returns:
        bool: True se tem menu, False caso contrário
    """
    config = get_assessment_config(assessment_id)
    return config.get("has_menu", False) if config else False

def get_function_name(assessment_id):
    """
    Retorna o nome da função process_forms_tab para um assessment.
    Padronizado: todos usam process_forms_tab_XX (incluindo 01).
    
    Args:
        assessment_id: ID do assessment
        
    Returns:
        str: Nome da função (ex: "process_forms_tab_01")
    """
    return f"process_forms_tab_{assessment_id}"

