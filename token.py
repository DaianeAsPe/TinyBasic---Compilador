# token.py
# -----------------------------
# Definição da classe Token
# Cada token representa uma unidade lexical do TinyBasic
# Cada token tem:
#   - type: tipo do token (ex: NUMBER, LET, PRINT, etc.)
#   - value: valor associado (ex: 123, "A", "+")
#   - line: linha no código fonte onde apareceu
#   - column: coluna no código fonte onde apareceu
# -----------------------------

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_       # Tipo do token
        self.value = value      # Valor do token
        self.line = line        # Linha do token
        self.column = column    # Coluna do token

    def __repr__(self):
        # Representação legível para debug
        return f"Token({self.type}, {self.value}, linha={self.line}, coluna={self.column})"
