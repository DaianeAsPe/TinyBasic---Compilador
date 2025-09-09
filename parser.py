# parser.py
# -----------------------------
# Parser do TinyBasic
# Constrói a AST (Abstract Syntax Tree) a partir da lista de tokens
# Cada linha do programa vira um nó na árvore
# -----------------------------

from token import Token

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens       # lista de tokens vinda do lexer
        self.pos = 0               # posição atual na lista
        self.current_token = self.tokens[self.pos]  # token atual

    # -----------------------------
    # Avança para o próximo token
    # -----------------------------
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            # Se acabou, cria token EOF
            self.current_token = Token("EOF", "$", -1, -1)

    # ========================================================
    # Função principal: parse_program
    # Retorna uma lista de linhas, cada linha com seus statements
    # --------------------------------------------------------
    def parse_program(self):
        lines = []
        while self.current_token.type != "EOF":
            # Ignora comentários que possam estar isolados
            while self.current_token.type in ("REM", "REM_TEXT"):
                self.advance()
            if self.current_token.type == "EOF":
                break
            lines.append(self.parse_line())
        return lines

    # ========================================================
    # Parse de uma linha:
    # Formato: NUMERO statements NEWLINE
    # --------------------------------------------------------
    def parse_line(self):
        num = self.current_token
        if num.type != "NUMBER":
            raise Exception(f"Era esperado número de linha, encontrado {num.type} na linha {num.line}")
        self.advance()

        stmt_list = self.parse_stmt_list()  # lista de statements separados por ":"

        if self.current_token.type == "NEWLINE":
            self.advance()
        elif self.current_token.type == "EOF":
            pass  # final do arquivo
        else:
            raise Exception(f"Esperado NEWLINE após a linha, encontrado {self.current_token.type} na linha {num.line}")

        # Retorna a linha como tupla: ("LINE", numero_da_linha, [statements])
        return ("LINE", num.value, stmt_list)

    # ========================================================
    # Lista de statements (separados por ":")
    # --------------------------------------------------------
    def parse_stmt_list(self):
        stmts = [self.parse_stmt()]
        while self.current_token.type == "COLON":
            self.advance()
            stmts.append(self.parse_stmt())
        return stmts

    # ========================================================
    # Parse de um statement individual
    # --------------------------------------------------------
    def parse_stmt(self):
        t = self.current_token.type

        if t == "LET":
            return self.parse_let()
        elif t == "PRINT":
            return self.parse_print()
        elif t == "INPUT":
            return self.parse_input()
        elif t == "IF":
            return self.parse_if()
        elif t == "GOTO":
            return self.parse_goto()
        elif t == "GOSUB":
            return self.parse_gosub()
        elif t == "RETURN":
            self.advance()
            return ("RETURN",)
        elif t == "END":
            self.advance()
            return ("END",)
        elif t == "REM":
            self.advance()
            return ("REM",)
        else:
            raise Exception(f"Comando inesperado {t} na linha {self.current_token.line}")

    # ========================================================
    # Parse do LET statement
    # Formato: LET ID = EXPR
    # --------------------------------------------------------
    def parse_let(self):
        self.advance()  # consome LET
        var_token = self.current_token
        if var_token.type != "ID":
            raise Exception(f"Era esperado ID após LET, encontrado {var_token.type} na linha {var_token.line}")
        self.advance()

        if self.current_token.type != "EQ":
            raise Exception(f"Era esperado '=' após ID, encontrado {self.current_token.type} na linha {var_token.line}")
        self.advance()

        expr = self.parse_expr()
        return ("LET", var_token.value, expr)

    # ========================================================
    # Parse do PRINT statement
    # Formato: PRINT item [, item ...]
    # --------------------------------------------------------
    def parse_print(self):
        self.advance()  # consome PRINT
        items = [self.parse_print_item()]
        while self.current_token.type == "COMMA":
            self.advance()
            items.append(self.parse_print_item())
        return ("PRINT", items)

    def parse_print_item(self):
        t = self.current_token.type
        if t == "STR":
            value = self.current_token.value
            self.advance()
            return ("STR", value)
        elif t in ("NUMBER", "ID", "LPAREN"):
            return self.parse_expr()
        else:
            raise Exception(f"PRINT token inesperado {t} na linha {self.current_token.line}")

    # ========================================================
    # Parse do INPUT statement
    # Formato: INPUT ID
    # --------------------------------------------------------
    def parse_input(self):
        self.advance()  # consome INPUT
        var_token = self.current_token
        if var_token.type != "ID":
            raise Exception(f"Esperado ID após INPUT, encontrado {var_token.type} na linha {var_token.line}")
        self.advance()
        return ("INPUT", var_token.value)

    # ========================================================
    # Parse do IF statement
    # Formato: IF COND THEN NUM
    # --------------------------------------------------------
    def parse_if(self):
        self.advance()  # consome IF
        cond = self.parse_cond()
        if self.current_token.type != "THEN":
            raise Exception(f"Esperado THEN após condição, encontrado {self.current_token.type} na linha {self.current_token.line}")
        self.advance()
        num_token = self.current_token
        if num_token.type != "NUMBER":
            raise Exception(f"Esperado número de linha após THEN, encontrado {num_token.type} na linha {num_token.line}")
        self.advance()
        return ("IF", cond, num_token.value)

    # Parse de condição (expressão relacional)
    def parse_cond(self):
        left = self.parse_expr()
        op = self.current_token.type
        if op not in ("EQ", "NE", "LT", "GT", "LE", "GE"):
            raise Exception(f"Operador relacional esperado, encontrado {op} na linha {self.current_token.line}")
        self.advance()
        right = self.parse_expr()
        return ("COND", left, op, right)

    # ========================================================
    # Parse do GOTO statement
    # Formato: GOTO NUM
    # --------------------------------------------------------
    def parse_goto(self):
        self.advance()
        num_token = self.current_token
        if num_token.type != "NUMBER":
            raise Exception(f"Esperado número de linha após GOTO, encontrado {num_token.type} na linha {num_token.line}")
        self.advance()
        return ("GOTO", num_token.value)

    # ========================================================
    # Parse do GOSUB statement
    # Formato: GOSUB NUM
    # --------------------------------------------------------
    def parse_gosub(self):
        self.advance()
        num_token = self.current_token
        if num_token.type != "NUMBER":
            raise Exception(f"Esperado número de linha após GOSUB, encontrado {num_token.type} na linha {num_token.line}")
        self.advance()
        return ("GOSUB", num_token.value)

    # ========================================================
    # EXPRESSÕES (Expr, Term, Factor)
    # Implementa precedência de operadores (+,- antes de *,/)
    # --------------------------------------------------------
    def parse_expr(self):
        node = self.parse_term()
        while self.current_token.type in ("PLUS", "MINUS"):
            op = self.current_token.type
            self.advance()
            right = self.parse_term()
            node = ("BINOP", op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token.type in ("MUL", "DIV"):
            op = self.current_token.type
            self.advance()
            right = self.parse_factor()
            node = ("BINOP", op, node, right)
        return node

    def parse_factor(self):
        t = self.current_token.type
        if t == "NUMBER":
            value = self.current_token.value
            self.advance()
            return ("NUMBER", value)
        elif t == "ID":
            name = self.current_token.value
            self.advance()
            return ("ID", name)
        elif t == "LPAREN":
            self.advance()
            node = self.parse_expr()
            if self.current_token.type != "RPAREN":
                raise Exception(f"Esperado ')' na linha {self.current_token.line}")
            self.advance()
            return node
        else:
            raise Exception(f"Factor inesperado {t} na linha {self.current_token.line}")
