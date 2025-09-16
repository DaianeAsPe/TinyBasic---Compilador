# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from lexer import lexer
from parser import Parser
from interpreter import Interpreter

class TinyBasicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyBasic - Compilador Visual")
        self.root.geometry("900x600")

        # Botões principais
        frame_top = tk.Frame(root)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(frame_top, text="Abrir Programa", command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_top, text="Rodar", command=self.run_program).pack(side=tk.LEFT, padx=5)

        # Áreas de texto
        self.code_area = self.create_text_area("Código Fonte")
        self.tokens_area = self.create_text_area("Tokens")
        self.ast_area = self.create_text_area("AST")
        self.output_area = self.create_text_area("Saída do Programa")

        self.program_code = ""

    def create_text_area(self, label):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(frame, text=label).pack()
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=15)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.program_code = f.read()
            self.code_area.delete("1.0", tk.END)
            self.code_area.insert(tk.END, self.program_code)

    def run_program(self):
        if not self.program_code:
            self.program_code = self.code_area.get("1.0", tk.END).strip()
        if not self.program_code:
            messagebox.showerror("Erro", "Nenhum código carregado.")
            return

        try:
            # Lexer
            tokens = lexer(self.program_code)
            self.tokens_area.delete("1.0", tk.END)
            for t in tokens:
                self.tokens_area.insert(tk.END, str(t) + "\n")

            # Parser
            parser = Parser(tokens)
            ast = parser.parse_program()
            self.ast_area.delete("1.0", tk.END)
            for line in ast:
                self.ast_area.insert(tk.END, str(line) + "\n")

            # Interpreter com captura da saída
            self.output_area.delete("1.0", tk.END)
            output_lines = []
            interpreter = Interpreter(ast)

            import builtins
            old_print = builtins.print
            old_input = builtins.input

            # Captura print
            builtins.print = lambda *args, **kwargs: output_lines.append(" ".join(map(str, args)))

            # Captura input → abre caixinha no Tkinter
            def gui_input(prompt=""):
                self.output_area.insert(tk.END, prompt + "\n")
                self.output_area.see(tk.END)
                value = simpledialog.askstring("Entrada de Dados", prompt, parent=self.root)
                if value is None:
                    return ""  # usuário cancelou
                value = value.strip()
                # tenta converter para número
                try:
                    if "." in value:
                        return float(value)
                    return int(value)
                except ValueError:
                    return value  # mantém string se não for número

            builtins.input = gui_input

            interpreter.run()

            # Restaura funções originais
            builtins.print = old_print
            builtins.input = old_input

            # Mostra saída
            for line in output_lines:
                self.output_area.insert(tk.END, line + "\n")

        except Exception as e:
            messagebox.showerror("Erro de Execução", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = TinyBasicGUI(root)
    root.mainloop()
