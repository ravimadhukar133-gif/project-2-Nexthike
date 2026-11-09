"""
Advanced GUI Calculator
Features: Standard, Scientific & Trigonometry, Unit Converter,
Graph Plotter, and Calculation History.

Requirements:
  - Python 3.10+
  - Tkinter (normally included with the official Windows Python installer)
  - matplotlib and numpy for graphing:
      python -m pip install matplotlib numpy

Run:
  python advanced_calculator.py
"""

import ast
import math
import operator
import tkinter as tk
from tkinter import ttk, messagebox


# --------------------------- Safe expression evaluator ---------------------------

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

FUNCTIONS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "log": math.log10, "ln": math.log, "abs": abs,
    "exp": math.exp, "factorial": math.factorial,
    "sind": lambda x: math.sin(math.radians(x)),
    "cosd": lambda x: math.cos(math.radians(x)),
    "tand": lambda x: math.tan(math.radians(x)),
    "asind": lambda x: math.degrees(math.asin(x)),
    "acosd": lambda x: math.degrees(math.acos(x)),
    "atand": lambda x: math.degrees(math.atan(x)),
}
CONSTANTS = {"pi": math.pi, "e": math.e}


def safe_eval(expression):
    """Evaluate a limited mathematical expression without using eval()."""
    expression = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError(f"Unknown name: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large")
            return BINARY_OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
            return UNARY_OPERATORS[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in FUNCTIONS or node.keywords or len(node.args) != 1:
                raise ValueError("Unsupported function")
            return FUNCTIONS[name](visit(node.args[0]))
        raise ValueError("Invalid or unsupported expression")

    result = visit(tree)
    if isinstance(result, complex) or not math.isfinite(float(result)):
        raise ValueError("Result is outside the supported range")
    return result


# --------------------------- Main application ---------------------------

class AdvancedCalculator:
    BG = "#171923"
    PANEL = "#222638"
    ENTRY = "#111522"
    TEXT = "#f4f5f7"
    ACCENT = "#5b8def"
    BUTTON = "#30384f"
    OPERATOR = "#46577d"

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Scientific Calculator")
        self.root.geometry("280x350")
        self.root.minsize(850, 620)
        self.root.configure(bg=self.BG)

        self.history = []
        self.angle_mode = tk.StringVar(value="Degrees")
        self.expression = tk.StringVar()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.BG, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab", background=self.PANEL, foreground=self.TEXT,
            padding=(16, 10), font=("Segoe UI", 10, "bold")
        )
        self.style.map("TNotebook.Tab", background=[("selected", self.ACCENT)])

        header = tk.Frame(root, bg=self.BG)
        header.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(
            header, text="ADVANCED CALCULATOR", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 19, "bold")
        ).pack(side="left")
        tk.Label(
            header, text="Python • Tkinter", bg=self.BG, fg="#aab3ca",
            font=("Segoe UI", 10)
        ).pack(side="right", pady=8)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        self.standard_tab = tk.Frame(self.notebook, bg=self.BG)
        self.scientific_tab = tk.Frame(self.notebook, bg=self.BG)
        self.converter_tab = tk.Frame(self.notebook, bg=self.BG)
        self.graph_tab = tk.Frame(self.notebook, bg=self.BG)
        self.history_tab = tk.Frame(self.notebook, bg=self.BG)

        self.notebook.add(self.standard_tab, text="Standard")
        self.notebook.add(self.scientific_tab, text="Scientific & Trig")
        self.notebook.add(self.converter_tab, text="Converter")
        self.notebook.add(self.graph_tab, text="Graph")
        self.notebook.add(self.history_tab, text="History")

        self.build_standard()
        self.build_scientific()
        self.build_converter()
        self.build_graph()
        self.build_history()

        self.root.bind("<Return>", lambda event: self.calculate_standard())
        self.root.bind("<Escape>", lambda event: self.clear_standard())

    # --------------------------- Shared UI helpers ---------------------------

    def make_display(self, parent, variable=None):
        entry = tk.Entry(
            parent, textvariable=variable, font=("Segoe UI", 25),
            bg=self.ENTRY, fg=self.TEXT, insertbackground=self.TEXT,
            justify="right", relief="flat", bd=0
        )
        entry.pack(fill="x", padx=12, pady=12, ipady=16)
        return entry

    def make_button(self, parent, text, command, row, col, *,
                    colspan=1, color=None, font_size=13):
        button = tk.Button(
            parent, text=text, command=command,
            bg=color or self.BUTTON, fg=self.TEXT,
            activebackground=self.ACCENT, activeforeground="white",
            relief="flat", bd=0, font=("Segoe UI", font_size, "bold"),
            cursor="hand2"
        )
        button.grid(row=row, column=col, columnspan=colspan,
                    sticky="nsew", padx=4, pady=4, ipady=11)
        return button

    def add_history(self, expression, result):
        self.history.append((expression, str(result)))
        self.refresh_history()

    # --------------------------- Standard calculator ---------------------------

    def build_standard(self):
        self.standard_display = tk.StringVar()
        self.make_display(self.standard_tab, self.standard_display)

        keypad = tk.Frame(self.standard_tab, bg=self.BG)
        keypad.pack(fill="both", expand=True, padx=8, pady=4)

        keys = [
            ["C", "DEL", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "(", ")"],
            ["π", "e", "^", "="],
        ]
        for r in range(len(keys)):
            keypad.rowconfigure(r, weight=1)
            for c in range(4):
                keypad.columnconfigure(c, weight=1)
                key = keys[r][c]
                if key == "C":
                    command = self.clear_standard
                elif key == "DEL":
                    command = self.delete_standard
                elif key == "=":
                    command = self.calculate_standard
                else:
                    command = lambda value=key: self.press_standard(value)
                color = self.ACCENT if key == "=" else (
                    self.OPERATOR if key in {"÷", "×", "-", "+", "^"} else self.BUTTON
                )
                self.make_button(keypad, key, command, r, c, color=color)

    def press_standard(self, value):
        replacements = {"π": "pi", "×": "*", "÷": "/", "^": "**"}
        self.standard_display.set(
            self.standard_display.get() + replacements.get(value, value)
        )

    def clear_standard(self):
        self.standard_display.set("")

    def delete_standard(self):
        self.standard_display.set(self.standard_display.get()[:-1])

    def calculate_standard(self):
        expression = self.standard_display.get().strip()
        if not expression:
            return
        try:
            result = safe_eval(expression)
            shown = f"{result:.12g}" if isinstance(result, float) else str(result)
            self.standard_display.set(shown)
            self.add_history(expression, shown)
        except Exception as error:
            messagebox.showerror("Calculation Error", str(error))

    # --------------------------- Scientific and trigonometry ---------------------------

    def build_scientific(self):
        self.scientific_display = tk.StringVar()
        self.make_display(self.scientific_tab, self.scientific_display)

        mode_row = tk.Frame(self.scientific_tab, bg=self.BG)
        mode_row.pack(fill="x", padx=12)
        tk.Label(mode_row, text="Angle mode:", bg=self.BG, fg=self.TEXT).pack(side="left")
        ttk.Combobox(
            mode_row, textvariable=self.angle_mode,
            values=["Degrees", "Radians"], state="readonly", width=12
        ).pack(side="left", padx=8)

        grid = tk.Frame(self.scientific_tab, bg=self.BG)
        grid.pack(fill="both", expand=True, padx=8, pady=8)
        keys = [
            ["sin", "cos", "tan", "asin", "acos"],
            ["atan", "sqrt", "log", "ln", "factorial"],
            ["x²", "x³", "π", "e", "^"],
            ["7", "8", "9", "÷", "C"],
            ["4", "5", "6", "×", "DEL"],
            ["1", "2", "3", "-", "("],
            ["0", ".", "=", "+", ")"],
        ]
        for r, row in enumerate(keys):
            grid.rowconfigure(r, weight=1)
            for c, key in enumerate(row):
                grid.columnconfigure(c, weight=1)
                self.make_button(
                    grid, key, lambda value=key: self.press_scientific(value),
                    r, c, color=self.ACCENT if key == "=" else self.BUTTON,
                    font_size=11
                )

    def press_scientific(self, key):
        current = self.scientific_display.get()
        if key == "C":
            self.scientific_display.set("")
            return
        if key == "DEL":
            self.scientific_display.set(current[:-1])
            return
        if key == "=":
            self.calculate_scientific()
            return
        if key in {"sin", "cos", "tan", "asin", "acos", "atan",
                   "sqrt", "log", "ln", "factorial"}:
            addition = key + "("
        elif key == "x²":
            addition = "**2"
        elif key == "x³":
            addition = "**3"
        elif key == "π":
            addition = "pi"
        elif key == "÷":
            addition = "/"
        elif key == "×":
            addition = "*"
        else:
            addition = key
        self.scientific_display.set(current + addition)

    def calculate_scientific(self):
        expression = self.scientific_display.get().strip()
        if not expression:
            return
        try:
            # Convert trig input to radians when Degrees mode is selected.
            # Inverse trig results are converted back to degrees.
            expression_for_eval = expression
            if self.angle_mode.get() == "Degrees":
                # Use degree-aware function names; this avoids changing parentheses.
                for fn in ("asin", "acos", "atan", "sin", "cos", "tan"):
                    expression_for_eval = expression_for_eval.replace(
                        fn + "(", fn + "d("
                    )
            result = safe_eval(expression_for_eval)
            shown = f"{result:.12g}" if isinstance(result, float) else str(result)
            self.scientific_display.set(shown)
            self.add_history(expression, shown)
        except Exception as error:
            messagebox.showerror("Scientific Calculation Error", str(error))

    # --------------------------- Unit converter ---------------------------

    def build_converter(self):
        panel = tk.Frame(self.converter_tab, bg=self.PANEL)
        panel.pack(fill="x", padx=20, pady=20)

        self.category = tk.StringVar(value="Length")
        self.convert_value = tk.StringVar(value="1")
        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.convert_result = tk.StringVar(value="Result will appear here")

        tk.Label(panel, text="Conversion category", bg=self.PANEL, fg=self.TEXT).grid(
            row=0, column=0, sticky="w", padx=12, pady=10
        )
        category_box = ttk.Combobox(
            panel, textvariable=self.category,
            values=["Length", "Weight", "Temperature", "Time"],
            state="readonly", width=22
        )
        category_box.grid(row=0, column=1, padx=12, pady=10)
        category_box.bind("<<ComboboxSelected>>", self.update_unit_choices)

        tk.Label(panel, text="Value", bg=self.PANEL, fg=self.TEXT).grid(
            row=1, column=0, sticky="w", padx=12, pady=10
        )
        tk.Entry(panel, textvariable=self.convert_value, width=25).grid(
            row=1, column=1, padx=12, pady=10, ipady=5
        )

        tk.Label(panel, text="From", bg=self.PANEL, fg=self.TEXT).grid(
            row=2, column=0, sticky="w", padx=12, pady=10
        )
        self.from_box = ttk.Combobox(panel, textvariable=self.from_unit, state="readonly", width=22)
        self.from_box.grid(row=2, column=1, padx=12, pady=10)

        tk.Label(panel, text="To", bg=self.PANEL, fg=self.TEXT).grid(
            row=3, column=0, sticky="w", padx=12, pady=10
        )
        self.to_box = ttk.Combobox(panel, textvariable=self.to_unit, state="readonly", width=22)
        self.to_box.grid(row=3, column=1, padx=12, pady=10)

        tk.Button(
            panel, text="Convert", command=self.convert_units,
            bg=self.ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 12, "bold"), padx=25, pady=10
        ).grid(row=4, column=0, columnspan=2, pady=18)

        tk.Label(
            self.converter_tab, textvariable=self.convert_result,
            bg=self.BG, fg="#83b7ff", font=("Segoe UI", 18, "bold")
        ).pack(pady=18)

        self.units = {
            "Length": {"m": 1, "km": 1000, "cm": .01, "mm": .001, "mile": 1609.344, "foot": .3048},
            "Weight": {"kg": 1, "g": .001, "mg": .000001, "pound": .45359237, "ounce": .028349523125},
            "Time": {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400},
            "Temperature": {"Celsius": 1, "Fahrenheit": 1, "Kelvin": 1},
        }
        self.update_unit_choices()

    def update_unit_choices(self, event=None):
        choices = list(self.units[self.category.get()].keys())
        self.from_box["values"] = choices
        self.to_box["values"] = choices
        self.from_unit.set(choices[0])
        self.to_unit.set(choices[1] if len(choices) > 1 else choices[0])

    def convert_units(self):
        try:
            value = float(self.convert_value.get())
            category = self.category.get()
            source, target = self.from_unit.get(), self.to_unit.get()

            if category == "Temperature":
                if source == "Celsius":
                    celsius = value
                elif source == "Fahrenheit":
                    celsius = (value - 32) * 5 / 9
                else:
                    celsius = value - 273.15

                if target == "Celsius":
                    result = celsius
                elif target == "Fahrenheit":
                    result = celsius * 9 / 5 + 32
                else:
                    result = celsius + 273.15
            else:
                base_value = value * self.units[category][source]
                result = base_value / self.units[category][target]

            output = f"{result:.10g} {target}"
            self.convert_result.set(output)
            self.add_history(f"{value} {source} → {target}", output)
        except Exception as error:
            messagebox.showerror("Conversion Error", str(error))

    # --------------------------- Graph plotter ---------------------------

    def build_graph(self):
        info = tk.Label(
            self.graph_tab,
            text="Enter a function of x, for example: x**2, sin(x), cos(x), x**3",
            bg=self.BG, fg=self.TEXT, font=("Segoe UI", 11)
        )
        info.pack(anchor="w", padx=16, pady=(14, 6))

        controls = tk.Frame(self.graph_tab, bg=self.BG)
        controls.pack(fill="x", padx=16)
        self.graph_expression = tk.StringVar(value="x**2")
        self.x_min = tk.StringVar(value="-10")
        self.x_max = tk.StringVar(value="10")

        for label, variable, width in [
            ("y =", self.graph_expression, 24),
            ("X min", self.x_min, 7),
            ("X max", self.x_max, 7),
        ]:
            tk.Label(controls, text=label, bg=self.BG, fg=self.TEXT).pack(side="left", padx=(5, 3))
            tk.Entry(controls, textvariable=variable, width=width).pack(side="left", padx=4, ipady=5)

        tk.Button(
            controls, text="Plot Graph", command=self.plot_graph,
            bg=self.ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=14, pady=7
        ).pack(side="left", padx=8)

        self.graph_area = tk.Frame(self.graph_tab, bg="white")
        self.graph_area.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(
            self.graph_area,
            text="Your graph will appear here.\nInstall matplotlib and numpy to enable graphing.",
            bg="white", fg="#333333", font=("Segoe UI", 12)
        ).pack(expand=True)

    def plot_graph(self):
        try:
            import importlib
            np = importlib.import_module("numpy")
            Figure = importlib.import_module("matplotlib.figure").Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showerror(
                "Missing packages",
                "Graphing needs matplotlib and numpy.\n\n"
                "Open the VS Code terminal and run:\n"
                "python -m pip install matplotlib numpy"
            )
            return

        expression = self.graph_expression.get().strip().replace("^", "**")
        low, high = float(self.x_min.get()), float(self.x_max.get())
        if low >= high:
            messagebox.showerror("Graph Error", "X min must be smaller than X max.")
            return

        allowed = {
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "sqrt": np.sqrt, "log": np.log10, "ln": np.log,
            "exp": np.exp, "abs": np.abs, "pi": np.pi, "e": np.e,
        }
        try:
            tree = ast.parse(expression, mode="eval")

            def evaluate_node(node, x_values):
                if isinstance(node, ast.Expression):
                    return evaluate_node(node.body, x_values)
                if isinstance(node, ast.Name):
                    if node.id == "x":
                        return x_values
                    if node.id in allowed:
                        return allowed[node.id]
                    raise ValueError(f"Unknown name: {node.id}")
                if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                    return node.value
                if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
                    return BINARY_OPERATORS[type(node.op)](
                        evaluate_node(node.left, x_values),
                        evaluate_node(node.right, x_values)
                    )
                if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
                    return UNARY_OPERATORS[type(node.op)](evaluate_node(node.operand, x_values))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    fn = evaluate_node(node.func, x_values)
                    if node.keywords or len(node.args) != 1 or not callable(fn):
                        raise ValueError("Unsupported graph function")
                    return fn(evaluate_node(node.args[0], x_values))
                raise ValueError("Unsupported graph expression")

            x_values = np.linspace(low, high, 800)
            y_values = evaluate_node(tree, x_values)
            if np.isscalar(y_values):
                y_values = np.full_like(x_values, y_values)
            y_values = np.asarray(y_values, dtype=float)
            y_values = np.where(np.isfinite(y_values), y_values, np.nan)

            for child in self.graph_area.winfo_children():
                child.destroy()

            figure = Figure(figsize=(7, 4.2), dpi=100)
            axis = figure.add_subplot(111)
            axis.plot(x_values, y_values, label=f"y = {expression}")
            axis.axhline(0, linewidth=0.8)
            axis.axvline(0, linewidth=0.8)
            axis.set_xlabel("X")
            axis.set_ylabel("Y")
            axis.set_title(f"Graph of y = {expression}")
            axis.grid(True)
            axis.legend()
            figure.tight_layout()

            canvas = FigureCanvasTkAgg(figure, master=self.graph_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as error:
            messagebox.showerror("Graph Error", str(error))

    # --------------------------- History ---------------------------

    def build_history(self):
        heading = tk.Label(
            self.history_tab, text="Calculation History",
            bg=self.BG, fg=self.TEXT, font=("Segoe UI", 17, "bold")
        )
        heading.pack(anchor="w", padx=16, pady=14)

        body = tk.Frame(self.history_tab, bg=self.BG)
        body.pack(fill="both", expand=True, padx=16, pady=4)

        self.history_list = tk.Listbox(
            body, bg=self.ENTRY, fg=self.TEXT, selectbackground=self.ACCENT,
            font=("Consolas", 12), relief="flat", activestyle="none"
        )
        self.history_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.history_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_list.configure(yscrollcommand=scrollbar.set)

        buttons = tk.Frame(self.history_tab, bg=self.BG)
        buttons.pack(fill="x", padx=16, pady=12)
        tk.Button(
            buttons, text="Use Selected Result", command=self.use_history_result,
            bg=self.ACCENT, fg="white", relief="flat", padx=12, pady=8
        ).pack(side="left", padx=4)
        tk.Button(
            buttons, text="Clear History", command=self.clear_history,
            bg=self.OPERATOR, fg="white", relief="flat", padx=12, pady=8
        ).pack(side="left", padx=4)

    def refresh_history(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.delete(0, tk.END)
        for expression, result in reversed(self.history):
            self.history_list.insert(tk.END, f"{expression}  =  {result}")

    def use_history_result(self):
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showinfo("History", "Select a calculation first.")
            return
        index = len(self.history) - 1 - selection[0]
        result = self.history[index][1]
        self.standard_display.set(result)
        self.notebook.select(self.standard_tab)

    def clear_history(self):
        self.history.clear()
        self.refresh_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedCalculator(root)
    root.mainloop()