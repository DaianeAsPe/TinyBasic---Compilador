# interpreter.py
# -----------------------------
# Interpreter do TinyBasic
# Executa a AST linha a linha
# -----------------------------

class Interpreter:
    def __init__(self, ast):
        self.ast = ast                # lista de linhas: ("LINE", numero, [statements])
        self.variables = {}           # dicionário para armazenar variáveis
        self.line_map = {}            # mapeia número da linha para índice da lista
        self.call_stack = []          # pilha para GOSUB/RETURN
        self.build_line_map()         # constrói mapa de linhas

    # ========================================================
    # Constrói mapa de linhas para facilitar GOTO e GOSUB
    # --------------------------------------------------------
    def build_line_map(self):
        for i, line in enumerate(self.ast):
            _, line_num, _ = line
            self.line_map[line_num] = i

    # ========================================================
    # Executa o programa completo
    # --------------------------------------------------------
    def run(self):
        i = 0
        while i < len(self.ast):
            #i = self.execute_line(i)  # retorna próximo índice da linha
            next_i = self.execute_line(i)
            if next_i == -1:  # encontrou END
                break
            i = next_i

    # ========================================================
    # Executa uma linha inteira
    # --------------------------------------------------------
    def execute_line(self, index):
        line = self.ast[index]
        _, line_num, stmt_list = line

        for stmt in stmt_list:
            result = self.execute_stmt(stmt, index)
            if isinstance(result, int):
                # Se o statement for GOTO/GOSUB/RETURN, muda índice da linha
                return result

        return index + 1  # próxima linha sequencial

    # ========================================================
    # Executa um statement individual
    # --------------------------------------------------------
    def execute_stmt(self, stmt, current_index):
        t = stmt[0]

        if t == "LET":
            _, var, expr = stmt
            self.variables[var] = self.eval_expr(expr)

        elif t == "PRINT":
            _, items = stmt
            output = []
            for item in items:
                if item[0] == "STR":
                    output.append(item[1])
                else:
                    output.append(str(self.eval_expr(item)))
            print(" ".join(output))

        elif t == "INPUT":
            _, var = stmt
            value = input(f"Digite {var}: ")
            self.variables[var] = int(value)

        elif t == "IF":
            _, cond, line_num = stmt
            if self.eval_cond(cond):
                if line_num in self.line_map:
                    return self.line_map[line_num]
                else:
                    raise Exception(f"Linha {line_num} não encontrada para IF")

        elif t == "GOTO":
            _, line_num = stmt
            if line_num in self.line_map:
                return self.line_map[line_num]
            else:
                raise Exception(f"Linha {line_num} não encontrada para GOTO")

        elif t == "GOSUB":
            _, line_num = stmt
            self.call_stack.append(current_index + 1)  # salva retorno
            if line_num in self.line_map:
                return self.line_map[line_num]
            else:
                raise Exception(f"Linha {line_num} não encontrada para GOSUB")

        elif t == "RETURN":
            if self.call_stack:
                return self.call_stack.pop()  # retorna ao ponto do GOSUB
            else:
                raise Exception("RETURN sem GOSUB correspondente")

        elif t == "END":
            print("Fim do programa.")
            return -1 #antes exit(0)

        elif t == "REM":
            pass  # ignora comentários

        else:
            raise Exception(f"Statement inesperado: {stmt}")

        return None  # continua na linha sequencial

    # ========================================================
    # Avalia expressões aritméticas
    # --------------------------------------------------------
    def eval_expr(self, expr):
        if expr[0] == "NUMBER":
            return expr[1]
        elif expr[0] == "ID":
            var = expr[1]
            return self.variables.get(var, 0)  # variáveis não inicializadas valem 0
        elif expr[0] == "BINOP":
            _, op, left, right = expr
            left_val = self.eval_expr(left)
            right_val = self.eval_expr(right)
            if op == "PLUS":
                return left_val + right_val
            elif op == "MINUS":
                return left_val - right_val
            elif op == "MUL":
                return left_val * right_val
            elif op == "DIV":
                if right_val == 0:
                    raise Exception("Divisão por zero")
                return left_val // right_val
        else:
            raise Exception(f"Expr inesperada: {expr}")

    # ========================================================
    # Avalia condições IF
    # --------------------------------------------------------
    def eval_cond(self, cond):
        _, left, op, right = cond
        left_val = self.eval_expr(left)
        right_val = self.eval_expr(right)
        if op == "EQ":
            return left_val == right_val
        elif op == "NE":
            return left_val != right_val
        elif op == "LT":
            return left_val < right_val
        elif op == "GT":
            return left_val > right_val
        elif op == "LE":
            return left_val <= right_val
        elif op == "GE":
            return left_val >= right_val
        else:
            raise Exception(f"Operador relacional inesperado: {op}")
