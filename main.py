# main.py
# -----------------------------
# TinyBasic - Programa principal
# Integra lexer, parser e interpreter
# -----------------------------

from lexer import lexer
from parser import Parser
from interpreter import Interpreter
from token import Token  # nosso Token.py, não o módulo interno do Python

# -----------------------------
# Lê o código TinyBasic de um arquivo
# -----------------------------
with open("program.txt", "r", encoding="utf-8") as f:
    code = f.read()


# -----------------------------
# Passo 1: Lexer
# Transforma o código em uma lista de tokens
# -----------------------------
tokens = lexer(code)
print("Tokens gerados pelo Lexer:")
for t in tokens:
    print(t)
print("-" * 40)

# -----------------------------
# Passo 2: Parser
# Constrói a AST a partir da lista de tokens
# -----------------------------
parser = Parser(tokens)
ast = parser.parse_program()
print("AST gerada pelo Parser:")
for line in ast:
    print(line)
print("-" * 40)

# -----------------------------
# Passo 3: Interpreter
# Executa a AST linha a linha
# -----------------------------
interpreter = Interpreter(ast)
interpreter.run()
