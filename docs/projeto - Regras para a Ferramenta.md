(As respostas salvas são somente para visualização)
Aqui estão as regras de negócio para montar um aplicativo que consiga aplicar o assessment "As Sete Armadilhas do Eu Empresário", com base nas informações fornecidas:
Regras de Negócio para o Aplicativo "As Sete Armadilhas do Eu Empresário"
1. Propósito do Aplicativo:
• O aplicativo deve funcionar como uma ferramenta de assessment para empreendedores.
• Seu objetivo é avaliar o nível de vulnerabilidade do empreendedor em relação a "As Sete Armadilhas do Eu Empresário".
• Deve fornecer uma pontuação e um resultado/devolutiva com base nessa avaliação.
2. Estrutura do Assessment:
• O assessment é composto por 7 categorias de "armadilhas".
• Cada armadilha possui duas perguntas relacionadas.
• As categorias de armadilhas são:
    ◦ Sobrecarga e Solidão
    ◦ Vida Pessoal x Profissional
    ◦ Sem Backup / Sucessão
    ◦ Crescimento no Improviso
    ◦ Dependência Total do Dono
    ◦ Dificuldade em Atrair Parceiros
    ◦ Sem Tempo para o Futuro
• Haverá um total de 14 questões no assessment (7 armadilhas x 2 perguntas).
3. Coleta de Dados (Entrada do Usuário):
• Para cada uma das 14 perguntas, o usuário deve inserir uma "Pontuação (0-3)", onde 0 é a pontuação mínima e 3 é a pontuação máxima.
• Esta "Pontuação (0-3)" é a entrada direta do respondente.
4. Processamento da Pontuação (Cálculo de Risco Individual por Pergunta):
• Para cada pergunta, o aplicativo deve calcular uma "Pontuação de Risco" com base no tipo da pergunta e na pontuação de entrada.
• As perguntas são de dois tipos:
    ◦ Pergunta Direta: A "Pontuação de Risco" é igual à "Pontuação (0-3)" inserida pelo usuário.
        ▪ Exemplo: Se a pergunta direta recebe pontuação '2', a Pontuação de Risco é '2'.
    ◦ Pergunta Invertida: A "Pontuação de Risco" é calculada como '3 - Pontuação (0-3)'.
        ▪ Exemplo: Se a pergunta invertida recebe pontuação '0', a Pontuação de Risco é '3' (3-0). Se a pergunta invertida recebe pontuação '3', a Pontuação de Risco é '0' (3-3).
5. Cálculo da Vulnerabilidade Total:
• O resultado final de vulnerabilidade do empreendedor deve ser obtido pela soma de todas as "Pontuações de Risco" das 14 perguntas.
• O aplicativo deve desconsiderar a coluna "Pontuação (0-3)" para a soma final, utilizando exclusivamente a coluna "Pontuação de Risco".
• A pontuação máxima possível é 28 (14 perguntas x 2 pontos, caso todas as perguntas de risco tenham pontuação máxima na coluna de risco).
6. Interpretação dos Resultados (Níveis de Risco):
• A soma total das "Pontuações de Risco" deve ser interpretada de acordo com as seguintes faixas:
    ◦ 0 – 7 pontos: Baixo risco 🟢
    ◦ 8 – 14 pontos: Atenção 🟡
    ◦ 15 – 21 pontos: Alto risco 🟠
    ◦ 22 – 28 pontos: Risco crítico 🔴
7. Devolutivas (Feedback ao Usuário):
• Com base no nível de risco identificado, o aplicativo deve apresentar uma devolutiva específica ao usuário:
    ◦ Baixo risco (0-7 pontos): "Empreendedora. Você demonstra equilíbrio entre vida pessoal e profissional, sabe delegar, e tem processos que sustentam o negócio com autonomia. Continue fortalecendo essas práticas e compartilhando sua experiência com outros empreendedores."
    ◦ Atenção (8-14 pontos): "Você está indo bem, mas há sinais que merecem atenção. Algumas armadilhas podem estar começando a impactar sua rotina ou decisões. Reflita sobre os pontos em que você se sente mais sobrecarregada ou onde há improviso. Pequenos ajustes agora podem evitar grandes problemas no futuro."
    ◦ Alto risco (15-21 pontos): "Seu perfil mostra vulnerabilidades importantes. É provável que você esteja enfrentando desafios como excesso de responsabilidade, dificuldade em delegar ou falta de tempo para planejamento. Isso pode comprometer tanto sua saúde quanto a sustentabilidade do negócio. É hora de repensar processos, buscar apoio e criar estratégias mais sólidas."
    ◦ Risco crítico (22-28 pontos): "O alerta está aceso. Seu negócio e sua jornada empreendedora estão em risco elevado. As armadilhas do eu empreendedor parecem estar dominando sua rotina, o que pode levar à exaustão, estagnação ou até à falência. É essencial buscar ajuda, rever profundamente sua forma de atuar e implementar mudanças urgentes. Você não precisa enfrentar isso sozinha."
8. Considerações Adicionais para o Aplicativo:
• O aplicativo pode ser desenvolvido para replicar a funcionalidade de uma planilha Excel ou Google Forms, conforme mencionado por Erika Rossi.
• A interface deve ser clara para a entrada de dados (Pontuação 0-3) e para a exibição dos resultados (Pontuação de Risco total e Devolutiva).
• Pode ser considerada a opção de integrar um relatório mais visual ou um plano de ação para cada armadilha, como sugerido nas devolutivas.
• O aplicativo deve garantir que a lógica de "pergunta direta" e "pergunta invertida" seja implementada corretamente para o cálculo da "Pontuação de Risco".
