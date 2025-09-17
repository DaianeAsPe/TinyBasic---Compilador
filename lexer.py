# lexer.py
# -----------------------------
# TinyBasic - Analisador Léxico
# Converte código-fonte em lista de tokens.
# -----------------------------

import re
from token import Token

# ============================================================
# Definição dos padrões de tokens (expressões regulares).
# A ordem importa: tokens mais longos (>=, <=, <>) devem vir
# antes dos curtos (> < =).
# ============================================================
token_specification = [
    ("NUMBER",   r'\d+'),        # números inteiros
    ("LET",      r'LET'),        # palavra-chave LET
    ("PRINT",    r'PRINT'),      # palavra-chave PRINT
    ("INPUT",    r'INPUT'),      # palavra-chave INPUT
    ("IF",       r'IF'),         # palavra-chave IF
    ("THEN",     r'THEN'),       # palavra-chave THEN
    ("GOTO",     r'GOTO'),       # palavra-chave GOTO
    ("GOSUB",    r'GOSUB'),      # palavra-chave GOSUB
    ("RETURN",   r'RETURN'),     # palavra-chave RETURN
    ("END",      r'END'),        # palavra-chave END
    ("REM",      r'REM.*'),      # comentário até o fim da linha
    ("ID",       r'[A-Z]'),      # variáveis (letra maiúscula)
    ("STR",      r'"[^"\n]*"'),  # strings entre aspas
    
    # Operadores relacionais
    ("GE", r'>='), ("LE", r'<='), ("NE", r'<>'),
    ("GT", r'>'), ("LT", r'<'), ("EQ", r'='),
    
    # Operadores aritméticos
    ("PLUS", r'\+'), ("MINUS", r'-'), ("MUL", r'\*'), ("DIV", r'/'),
    
    # Parênteses e pontuação
    ("LPAREN", r'\('), ("RPAREN", r'\)'), ("COMMA", r','), ("COLON", r':'),
    
    # Espaços e quebras de linha
    ("NEWLINE", r'\n'), ("SKIP", r'[ \t]+'),
    
    # Qualquer outro caractere inesperado
    ("MISMATCH", r'.'),
]

# Compila todas as regex em uma única expressão
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
get_token = re.compile(tok_regex).match

# ============================================================
# Função principal: analisador léxico
# Recebe código-fonte e devolve lista de tokens.
# ============================================================
def lexer(code, debug=False):
    pos = 0
    line_num = 1
    tokens = []
    mo = get_token(code, pos)

    while mo:
        kind = mo.lastgroup       # tipo do token
        value = mo.group(kind)    # valor capturado

        # =======================
        # Tratamento por categoria
        # =======================
        if kind == "NUMBER":
            tokens.append(Token(kind, int(value), line_num, mo.start()))
        
        elif kind in {"ID", "LET", "PRINT", "INPUT", "IF", "THEN", 
                      "GOTO", "GOSUB", "RETURN", "END"}:
            tokens.append(Token(kind, value, line_num, mo.start()))
        
        elif kind == "REM":
            tokens.append(Token("REM", value[3:].strip(), line_num, mo.start()))
        
        elif kind == "STR":
            tokens.append(Token(kind, value[1:-1], line_num, mo.start()))
        
        elif kind in {"GE", "LE", "NE", "GT", "LT", "EQ",
                      "PLUS", "MINUS", "MUL", "DIV",
                      "LPAREN", "RPAREN", "COMMA", "COLON"}:
            tokens.append(Token(kind, value, line_num, mo.start()))
        
        elif kind == "NEWLINE":
            tokens.append(Token(kind, value, line_num, mo.start()))
            line_num += 1
        
        elif kind == "SKIP":
            pass  # ignora espaços/tabs
        
        elif kind == "MISMATCH":
            # 🚨 Tratamento de erro detalhado
            error_col = mo.start() - code.rfind("\n", 0, mo.start())
            error_line = code.splitlines()[line_num - 1]
            raise RuntimeError(
                f"\nErro léxico na linha {line_num}, coluna {error_col}:\n"
                f"  {error_line}\n"
                f"  {' ' * (error_col-1)}^\n"
                f"Caractere inesperado: {value!r}"
            )

        # Avança para o próximo token
        pos = mo.end()
        mo = get_token(code, pos)

    # Adiciona token EOF no final
    tokens.append(Token("EOF", "$", line_num, pos))

    # Se debug=True, imprime tokens
    if debug:
        for t in tokens:
            print(t)

    return tokens
