# lexer.py
# -----------------------------
# Lexer do TinyBasic
# Converte o código fonte em uma lista de tokens.
# Cada token identifica uma unidade léxica (palavra-chave, número, operador, etc.)
# -----------------------------

import re
from token import Token

# -----------------------------
# Especificações de tokens
# Lista de tuplas: (NOME_DO_TOKEN, EXPRESSÃO_REGULAR)
# A ordem importa! Tokens de múltiplos caracteres (>=, <=, <>) devem vir antes dos de um caractere.
# -----------------------------
token_specification = [
    ("NUMBER",   r'\d+'),       # números inteiros
    ("LET",      r'LET'),       # palavra-chave LET
    ("PRINT",    r'PRINT'),     # palavra-chave PRINT
    ("INPUT",    r'INPUT'),     # palavra-chave INPUT
    ("IF",       r'IF'),        # palavra-chave IF
    ("THEN",     r'THEN'),      # palavra-chave THEN
    ("GOTO",     r'GOTO'),      # palavra-chave GOTO
    ("GOSUB",    r'GOSUB'),     # palavra-chave GOSUB
    ("RETURN",   r'RETURN'),    # palavra-chave RETURN
    ("END",      r'END'),       # palavra-chave END
    ("REM",      r'REM.*'),     # comentário até o final da linha
    ("ID",       r'[A-Z]'),     # variáveis (letras maiúsculas)
    ("STR",      r'"[^"\n]*"'), # strings entre aspas
    # Operadores relacionais (>=, <=, <> devem vir antes dos de 1 caractere)
    ("GE", r'>='), ("LE", r'<='), ("NE", r'<>'), 
    ("GT", r'>'), ("LT", r'<'), ("EQ", r'='),
    # Operadores aritméticos
    ("PLUS", r'\+'), ("MINUS", r'-'), ("MUL", r'\*'), ("DIV", r'/'),
    # Parênteses e pontuação
    ("LPAREN", r'\('), ("RPAREN", r'\)'), ("COMMA", r','), ("COLON", r':'),
    # Quebra de linha e espaços
    ("NEWLINE", r'\n'), ("SKIP", r'[ \t]+'),
    # Qualquer outro caractere inesperado
    ("MISMATCH", r'.'),
]

# Monta uma única expressão regular combinando todos os tokens
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
get_token = re.compile(tok_regex).match

# -----------------------------
# Função principal do lexer
# Recebe o código-fonte e retorna uma lista de tokens
# -----------------------------
def lexer(code):
    pos = 0
    line_num = 1
    tokens = []
    mo = get_token(code, pos)  # primeiro match
    while mo:
        kind = mo.lastgroup  # nome do token identificado
        value = mo.group(kind)  # valor encontrado
        if kind == "NUMBER":
            tokens.append(Token(kind, int(value), line_num, mo.start()))
        elif kind in {"ID", "LET", "PRINT", "INPUT", "IF", "THEN", "GOTO", "GOSUB", "RETURN", "END"}:
            tokens.append(Token(kind, value, line_num, mo.start()))
        elif kind == "REM":
            # Comentário: armazenamos só o texto sem "REM"
            tokens.append(Token("REM", value[3:].strip(), line_num, mo.start()))
        elif kind == "STR":
            # Removemos as aspas
            tokens.append(Token(kind, value[1:-1], line_num, mo.start()))
        elif kind in {"GE", "LE", "NE", "GT", "LT", "EQ", 
                      "PLUS", "MINUS", "MUL", "DIV", 
                      "LPAREN", "RPAREN", "COMMA", "COLON"}:
            tokens.append(Token(kind, value, line_num, mo.start()))
        elif kind == "NEWLINE":
            tokens.append(Token(kind, value, line_num, mo.start()))
            line_num += 1  # incrementa número da linha
        elif kind == "SKIP":
            pass  # ignora espaços e tabs
        elif kind == "MISMATCH":
            raise RuntimeError(f"Caractere inesperado {value!r} na linha {line_num}")
        pos = mo.end()
        mo = get_token(code, pos)
    # Adiciona token EOF no final para indicar fim do arquivo
    tokens.append(Token("EOF", "$", line_num, pos))
    return tokens
